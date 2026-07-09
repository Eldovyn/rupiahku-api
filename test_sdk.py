import os
from dotenv import load_dotenv
from stellar_sdk import Server, Keypair, Network, TransactionBuilder, scval, SorobanServer
from stellar_sdk.soroban_rpc import GetTransactionStatus

load_dotenv()
ADMIN_SECRET = os.environ.get("ADMIN_STELLAR")
CONTRACT_ID = os.environ.get("RPK_STELLAR")
NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE
RPC_URL = "https://soroban-testnet.stellar.org"

admin_keypair = Keypair.from_secret(ADMIN_SECRET)
soroban_server = SorobanServer(RPC_URL)

from stellar_sdk import Server as HorizonServer
horizon_server = HorizonServer("https://horizon-testnet.stellar.org")
account = horizon_server.load_account(admin_keypair.public_key)

tx_builder = TransactionBuilder(
    source_account=account,
    network_passphrase=NETWORK_PASSPHRASE,
    base_fee=10000
)

admin_address_val = scval.to_address(admin_keypair.public_key)
to_address_val = scval.to_address("GDJ4JOYXVHVS6VPL6YAIKWABCLB2NJVQBKBRHCWSQQTVWBHTPZ3BLQFX")
amount_val = scval.to_int128(100 * 10**7)

tx_builder.append_invoke_contract_function_op(
    contract_id=CONTRACT_ID,
    function_name="mint",
    parameters=[admin_address_val, to_address_val, amount_val]
)

tx = tx_builder.build()

print("Simulating...")
sim_resp = soroban_server.simulate_transaction(tx)
print("Simulation result:", sim_resp)

print("Preparing...")
tx = soroban_server.prepare_transaction(tx)
tx.sign(admin_keypair)

print("Sending...")
send_resp = soroban_server.send_transaction(tx)
print("Send result:", send_resp)
