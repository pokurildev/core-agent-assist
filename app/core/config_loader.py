import yaml
import os
from functools import lru_cache
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from app.core.logger import logger

# Models corresponding to settings.yaml structure
class VoiceSettings(BaseModel):
    provider: str = "deepgram"
    model: str = "nova-2"
    voice_id: str = "s3://voice-cloning-zero-shot/775be1e6-14e5-4f7f-94d3-05908cf818c3/original/file.mp3"
    stability: float = 0.5
    similarity_boost: float = 0.75
    language: str = "ru"

class AppSettings(BaseModel):
    system_prompt: str = ""
    first_message: str = ""
    voice_settings: VoiceSettings = Field(default_factory=VoiceSettings)
    knowledge_base_file: str = "config/knowledge_base.txt"
    tools_enabled: List[str] = Field(default_factory=list)

    @classmethod
    def load_from_yaml(cls, path: str) -> "AppSettings":
        if not os.path.exists(path):
            logger.warning(f"Config file not found at {path}, using defaults.")
            return cls()
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return cls(**data)
        except Exception as e:
            logger.error(f"Error loading config from {path}: {e}")
            return cls()

@lru_cache()
def get_config(config_path: str = "config/settings.yaml") -> AppSettings:
    """
    Cached config loader. Returns AppSettings object.
    """
    # Assuming the config is at the root of the project or relative to cwd
    return AppSettings.load_from_yaml(config_path)

def read_knowledge_base(file_path: str) -> str:
    """
    Reads the knowledge base text file.
    """
    if not os.path.exists(file_path):
        logger.warning(f"Knowledge base file not found: {file_path}")
        return ""
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error reading knowledge base: {e}")
        return ""

def reload_config():
    """
    Clears the cache to reload config on next call.
    """
    get_config.cache_clear()
    logger.info("Config cache cleared.")
