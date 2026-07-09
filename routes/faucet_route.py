from fastapi import APIRouter, status
from schemas.faucet_schema import MintRequest
from controllers.faucet_controller import FaucetController

router = APIRouter()
faucet_controller = FaucetController()

@router.post("/mint", status_code=status.HTTP_201_CREATED)
def mint_token(req: MintRequest):
    return faucet_controller.mint_token(req)
