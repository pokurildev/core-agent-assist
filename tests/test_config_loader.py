import pytest
import yaml
from unittest.mock import mock_open, patch
from app.core.config_loader import get_config, read_knowledge_base, AppSettings

def test_load_yaml_config():
    yaml_content = """
    system_prompt: "You are a bot."
    first_message: "Hello!"
    voice_settings:
      provider: "vapi"
      language: "en"
    """
    
    with patch("builtins.open", mock_open(read_data=yaml_content)):
        with patch("os.path.exists", return_value=True):
            config = AppSettings.load_from_yaml("dummy.yaml")
            assert config.system_prompt == "You are a bot."
            assert config.voice_settings.language == "en"

def test_read_knowledge_base():
    kb_content = "This is important info."
    
    with patch("builtins.open", mock_open(read_data=kb_content)):
        with patch("os.path.exists", return_value=True):
            content = read_knowledge_base("dummy.txt")
            assert content == "This is important info."

def test_read_knowledge_base_missing():
    with patch("os.path.exists", return_value=False):
        content = read_knowledge_base("missing.txt")
        assert content == ""
