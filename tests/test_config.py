import pytest
import yaml
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from pydantic import ValidationError
from app.core.config_loader import get_config, AppSettings

@pytest.fixture(autouse=True)
def clear_cache():
    """Сбрасываем кэш перед каждым тестом."""
    get_config.cache_clear()

def test_get_config_success():
    """Проверяет успешный парсинг YAML и создание модели."""
    yaml_content = {
        "system_prompt": "Base system prompt",
        "voice_settings": {
            "provider": "elevenlabs",
            "voice_id": "adam",
            "stability": 0.5,
            "similarity_boost": 0.75
        },
        "tools_enabled": ["web_search"]
    }
    yaml_str = yaml.dump(yaml_content)
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=yaml_str)):
        
        config = get_config()
        assert isinstance(config, AppSettings)
        assert config.system_prompt == "Base system prompt"
        assert config.voice_settings.provider == "elevenlabs"
        assert "web_search" in config.tools_enabled

def test_context_injection_success():
    """Проверяет, что база знаний успешно 'подшивается' в промпт."""
    yaml_content = {
        "system_prompt": "Base prompt",
        "knowledge_base_file": "config/knowledge_base.txt",
        "voice_settings": {
            "provider": "elevenlabs",
            "voice_id": "adam"
        }
    }
    yaml_str = yaml.dump(yaml_content)
    kb_content = "This is some expert knowledge."
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=yaml_str)), \
         patch("pathlib.Path.read_text", return_value=kb_content):
        
        config = get_config()
        assert "Base prompt" in config.system_prompt
        assert kb_content in config.system_prompt
        assert "ADDITIONAL KNOWLEDGE BASE CONTEXT" in config.system_prompt

def test_knowledge_base_not_found():
    """Проверяет обработку отсутствующего файла базы знаний."""
    yaml_content = {
        "system_prompt": "Base prompt",
        "knowledge_base_file": "config/non_existent.txt",
        "voice_settings": {
            "provider": "elevenlabs",
            "voice_id": "adam"
        }
    }
    yaml_str = yaml.dump(yaml_content)
    
    # Эмулируем FileNotFoundError при чтении KB
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=yaml_str)), \
         patch("pathlib.Path.read_text", side_effect=FileNotFoundError), \
         patch("app.core.config_loader.logger") as mock_logger:
        
        config = get_config()
        # Промпт не должен измениться
        assert config.system_prompt == "Base prompt"
        # Должна быть залогирована ошибка
        # В config_loader.py используется logger.error
        mock_logger.error.assert_called()

def test_config_file_not_found():
    """Проверяет падение с FileNotFoundError при отсутствии основного конфига."""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            get_config("missing_settings.yaml")

def test_config_invalid_type():
    """Проверяет валидацию типов (строка вместо числа в stability)."""
    yaml_content = {
        "system_prompt": "Base prompt",
        "voice_settings": {
            "provider": "elevenlabs",
            "voice_id": "adam",
            "stability": "NOT_A_NUMBER"
        }
    }
    yaml_str = yaml.dump(yaml_content)
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=yaml_str)):
        
        with pytest.raises(ValidationError):
            get_config()

def test_config_missing_field():
    """Проверяет реакцию на отсутствие обязательного поля."""
    yaml_content = {
        "system_prompt": "Base prompt",
        "voice_settings": {
            "provider": "elevenlabs"
            # voice_id отсутствует
        }
    }
    yaml_str = yaml.dump(yaml_content)
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=yaml_str)):
        
        with pytest.raises(ValidationError):
            get_config()

def test_config_out_of_range():
    """Проверяет валидацию границ значений (stability > 1.0)."""
    yaml_content = {
        "system_prompt": "Base prompt",
        "voice_settings": {
            "provider": "elevenlabs",
            "voice_id": "adam",
            "stability": 1.5  # Выход за границу [0, 1]
        }
    }
    yaml_str = yaml.dump(yaml_content)
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=yaml_str)):
        
        with pytest.raises(ValidationError):
            get_config()
