from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.api.auth import router as router_auth

from contextlib import asynccontextmanager
from src.core.logsetup import setup_logging
from src.utils.logger import get_app_logger

logger = get_app_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # setup_logging()
    logger.info("🚀 Приложение запускается")

    yield

    # Shutdown
    logger.info("🛑 Приложение останавливается")


app = FastAPI(lifespan=lifespan, title="API for Forward Trading service", root_path="/api")

app.include_router(router_auth)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Или "*" для всех (небезопасно!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
