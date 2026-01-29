"""
Базовый HTTP клиент для работы с Vapi API
"""
from typing import Optional, Dict, Any, List
import httpx
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class VapiConfig(BaseModel):
    """Конфигурация Vapi клиента"""
    api_key: str
    base_url: str = "https://api.vapi.ai"
    timeout: int = 30
    max_retries: int = 3


class VapiClient:
    """
    Базовый клиент для взаимодействия с Vapi API
    """
    
    def __init__(self, config: VapiConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Выполнить HTTP запрос к Vapi API"""
        url = f"{self.config.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=json,
                    params=params
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error: {str(e)}")
                raise
    
    async def get(self, endpoint: str, params: Optional[Dict] = None):
        """GET запрос"""
        return await self._request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, json: Dict[str, Any]):
        """POST запрос"""
        return await self._request("POST", endpoint, json=json)
    
    async def patch(self, endpoint: str, json: Dict[str, Any]):
        """PATCH запрос"""
        return await self._request("PATCH", endpoint, json=json)
    
    async def delete(self, endpoint: str):
        """DELETE запрос"""
        return await self._request("DELETE", endpoint)
