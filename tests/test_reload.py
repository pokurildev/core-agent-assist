from app.main import app
from app.core.config_loader import get_config
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_config_reload():
    print("--- Testing Config Reload Endpoint ---")
    
    # Fill cache
    get_config()
    print("Config loaded (cached).")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Call reload endpoint
        response = await ac.post("/config/reload")
        
        print(f"Response Status: {response.status_code}")
        print(f"Response JSON: {response.json()}")
        
        if response.status_code == 200 and response.json().get("status") == "success":
            print("\nSUCCESS: Config reload endpoint verified!")
        else:
            print("\nFAILURE: Config reload failed!")

if __name__ == "__main__":
    asyncio.run(test_config_reload())
