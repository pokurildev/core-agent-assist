import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.api.vapi.client import VapiClient, VapiConfig
from app.api.vapi.assistants.manager import AssistantManager, AssistantBuilder, AssistantConfig


@pytest.mark.asyncio
async def test_assistant_builder():
    """Тест билдера ассистентов"""
    builder = AssistantBuilder()
    config = (builder
        .with_name("Test Assistant")
        .with_system_prompt("You are a test assistant")
        .with_model("openai", "gpt-4o")
        .with_voice("11labs", "rachel")
        .build()
    )
    
    assert config["name"] == "Test Assistant"
    assert config["model"]["messages"][0]["content"] == "You are a test assistant"
    assert config["voice"]["voiceId"] == "rachel"


@pytest.mark.asyncio
async def test_webhook_handler_routing():
    """Тест роутинга событий в WebhookHandler"""
    from app.api.vapi.webhooks.handler import webhook_handler, WebhookEventType
    
    # Регистрируем тестовый обработчик
    mock_handler = AsyncMock(return_value={"status": "handled"})
    
    # Сохраняем оригинальные обработчики
    original_handlers = webhook_handler._handlers.get(WebhookEventType.CALL_STARTED, [])
    webhook_handler._handlers[WebhookEventType.CALL_STARTED] = [mock_handler]
    
    try:
        test_data = {
            "type": "call.started",
            "call": {"id": "test_call_id"}
        }
        
        result = await webhook_handler.handle("call.started", test_data)
        
        mock_handler.assert_called_once_with(test_data)
        assert result == {"status": "handled"}
    finally:
        # Восстанавливаем оригинальные обработчики
        webhook_handler._handlers[WebhookEventType.CALL_STARTED] = original_handlers


@pytest.mark.asyncio
async def test_vapi_client_request():
    """Тест базового клиента Vapi с моком HTTP"""
    config = VapiConfig(api_key="test_key")
    client = VapiClient(config)
    
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        # Create a mock for the response
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "new_assistant_id"}
        mock_response.raise_for_status = MagicMock()
        
        mock_request.return_value = mock_response
        
        result = await client.post("/assistant", json={"name": "Test"})
        
        assert result["id"] == "new_assistant_id"
        mock_request.assert_called_once()
