"""
Менеджер для работы со звонками Vapi
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from ..client import VapiClient
import logging

logger = logging.getLogger(__name__)


class CustomerInfo(BaseModel):
    """Информация о клиенте для звонка"""
    number: str  # Номер телефона в формате E.164: +1234567890
    name: Optional[str] = None
    extension: Optional[str] = None


class CallConfig(BaseModel):
    """Конфигурация звонка"""
    assistant_id: Optional[str] = None
    assistant: Optional[Dict[str, Any]] = None  # Inline конфигурация
    customer: CustomerInfo
    phone_number_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class CallManager:
    """
    Менеджер для работы со звонками
    """
    
    def __init__(self, client: VapiClient):
        self.client = client
    
    async def create_call(self, config: CallConfig) -> Dict[str, Any]:
        """
        Создать исходящий звонок
        
        Args:
            config: Конфигурация звонка
            
        Returns:
            Информация о созданном звонке
        """
        payload = {
            "customer": config.customer.dict(exclude_none=True),
            "metadata": config.metadata
        }
        
        if config.assistant_id:
            payload["assistantId"] = config.assistant_id
        elif config.assistant:
            payload["assistant"] = config.assistant
        else:
            raise ValueError("Either assistant_id or assistant config must be provided")
        
        if config.phone_number_id:
            payload["phoneNumberId"] = config.phone_number_id
        
        logger.info(f"Creating outbound call to {config.customer.number}")
        result = await self.client.post("/call", json=payload)
        logger.info(f"Call created with ID: {result.get('id')}")
        return result
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Получить информацию о звонке"""
        return await self.client.get(f"/call/{call_id}")
    
    async def list_calls(
        self,
        limit: int = 100,
        assistant_id: Optional[str] = None,
        created_at_gt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить список звонков
        
        Args:
            limit: Максимальное количество
            assistant_id: Фильтр по ассистенту
            created_at_gt: Фильтр по дате
        """
        params = {"limit": limit}
        if assistant_id:
            params["assistantId"] = assistant_id
        if created_at_gt:
            params["createdAtGt"] = created_at_gt
            
        return await self.client.get("/call", params=params)
    
    async def end_call(self, call_id: str) -> None:
        """Завершить активный звонок"""
        await self.client.delete(f"/call/{call_id}")
        logger.info(f"Call {call_id} ended")
