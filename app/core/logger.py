import sys
from loguru import logger
import json

def json_serializer(record):
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "extra": record["extra"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }
    return json.dumps(subset)

def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        format="{message}",
        serialize=True,
        level="INFO"
    )

setup_logging()
