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
    
    SEPOLIA_PRIVATE_KEY = os.environ.get("RPK_SEPOLIA")
    SEPOLIA_CONTRACT_ADDRESS = os.environ.get("ADMIN_SEPOLIA")
    SEPOLIA_RPC_URL = os.environ.get("SEPOLIA_RPC_URL", "https://rpc.sepolia.org")

    @classmethod
    def validate(cls):
        if not cls.ADMIN_STELLAR or not cls.CONTRACT_ID:
            raise RuntimeError("Missing ADMIN_STELLAR or RPK_STELLAR in .env")
        if not cls.SEPOLIA_PRIVATE_KEY or not cls.SEPOLIA_CONTRACT_ADDRESS:
            raise RuntimeError("Missing RPK_SEPOLIA or ADMIN_SEPOLIA in .env")

Config.validate()
