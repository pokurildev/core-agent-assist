import sys
import json
from loguru import logger

# Удаляем старые кастомные форматы, если они ломают запуск
logger.remove()

# 1. Консольный вывод (Красивый, для разработчика)
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
)

# 2. Файловый вывод (Самый надежный способ для JSON)
logger.add(
    "logs/app.json", 
    rotation="10 MB", 
    serialize=True
)
