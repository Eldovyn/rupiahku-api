import time
from fastapi import HTTPException
from web3 import Web3
from stellar_sdk import Keypair, TransactionBuilder, scval, SorobanServer
from stellar_sdk.soroban_rpc import GetTransactionStatus
from stellar_sdk.exceptions import Ed25519PublicKeyInvalidError
from stellar_sdk import Server as HorizonServer

import json
import os

from configs.env import Config
from schemas.faucet_schema import MintRequest

abi_path = os.path.join(os.path.dirname(__file__), '..', 'abi', 'RupiahKU.json')
with open(abi_path, 'r') as f:
    ERC20_MINT_ABI = json.load(f)

class FaucetController:
    def __init__(self):
        self.admin_keypair = Keypair.from_secret(Config.ADMIN_STELLAR)
        self.soroban_server = SorobanServer(Config.RPC_URL)
        self.horizon_server = HorizonServer(Config.HORIZON_URL)
        
        try:
            self.w3 = Web3(Web3.HTTPProvider(Config.SEPOLIA_RPC_URL))
            self.sepolia_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(Config.SEPOLIA_CONTRACT_ADDRESS), abi=ERC20_MINT_ABI)
            self.sepolia_account = self.w3.eth.account.from_key(Config.SEPOLIA_PRIVATE_KEY)
            self.sepolia_error = None
        except Exception as e:
            self.w3 = None
            self.sepolia_account = None
            self.sepolia_contract = None
            self.sepolia_error = str(e)

    def mint_token(self, req: MintRequest):
        if req.network == "sepolia":
            return self._mint_sepolia(req)
        return self._mint_stellar(req)

    def _mint_sepolia(self, req: MintRequest):
        if self.sepolia_account is None:
            raise HTTPException(status_code=500, detail={"error": f"Sepolia misconfigured: {self.sepolia_error}"})
        
        if req.amount <= 0:
            raise HTTPException(status_code=400, detail={"amount": "IS_INVALID"})
            
        if not self.w3.is_address(req.wallet_address):
            raise HTTPException(status_code=400, detail={"wallet_address": "IS_INVALID"})
            
        try:
            to_address = self.w3.to_checksum_address(req.wallet_address)
            amount_wei = int(req.amount * (10**18))
            
            nonce = self.w3.eth.get_transaction_count(self.sepolia_account.address)
            
            tx = self.sepolia_contract.functions.mint(to_address, amount_wei).build_transaction({
                'chainId': 11155111,
                'nonce': nonce,
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=Config.SEPOLIA_PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {
                "message": "Permintaan berhasil diproses",
                "data": {
                    "tx_hash": self.w3.to_hex(tx_hash),
                    "minted_amount": req.amount,
                    "wallet_address": req.wallet_address,
                    "network": "sepolia"
                },
                "errors": None
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to mint on Sepolia: {str(e)}")

    def _mint_stellar(self, req: MintRequest):
        try:
            # Validate address format
            try:
                Keypair.from_public_key(req.wallet_address)
            except Ed25519PublicKeyInvalidError:
                raise HTTPException(status_code=400, detail={"wallet_address": "IS_INVALID"})

            if req.amount <= 0:
                raise HTTPException(status_code=400, detail={"amount": "IS_INVALID"})

            # Load account sequence from Horizon
            try:
                account = self.horizon_server.load_account(self.admin_keypair.public_key)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load admin account from Horizon: {e}")

            # Build transaction
            tx_builder = TransactionBuilder(
                source_account=account,
                network_passphrase=Config.NETWORK_PASSPHRASE,
                base_fee=10000
            )
            
            admin_address_val = scval.to_address(self.admin_keypair.public_key)
            to_address_val = scval.to_address(req.wallet_address)
            contract_amount = req.amount * (10**7)
            amount_val = scval.to_int128(contract_amount)
            
            tx_builder.append_invoke_contract_function_op(
                contract_id=Config.CONTRACT_ID,
                function_name="mint",
                parameters=[admin_address_val, to_address_val, amount_val]
            )
            
            tx = tx_builder.build()
            
            # Simulate transaction
            sim_resp = self.soroban_server.simulate_transaction(tx)
            
            if hasattr(sim_resp, "error") and sim_resp.error:
                raise HTTPException(status_code=500, detail=f"Simulation failed: {sim_resp.error}")
                
            # Prepare transaction
            tx = self.soroban_server.prepare_transaction(tx)
            tx.sign(self.admin_keypair)
            
            # Submit transaction
            send_resp = self.soroban_server.send_transaction(tx)
            
            if send_resp.error_result_xdr:
                 raise HTTPException(status_code=500, detail=f"Transaction submission failed: {send_resp.error_result_xdr}")
                 
            # Wait for confirmation
            tx_hash = send_resp.hash
            for _ in range(15):
                time.sleep(2)
                status_resp = self.soroban_server.get_transaction(tx_hash)
                if status_resp.status == GetTransactionStatus.SUCCESS:
                    return {
                        "message": "Permintaan berhasil diproses",
                        "data": {
                            "tx_hash": tx_hash,
                            "minted_amount": req.amount,
                            "wallet_address": req.wallet_address
                        },
                        "errors": None
                    }
                elif status_resp.status == GetTransactionStatus.FAILED:
                    raise HTTPException(status_code=500, detail=f"Transaction failed on network: {status_resp.result_xdr}")
                    
            return {
                "message": "Transaksi berhasil dikirim tapi butuh waktu konfirmasi lebih lama",
                "data": {
                    "tx_hash": tx_hash,
                    "status": "pending"
                },
                "errors": None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
