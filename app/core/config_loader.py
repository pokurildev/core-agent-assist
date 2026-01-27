import os
import yaml
from pathlib import Path
from typing import List, Optional
from functools import lru_cache
from pydantic import BaseModel, Field
from app.core.logger import logger

class VoiceSettings(BaseModel):
    provider: str
    voice_id: str
    stability: float = 0.5
    similarity_boost: float = 0.75

class AppSettings(BaseModel):
    system_prompt: str
    knowledge_base_file: Optional[str] = None
    voice_settings: VoiceSettings
    tools_enabled: List[str] = Field(default_factory=list)

def _read_knowledge_base(file_path: str) -> str:
    """Reads the knowledge base file if it exists."""
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"Knowledge base file not found at {file_path}")
        return ""
    
    try:
        content = path.read_text(encoding="utf-8")
        logger.info(f"Loaded knowledge base from {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error reading knowledge base file: {e}")
        return ""

@lru_cache()
def get_config(config_path: str = "config/settings.yaml") -> AppSettings:
    """
    Loads, validates, and enhances the configuration from a YAML file.
    Implements Context Injection for the knowledge base.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

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
