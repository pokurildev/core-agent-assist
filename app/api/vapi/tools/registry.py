"""
Реестр инструментов для ассистентов
"""
from typing import Dict, Any, List, Callable, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Параметр инструмента"""
    type: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None


class APIRequestTool(BaseModel):
    """Инструмент для HTTP запросов"""
    type: str = "apiRequest"
    name: str
    description: str
    method: str = "POST"  # GET, POST, PATCH, DELETE
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 20


class MCPTool(BaseModel):
    """MCP инструмент для динамических интеграций"""
    type: str = "mcp"
    function: Dict[str, str] = Field(default_factory=lambda: {"name": "mcpTools"})
    server: Dict[str, Any]
    metadata: Dict[str, str] = Field(default_factory=lambda: {"protocol": "shttp"})


class CustomFunctionTool(BaseModel):
    """Пользовательский инструмент-функция"""
    type: str = "function"
    name: str
    description: str
    parameters: Dict[str, ToolParameter]
    handler: Optional[Callable] = None  # Локальный обработчик


class ToolRegistry:
    """
    Реестр всех доступных инструментов
    """
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
    
    def register_api_tool(
        self,
        name: str,
        description: str,
        url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        body_schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Зарегистрировать API инструмент
        
        Returns:
            ID зарегистрированного инструмента
        """
        tool = APIRequestTool(
            name=name,
            description=description,
            method=method,
            url=url,
            headers=headers or {},
            body=body_schema
        )
        
        self._tools[name] = tool.dict()
        logger.info(f"Registered API tool: {name}")
        return name
    
    def register_mcp_tool(
        self,
        name: str,
        server_url: str,
        headers: Optional[Dict[str, str]] = None,
        protocol: str = "shttp"
    ) -> str:
        """
        Зарегистрировать MCP инструмент
        
        Args:
            name: Имя инструмента
            server_url: URL MCP сервера
            headers: Дополнительные заголовки
            protocol: Протокол (shttp или sse)
        """
        tool = MCPTool(
            server={
                "url": server_url,
                "headers": headers or {}
            },
            metadata={"protocol": protocol}
        )
        
        self._tools[name] = tool.dict()
        logger.info(f"Registered MCP tool: {name}")
        return name
    
    def register_function_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, ToolParameter],
        handler: Callable
    ) -> str:
        """
        Зарегистрировать пользовательский функциональный инструмент
        
        Args:
            name: Имя функции
            description: Описание для модели
            parameters: Схема параметров
            handler: Функция-обработчик
        """
        # Convert ToolParameter objects to dict if they are not already
        params_dict = {k: v.dict() if isinstance(v, ToolParameter) else v for k, v in parameters.items()}
        
        tool = CustomFunctionTool(
            name=name,
            description=description,
            parameters=params_dict
        )
        
        self._tools[name] = tool.dict(exclude={"handler"})
        self._handlers[name] = handler
        logger.info(f"Registered function tool: {name}")
        return name
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Получить инструмент по имени"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Получить все зарегистрированные инструменты"""
        return list(self._tools.values())
    
    def get_handler(self, name: str) -> Optional[Callable]:
        """Получить обработчик функции"""
        return self._handlers.get(name)
    
    async def execute_function(self, name: str, **kwargs) -> Any:
        """Выполнить функцию-обработчик"""
        handler = self.get_handler(name)
        if not handler:
            raise ValueError(f"No handler found for function: {name}")
        
        logger.info(f"Executing function: {name}")
        return await handler(**kwargs)


# Глобальный реестр инструментов
tool_registry = ToolRegistry()
