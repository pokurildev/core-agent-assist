import sys
import json
from loguru import logger
from app.core.config import settings

# Удаляем стандартный обработчик, чтобы не было дублей
logger.remove()

# Функция для сериализации логов в JSON (для админки)
def json_serializer(record):
    subset = {
        "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S"),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "line": record["line"],
    }
    return json.dumps(subset) + "\n"

# 1. Консольный вывод (Красивый, для разработчика)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if getattr(settings, "APP_ENV", "dev") == "dev" else "INFO"
)

# 2. Файловый вывод (Плоский JSON, для Админки)
logger.add(
    "logs/app.json",
    rotation="10 MB",
    format=json_serializer,
    level="INFO"
)
