import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def mock_crm_service():
    with patch("app.handlers.vapi_handler.crm_service") as mock:
        mock.send_telegram = AsyncMock()
        mock.add_lead = AsyncMock()
        yield mock

def test_vapi_tool_telegram(mock_crm_service):
    secret = settings.VAPI_SECRET_TOKEN or "test-secret"
    # Ensure settings match if it's not set in env during test
    with patch("app.core.config.settings.VAPI_SECRET_TOKEN", secret):
        payload = {
            "message": {
                "type": "tool-calls",
                "toolCallList": [
                    {
                        "id": "call_1",
                        "name": "send_telegram_message",
                        "arguments": {"text": "Hello", "chat_id": "123"}
                    }
                ]
            }
        }
        
        headers = {"x-vapi-secret": secret}
        response = client.post("/vapi/tool", json=payload, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["results"][0]["result"] == "Message queued"
        
        # Verify background task was presumably added (or we can't easily verify background tasks with TestClient without extra setup, 
        # but we can verify the mock was called if we use TestClient with a context that runs tasks, or just trust the handler logic for now.
        # However, TestClient logic runs synchronously. BackgroundTasks are executed after response.
        # We might need to manually trigger them or just check if add_task was called if we mocked BackgroundTasks.
        # But here we mocked crm_service. Tests usually run background tasks in TestClient? 
        # Actually Starlette TestClient runs background tasks.
        
        mock_crm_service.send_telegram.assert_called_with("Hello", "123")

def test_vapi_tool_sheets(mock_crm_service):
    secret = settings.VAPI_SECRET_TOKEN or "test-secret"
    with patch("app.core.config.settings.VAPI_SECRET_TOKEN", secret):
        payload = {
            "message": {
                "type": "tool-calls",
                "toolCallList": [
                    {
                        "id": "call_2",
                        "name": "add_to_google_sheets",
                        "arguments": {"name": "John", "phone": "555", "notes": "Test"}
                    }
                ]
            }
        }
        
        headers = {"x-vapi-secret": secret}
        response = client.post("/vapi/tool", json=payload, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["results"][0]["result"] == "Lead processing started"
        
        mock_crm_service.add_lead.assert_called_with("John", "555", "Test")
