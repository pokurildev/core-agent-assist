"""
FastAPI роуты для вебхуков Vapi
"""
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging

from ..vapi.webhooks.handler import webhook_handler
from ..vapi.webhooks import inbound_handlers # Этим импортом регистрируем обработчики

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/vapi", tags=["vapi-webhooks"])


@router.post("/webhook")
async def vapi_webhook(request: Request):
    """
    Эндпоинт для приема вебхуков от Vapi
    
    Vapi отправляет события на этот URL:
    - call.started
    - call.ended
    - function-call
    - transcript
    - и другие
    """
    try:
        # Получаем данные
        data = await request.json()
        
        # Vapi оборачивает событие в ключ "message"
        event_data = data.get("message", data)
        event_type = event_data.get("type")
        
        if not event_type:
            logger.error("Missing event type in webhook")
            # Log raw data for debugging
            logger.debug(f"Raw webhook data: {data}")
            raise HTTPException(status_code=400, detail="Missing event type")
        
        logger.info(f"Received webhook: {event_type}")
        
        # Обрабатываем событие
        result = await webhook_handler.handle(event_type, event_data)
        
        # If the handler returned something, Vapi expects it in the response
        # (especially for function-call and assistant-request)
        if result is not None:
            return result
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/function-call")
async def function_call_webhook(request: Request):
    """
    Специализированный эндпоинт для вызовов функций
    
    Используется когда ассистент вызывает custom функцию
    через apiRequest или специализированный эндпоинт
    """
    try:
        data = await request.json()
        # Vapi structure varies slightly depending on how it's called
        message = data.get("message", {})
        function_call = message.get("functionCall", {})
        
        if not function_call:
            # Fallback for direct function call payloads
            function_call = data.get("functionCall", data)
            
        function_name = function_call.get("name")
        parameters = function_call.get("parameters", {})
        
        if not function_name:
            logger.error(f"Missing function name in request: {data}")
            raise HTTPException(status_code=400, detail="Missing function name")
            
        logger.info(f"Direct function call received: {function_name}")
        
        # Импортируем реестр
        from ..vapi.tools.registry import tool_registry
        
        # Выполняем функцию
        result = await tool_registry.execute_function(function_name, **parameters)
        
        return {"result": result}
        
    except Exception as e:
        logger.error(f"Error in function call: {str(e)}", exc_info=True)
        return {"error": str(e)}
