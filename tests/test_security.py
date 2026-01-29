import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_security_verified_endpoint():
    # Use the /vapi/tool endpoint which is protected
    secret = settings.VAPI_SECRET_TOKEN
    # If secret is empty string in test env, we might need to patch it
    if not secret:
        secret = "test-secret"
    
    with pytest.MonkeyPatch.context() as m:
        from app.core import config
        # Patching the settings object directly if possible or the module property
        # Pydantic settings are tricky to patch sometimes, usually better to set env var before app init 
        # or patch the settings instance.
        m.setattr(settings, "VAPI_SECRET_TOKEN", secret)
        
        # 1. No Header
        response = client.post("/vapi/tool", json={})
        assert response.status_code == 403
        assert "header missing" in response.json()["detail"]
        
        # 2. Wrong Secret
        response = client.post("/vapi/tool", json={}, headers={"x-vapi-secret": "wrong"})
        assert response.status_code == 403
        assert "Invalid VAPI secret" in response.json()["detail"]
        
        # 3. Correct Secret (Payload validation might fail 422, but Security passes)
        # We expect 422 Unprocessable Entity if payload is missing, which comes AFTER dependency check.
        # So 422 means security passed.
        response = client.post("/vapi/tool", json={}, headers={"x-vapi-secret": secret})
        assert response.status_code == 422
