from fastapi import Request
from app.services.tools_registry import get_dynamic_tool_schema
from app.core.config_loader import get_config
from app.core.logger import logger

async def vapi_inbound_handler(request: Request):
    """
    Inbound handler for VAPI webhooks.
    Injects dynamic tools based on configuration.
    """
    payload = await request.json()
    logger.info(f"Received VAPI webhook: {payload}")
    
    config = get_config()
    dynamic_fields = config.voice_settings.dynamic_fields
    
    # Генерация динамической схемы инструментов
    tools = [get_dynamic_tool_schema(dynamic_fields)] if dynamic_fields else []
    
    # Если VAPI запрашивает конфигурацию ассистента
    if payload.get("message", {}).get("type") == "assistant-request":
        return {
            "assistant": {
                "model": {
                    "provider": "openai",
                    "model": "gpt-4-turbo",
                    "tools": tools
                }
            }
        }

    return {"status": "received", "vapi_status": "success"}
