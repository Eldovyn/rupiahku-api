from pydantic import BaseModel

class MintRequest(BaseModel):
    wallet_address: str
    amount: int = 100
    network: str = "stellar"
