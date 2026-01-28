from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logger import logger
from app.core.config_loader import get_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Omnicore AI Backend...")
    yield
    logger.info("Shutting down Omnicore AI Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/config/reload")
async def reload_config():
    """
    Очищает кэш lru_cache для обновления настроек без перезапуска сервера.
    """
    get_config.cache_clear()
    logger.info("Configuration cache cleared successfully.")
    return {"status": "success", "message": "Configuration reloaded"}

from app.handlers.inbound import vapi_inbound_handler

@app.post("/inbound")
async def vapi_inbound(request: Request):
    return await vapi_inbound_handler(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
