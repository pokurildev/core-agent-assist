import os
import yaml
from pathlib import Path
from typing import List, Optional
from functools import lru_cache
from pydantic import BaseModel, Field
from app.core.logger import logger

# BASE_DIR указывает на корень проекта (на три уровня выше этого файла: app/core/config_loader.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class VoiceSettings(BaseModel):
    provider: str
    voice_id: str = Field(..., min_length=1)
    stability: float = Field(0.5, ge=0.0, le=1.0)
    similarity_boost: float = Field(0.75, ge=0.0, le=1.0)

class AppSettings(BaseModel):
    system_prompt: str
    knowledge_base_file: Optional[str] = None
    voice_settings: VoiceSettings
    tools_enabled: List[str] = Field(default_factory=list)

def _read_knowledge_base(file_path: str) -> str:
    """Безопасно читает файл базы знаний relative to BASE_DIR."""
    path = Path(file_path)
    if not path.is_absolute():
        path = BASE_DIR / path
        
    try:
        content = path.read_text(encoding="utf-8")
        logger.info(f"Loaded knowledge base from {path.absolute()}")
        return content
    except FileNotFoundError:
        logger.error(f"Knowledge base file not found at {path.absolute()}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error reading knowledge base at {path.absolute()}: {e}")
        return ""

@lru_cache()
def get_config(config_path: str = "config/settings.yaml") -> AppSettings:
    """
    Loads, validates, and enhances the configuration from a YAML file.
    All paths are resolved relative to BASE_DIR.
    """
    path = Path(config_path)
    if not path.is_absolute():
        path = BASE_DIR / path

    if not path.exists():
        logger.error(f"Config file not found: {path.absolute()}")
        raise FileNotFoundError(f"Config file not found: {path.absolute()}")

    with open(path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # Validate with Pydantic
    settings = AppSettings(**config_data)

    # Context Injection
    if settings.knowledge_base_file:
        kb_content = _read_knowledge_base(settings.knowledge_base_file)
        if kb_content:
            separator = "\n\n=== ADDITIONAL KNOWLEDGE BASE CONTEXT ===\n"
            settings.system_prompt += f"{separator}{kb_content}"
            logger.info("Knowledge base injected into system prompt.")

    return settings
