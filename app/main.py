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

@app.get("/v1/config")
async def fetch_current_config():
    config = get_config()
    return config

@app.post("/v1/config")
async def update_current_config(new_config: dict):
    import yaml
    from pathlib import Path
    from app.core.config_loader import AppSettings
    
    # Валидация данных перед сохранением
    try:
        AppSettings(**new_config)
    except Exception as e:
        logger.error(f"Invalid config submitted: {e}")
        return {"status": "error", "message": f"Validation failed: {e}"}

    # Путь к конфигу (аналогично config_loader.py)
    BASE_DIR = Path(__file__).resolve().parent.parent
    config_path = BASE_DIR / "config" / "settings.yaml"
    
    # Сохраняем новый YAML
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(new_config, f, allow_unicode=True, sort_keys=False)
    
    # Сбрасываем кэш
    get_config.cache_clear()
    logger.info(f"Configuration updated and written to {config_path}")
    
    return {"status": "success", "message": "Config updated"}

@app.get("/v1/logs")
async def fetch_logs():
    import os
    import json
    from pathlib import Path
    
    log_file = Path("logs/app.json")
    if not log_file.exists():
        return []
        
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Берем последние 50 строк
            last_lines = lines[-50:]
            logs = []
            for line in last_lines:
                try:
                    entry = json.loads(line.strip())
                    if isinstance(entry, dict) and "message" in entry:
                        logs.append(entry)
                except:
                    continue
            return logs
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return {"error": str(e)}

from app.handlers.inbound import vapi_inbound_handler

@app.post("/inbound")
async def vapi_inbound(request: Request):
    return await vapi_inbound_handler(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
