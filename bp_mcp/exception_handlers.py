import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

LOGGER = logging.getLogger(__name__)


def register_exception_handlers(api: FastAPI) -> None:
    @api.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions with Developer API error format."""
        # For 401 errors, use AuthorizationError format
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "errors": [
                        {
                            "code": "unauthorized",
                            "status": exc.status_code,
                            "title": exc.detail,
                        }
                    ]
                },
            )

        # For other HTTP errors, use ErrorObject format
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": exc.status_code,
                "error": exc.__class__.__name__,
                "message": exc.detail,
            },
        )

    @api.exception_handler(Exception)
    async def unhandled_exception(_: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions with Developer API error format."""
        LOGGER.exception("API unhandled exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal Server Error",
                "message": f"API unhandled exception: {exc!s}",
            },
        )
