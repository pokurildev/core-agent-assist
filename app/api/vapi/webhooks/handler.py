"""
Обработчик вебхуков от Vapi
"""
from typing import Dict, Any, Callable, List, Optional
from enum import Enum
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class WebhookEventType(str, Enum):
    """Типы событий вебхуков"""
    # Call events
    CALL_STARTED = "call.started"
    CALL_ENDED = "call.ended"
    CALL_FAILED = "call.failed"
    
    # Assistant events
    ASSISTANT_STARTED = "assistant.started"
    ASSISTANT_REQUEST = "assistant-request"
    
    # Conversation events
    CONVERSATION_UPDATE = "conversation-update"
    TRANSCRIPT = "transcript"
    
    # Function calls
    FUNCTION_CALL = "function-call"
    TOOL_CALLS = "tool-calls"
    
    # Status events
    STATUS_UPDATE = "status-update"
    SPEECH_UPDATE = "speech-update"
    
    # Transfer events
    TRANSFER_UPDATE = "transfer-update"
    TRANSFER_DESTINATION_REQUEST = "transfer-destination-request"
    
    # End of call
    END_OF_CALL_REPORT = "end-of-call-report"
    
    # Voicemail
    VOICEMAIL_DETECTION = "voicemail-detection"


class WebhookMessage(BaseModel):
    """Базовая модель вебхук сообщения"""
    type: str
    call: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


class WebhookHandler:
    """
    Обработчик вебхуков от Vapi
    """
    
    def __init__(self):
        self._handlers: Dict[WebhookEventType, List[Callable]] = {}
        
    def on(self, event_type: WebhookEventType):
        """
        Декоратор для регистрации обработчика события
        
        Usage:
            @webhook_handler.on(WebhookEventType.CALL_STARTED)
            async def handle_call_started(data: Dict[str, Any]):
                print(f"Call started: {data['call']['id']}")
        """
        def decorator(func: Callable):
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            logger.info(f"Registered handler for event: {event_type.value}")
            return func
        return decorator
    
    async def handle(self, event_type: str, data: Dict[str, Any]) -> Any:
        """
        Обработать входящий вебхук
        
        Args:
            event_type: Тип события
            data: Данные события
        """
        try:
            event = WebhookEventType(event_type)
        except ValueError:
            logger.warning(f"Unknown webhook event type: {event_type}")
            return
        
        handlers = self._handlers.get(event, [])
        if not handlers:
            logger.debug(f"No handlers registered for event: {event_type}")
            return
        
        logger.info(f"Processing {len(handlers)} handlers for event: {event_type}")
        results = []
        for handler in handlers:
            try:
                res = await handler(data)
                if res is not None:
                    results.append(res)
            except Exception as e:
                logger.error(f"Error in webhook handler: {str(e)}", exc_info=True)
        
        # Return first non-None result if any
        return results[0] if results else None


# Глобальный обработчик вебхуков
webhook_handler = WebhookHandler()


# Примеры обработчиков (можно вынести в отдельный файл или handlers/)

@webhook_handler.on(WebhookEventType.CALL_STARTED)
async def log_call_started(data: Dict[str, Any]):
    """Логирование начала звонка"""
    call_id = data.get("call", {}).get("id")
    logger.info(f"Call started: {call_id}")


@webhook_handler.on(WebhookEventType.CALL_ENDED)
async def process_call_ended(data: Dict[str, Any]):
    """Обработка завершения звонка"""
    call = data.get("call", {})
    call_id = call.get("id")
    reason = call.get("endedReason")
    logger.info(f"Call ended: {call_id}, reason: {reason}")


@webhook_handler.on(WebhookEventType.FUNCTION_CALL)
async def handle_function_call(data: Dict[str, Any]):
    """Обработка вызова функции ассистентом"""
    # Note: Vapi structure for function call inside generic webhook
    message = data.get("message", {})
    function_call = message.get("functionCall", {})
    if not function_call:
        # Fallback to direct access if already unwrapped
        function_call = data.get("functionCall", {})
        
    function_name = function_call.get("name")
    parameters = function_call.get("parameters", {})
    
    logger.info(f"Function called via webhook: {function_name} with params: {parameters}")
    
    # Import registry here to avoid circular imports if any
    from ..tools.registry import tool_registry
    
    try:
        result = await tool_registry.execute_function(function_name, **parameters)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error executing function {function_name}: {str(e)}")
        return {"error": str(e)}
