from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors_dict = {}
    for err in exc.errors():
        field = str(err["loc"][-1]) if err.get("loc") else "body"
        errors_dict[field] = "IS_INVALID"
        
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "gagal memproses permintaan",
            "data": None,
            "errors": errors_dict
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        message = "gagal memproses permintaan"
        errors = exc.detail
    else:
        message = str(exc.detail)
        errors = None
        
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": message,
            "data": None,
            "errors": errors
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal Server Error",
            "data": None,
            "errors": None
        }
    )
