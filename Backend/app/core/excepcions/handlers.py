from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.excepcions.base import FlowosException


async def flowos_exception_handler(
    request: Request,
    exc: FlowosException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message
        }
    )