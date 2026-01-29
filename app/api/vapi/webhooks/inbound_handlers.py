"""
Мигрированные обработчики вебхуков Vapi
"""
from typing import Dict, Any
from .handler import webhook_handler, WebhookEventType
from app.core.config_loader import get_config, read_knowledge_base
from app.services.crm import process_new_lead
from app.core.logger import logger
from ..tools.registry import tool_registry

@webhook_handler.on(WebhookEventType.ASSISTANT_REQUEST)
async def handle_assistant_request(data: Dict[str, Any]):
    """
    Обработка запроса конфигурации ассистента при входящем звонке
    """
    logger.info("Handling Assistant Request via WebhookHandler")
    config = get_config()
    
    # Инъекция базы знаний в промпт
    full_prompt = config.system_prompt
    if config.knowledge_base_file:
        kb = read_knowledge_base(config.knowledge_base_file)
        if kb:
            full_prompt = f"{full_prompt}\n\n### KNOWLEDGE BASE ###\n{kb}"
            logger.info("Knowledge base injected into system prompt.")

    # Получаем инструменты из реестра
    # В реальности здесь может быть фильтрация или динамическая сборка
    tools = tool_registry.get_all_tools()
    
    # Строим полный объект ассистента согласно документации VAPI
    assistant_config = {
        "assistant": {
            "name": "Omnicore AI Assistant",
            "firstMessage": config.first_message,
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": config.voice_settings.language
            },
            "model": {
                "provider": "openai",
                "model": config.voice_settings.model,
                "messages": [
                    {
                        "role": "system",
                        "content": full_prompt
                    }
                ],
                "tools": tools
            },
            "voice": {
                "provider": config.voice_settings.provider,
                "voiceId": config.voice_settings.voice_id,
                "stability": config.voice_settings.stability,
                "similarityBoost": config.voice_settings.similarity_boost
            }
        }
    }
    logger.info(f"Returning assistant override (Language: {config.voice_settings.language})")
    return assistant_config


@webhook_handler.on(WebhookEventType.END_OF_CALL_REPORT)
async def handle_end_of_call_report(data: Dict[str, Any]):
    """
    Обработка отчета о завершении звонка
    """
    report = data.get("endOfCallReport", {})
    call_obj = data.get("call", {})
    
    analysis = report.get("analysis", {})
    lead_data = analysis.get("structuredData") or {}
    
    # Обогащаем данными о самом звонке
    lead_data.update({
        "call_id": call_obj.get("id"),
        "phone": call_obj.get("customer", {}).get("number") or call_obj.get("customerNumber"),
        "name": call_obj.get("customer", {}).get("name") or call_obj.get("customerName"),
        "summary": report.get("summary") or "",
        "transcript": report.get("transcript") or ""
    })
    
    phone_display = lead_data.get("phone") or "unknown"
    logger.info(f"Processing call report for {phone_display}")
    
    # В FastAPI роуте мы не имеем прямого доступа к BackgroundTasks здесь,
    # поэтому просто вызываем сервис. Если нужно асинхронно - сервис должен это поддерживать
    # или мы можем обернуть это в асинхронную задачу.
    try:
        await process_new_lead(lead_data)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing lead: {e}")
        return {"status": "error", "message": str(e)}
