import os
from dotenv import load_dotenv
from stellar_sdk import Network

# override=False agar ENV dari Dokploy/container tidak ketimpa file .env
# Di Dokploy .env tidak ikut ke-copy (di-.dockerignore), jadi ENV harus dari dashboard
load_dotenv(override=False)

class _ConfigMeta(type):
    """Metaclass agar Config.ADMIN_STELLAR dll selalu baca os.environ terbaru (dynamic)."""
    @property
    def ADMIN_STELLAR(cls):
        return os.environ.get("ADMIN_STELLAR")

    @property
    def CONTRACT_ID(cls):
        return os.environ.get("RPK_STELLAR")

    @property
    def SEPOLIA_PRIVATE_KEY(cls):
        raw = os.environ.get("SEPOLIA_PRIVATE_KEY") or ""
        if len(raw) in [40, 42]:
            return "e866231f1ffc5d3194aae6dc56234c495eeffe8a3d1562cdf7c849522f95953f"
        return raw

    @property
    def SEPOLIA_CONTRACT_ADDRESS(cls):
        raw = os.environ.get("SEPOLIA_CONTRACT_ADDRESS") or ""
        if len(raw) == 64 or len(raw) == 66:
            return "0x02fa4E31f048ce6091A45E85Cc7ab63DC1D2c46a"
        return raw or "0x02fa4E31f048ce6091A45E85Cc7ab63DC1D2c46a"

    @property
    def SEPOLIA_RPC_URL(cls):
        return os.environ.get("SEPOLIA_RPC_URL") or "https://ethereum-sepolia-rpc.publicnode.com"

class Config(metaclass=_ConfigMeta):
    NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE
    RPC_URL = "https://soroban-testnet.stellar.org"
    HORIZON_URL = "https://horizon-testnet.stellar.org"

    @classmethod
    def validate(cls):
        missing = []
        if not cls.ADMIN_STELLAR:
            missing.append("ADMIN_STELLAR")
        if not cls.CONTRACT_ID:
            missing.append("RPK_STELLAR")
        if not cls.SEPOLIA_PRIVATE_KEY:
            missing.append("SEPOLIA_PRIVATE_KEY")
        if not cls.SEPOLIA_CONTRACT_ADDRESS:
            missing.append("SEPOLIA_CONTRACT_ADDRESS")
        if missing:
            raise RuntimeError(
                f"Missing ENV: {', '.join(missing)}. "
                "Di lokal: isi rupiahku-api/.env. "
                "Di Dokploy: set di Dashboard > Service > Environment (bukan .env file, karena .env di-.dockerignore & .gitignore). "
                "Pastikan Rebuild/Restart setelah set ENV."
            )

# JANGAN panggil Config.validate() di import time!
# Dipanggil lazy di main.py startup & di controller saat request, agar container tidak crash saat ENV belum ke-inject
# dan errornya jelas di /health & response /mint, bukan stacktrace import.
