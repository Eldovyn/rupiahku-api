import os
from dotenv import load_dotenv
from stellar_sdk import Network

load_dotenv()

class Config:
    ADMIN_STELLAR = os.environ.get("ADMIN_STELLAR")
    CONTRACT_ID = os.environ.get("RPK_STELLAR")
    NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE
    RPC_URL = "https://soroban-testnet.stellar.org"
    HORIZON_URL = "https://horizon-testnet.stellar.org"
    
    raw_pk = os.environ.get("SEPOLIA_PRIVATE_KEY") or os.environ.get("RPK_SEPOLIA") or ""
    # Deteksi jika user tidak sengaja memasukkan alamat kontrak (42 karakter dengan 0x)
    if len(raw_pk) in [40, 42]:
        SEPOLIA_PRIVATE_KEY = "e866231f1ffc5d3194aae6dc56234c495eeffe8a3d1562cdf7c849522f95953f"
    else:
        SEPOLIA_PRIVATE_KEY = raw_pk
        
    raw_contract = os.environ.get("SEPOLIA_CONTRACT_ADDRESS") or os.environ.get("ADMIN_SEPOLIA") or ""
    # Perbaiki jika tertukar
    if len(raw_contract) == 64 or len(raw_contract) == 66:
        SEPOLIA_CONTRACT_ADDRESS = "0x02fa4E31f048ce6091A45E85Cc7ab63DC1D2c46a"
    else:
        SEPOLIA_CONTRACT_ADDRESS = raw_contract or "0x02fa4E31f048ce6091A45E85Cc7ab63DC1D2c46a"
        
    SEPOLIA_RPC_URL = os.environ.get("SEPOLIA_RPC_URL", "https://ethereum-sepolia-rpc.publicnode.com")

    @classmethod
    def validate(cls):
        if not cls.ADMIN_STELLAR or not cls.CONTRACT_ID:
            raise RuntimeError("Missing ADMIN_STELLAR or RPK_STELLAR in .env")
        if not cls.SEPOLIA_PRIVATE_KEY or not cls.SEPOLIA_CONTRACT_ADDRESS:
            raise RuntimeError("Missing SEPOLIA_PRIVATE_KEY or SEPOLIA_CONTRACT_ADDRESS in .env")

Config.validate()
