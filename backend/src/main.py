from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.router import api_router
from src.auth.router import auth_route

THIS_DIR = Path(__file__).parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield

app = FastAPI(
    title="MarketPulse",
    description="The Market Pulse API Documentation",
    version="1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"msg": exc.errors()[0]["msg"]},
    )

app.include_router(api_router)
app.include_router(auth_route)