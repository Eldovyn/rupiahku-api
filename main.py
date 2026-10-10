from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from configs.env import Config
from routes import faucet_route
from utils.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

app = FastAPI(title="RPK Token Faucet", description="Faucet for RupiahKU (RPK) token on Stellar Testnet")

@app.get("/health")
def health():
    try:
        Config.validate()
        return {"status": "ok", "message": "RPK Faucet API ready", "env": "ready"}
    except RuntimeError as e:
        # Jangan 500 biar Dokploy healthcheck tidak restart loop, tapi klien tau ENV belum ready
        return {"status": "error", "message": str(e), "env": "missing"}

@app.get("/")
def root():
    return {"message": "RPK Faucet API", "health": "/health", "mint": "POST /mint"}

@app.on_event("startup")
def on_startup():
    try:
        Config.validate()
        print("[RPK API] ENV validated: ready")
    except RuntimeError as e:
        # Jangan crash container — biar /health jelasin miss ENV, dan /mint balikin 500 jelas
        print(f"[RPK API] ENV missing at startup: {e}")

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
        
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, If-None-Match"
    response.headers["Access-Control-Expose-Headers"] = "ETag"
    return response

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(faucet_route.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
