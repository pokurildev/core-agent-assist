"""
Скрипт для деплоя ассистентов в Vapi
"""
import asyncio
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

from app.api.vapi.client import VapiClient, VapiConfig
from app.api.vapi.assistants.manager import AssistantManager, AssistantConfig


async def deploy_assistant(config_file: Path):
    """Деплой ассистента из YAML файла"""
    # Загружаем конфигурацию
    with open(config_file, "r", encoding="utf-8") as f:
        # Резолвим переменные окружения в YAML если нужно (простой вариант)
        content = f.read()
        # Можно добавить логику замены ${VAR} если требуется
        config_dict = yaml.safe_load(content)
    
    # Создаем клиент
    api_key = os.getenv("VAPI_API_KEY")
    if not api_key:
        print("Error: VAPI_API_KEY environment variable not set")
        return
        
    client = VapiClient(VapiConfig(api_key=api_key))
    manager = AssistantManager(client)
    
    # Валидируем через Pydantic (модель AssistantConfig)
    # Примечание: Pydantic v2 требует model_validate или **dict
    try:
        assistant_config = AssistantConfig(**config_dict)
        
        # Создаем ассистента
        assistant = await manager.create_assistant(assistant_config)
        print(f"Deployed assistant: {assistant.get('name')} (ID: {assistant.get('id')})")
        return assistant
    except Exception as e:
        print(f"Error deploying {config_file.name}: {e}")
        return None


async def main():
    """Деплой всех ассистентов из папки config/assistants"""
    # Определяем путь к корню проекта
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    config_dir = PROJECT_ROOT / "config" / "assistants"
    
    if not config_dir.exists():
        print(f"Directory {config_dir} not found")
        return

    print(f"Searching for assistant templates in {config_dir}...")
    for config_file in config_dir.glob("*.yaml"):
        print(f"Deploying {config_file.name}...")
        await deploy_assistant(config_file)


if __name__ == "__main__":
    asyncio.run(main())
