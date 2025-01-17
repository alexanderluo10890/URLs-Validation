from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

def add_exception_handlers(app: FastAPI):
    """Add global exception handlers to the FastAPI app."""
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logging.error(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"},
        )
