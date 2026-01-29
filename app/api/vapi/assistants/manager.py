"""
Менеджер для работы с ассистентами Vapi
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from ..client import VapiClient
import logging

logger = logging.getLogger(__name__)


class TranscriberConfig(BaseModel):
    """Конфигурация транскрибера"""
    provider: str = "deepgram"
    model: str = "nova-2"
    language: str = "ru"  # или "multi" для мультиязычности
    keywords: Optional[List[str]] = None


class ModelConfig(BaseModel):
    """Конфигурация языковой модели"""
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 500
    messages: List[Dict[str, str]] = Field(default_factory=list)
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    tool_ids: Optional[List[str]] = None


class VoiceConfig(BaseModel):
    """Конфигурация голоса"""
    provider: str = "11labs"
    voice_id: str = "rachel"
    speed: float = 1.0
    stability: Optional[float] = None
    similarity_boost: Optional[float] = None


class AssistantConfig(BaseModel):
    """Полная конфигурация ассистента"""
    name: str
    transcriber: TranscriberConfig
    model: ModelConfig
    voice: VoiceConfig
    first_message: Optional[str] = None
    first_message_mode: str = "assistant-speaks-first"
    max_duration_seconds: int = 600
    background_sound: str = "office"
    server_url: Optional[str] = None  # URL для вебхуков
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssistantManager:
    """
    Менеджер для CRUD операций с ассистентами
    """
    
    def __init__(self, client: VapiClient):
        self.client = client
        
    async def create_assistant(self, config: AssistantConfig) -> Dict[str, Any]:
        """
        Создать нового ассистента
        
        Args:
            config: Конфигурация ассистента
            
        Returns:
            Созданный ассистент с ID
        """
        payload = {
            "name": config.name,
            "transcriber": config.transcriber.dict(),
            "model": {
                "provider": config.model.provider,
                "model": config.model.model,
                "temperature": config.model.temperature,
                "maxTokens": config.model.max_tokens,
                "messages": config.model.messages,
                "tools": config.model.tools,
            },
            "voice": config.voice.dict(exclude_none=True),
            "firstMessage": config.first_message,
            "firstMessageMode": config.first_message_mode,
            "maxDurationSeconds": config.max_duration_seconds,
            "backgroundSound": config.background_sound,
            "metadata": config.metadata
        }
        
        if config.model.tool_ids:
            payload["model"]["toolIds"] = config.model.tool_ids
            
        if config.server_url:
            payload["server"] = {"url": config.server_url}
        
        logger.info(f"Creating assistant: {config.name}")
        result = await self.client.post("/assistant", json=payload)
        logger.info(f"Assistant created with ID: {result.get('id')}")
        return result
    
    async def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """Получить ассистента по ID"""
        return await self.client.get(f"/assistant/{assistant_id}")
    
    async def list_assistants(
        self,
        limit: int = 100,
        created_at_gt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить список ассистентов
        
        Args:
            limit: Максимальное количество результатов
            created_at_gt: Фильтр по дате создания (ISO 8601)
        """
        params = {"limit": limit}
        if created_at_gt:
            params["createdAtGt"] = created_at_gt
            
        return await self.client.get("/assistant", params=params)
    
    async def update_assistant(
        self,
        assistant_id: str,
        config: AssistantConfig
    ) -> Dict[str, Any]:
        """Обновить ассистента"""
        payload = config.dict(exclude_none=True)
        return await self.client.patch(f"/assistant/{assistant_id}", json=payload)
    
    async def delete_assistant(self, assistant_id: str) -> None:
        """Удалить ассистента"""
        await self.client.delete(f"/assistant/{assistant_id}")
        logger.info(f"Assistant {assistant_id} deleted")


class AssistantBuilder:
    """
    Builder для удобного создания конфигураций ассистентов
    """
    
    def __init__(self):
        self.config = {
            "transcriber": {},
            "model": {"messages": [], "tools": []},
            "voice": {},
            "metadata": {}
        }
    
    def with_name(self, name: str):
        """Установить имя ассистента"""
        self.config["name"] = name
        return self
    
    def with_system_prompt(self, prompt: str):
        """Установить системный промпт"""
        self.config["model"]["messages"].append({
            "role": "system",
            "content": prompt
        })
        return self
    
    def with_model(self, provider: str, model: str, temperature: float = 0.7):
        """Настроить модель"""
        self.config["model"].update({
            "provider": provider,
            "model": model,
            "temperature": temperature
        })
        return self
    
    def with_voice(self, provider: str, voice_id: str, speed: float = 1.0):
        """Настроить голос"""
        self.config["voice"] = {
            "provider": provider,
            "voiceId": voice_id,
            "speed": speed
        }
        return self
    
    def with_transcriber(self, provider: str = "deepgram", language: str = "ru"):
        """Настроить транскрибер"""
        self.config["transcriber"] = {
            "provider": provider,
            "language": language
        }
        return self
    
    def add_tool(self, tool: Dict[str, Any]):
        """Добавить инструмент"""
        self.config["model"]["tools"].append(tool)
        return self
    
    def with_first_message(self, message: str):
        """Установить первое сообщение"""
        self.config["firstMessage"] = message
        return self
    
    def with_server_url(self, url: str):
        """Установить URL для вебхуков"""
        self.config["server"] = {"url": url}
        return self
    
    def build(self) -> Dict[str, Any]:
        """Построить финальную конфигурацию"""
        return self.config
