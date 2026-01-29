import requests
import json
import os
from app.core.config import settings
from app.services.vapi_tools import get_all_tools

BASE_URL = "https://api.vapi.ai"

def get_headers():
    return {
        "Authorization": f"Bearer {settings.VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }

def create_assistant():
    """Create a new Vapi assistant."""
    headers = get_headers()
    
    # Get tools definitions
    tools = get_all_tools()
    
    # Corrected data structure: systemPrompt and tools inside model
    data = {
        "name": "Omnicore AI Assistant",
        "firstMessage": "Здравствуйте! Я — Omnicore AI, ваш умный core-ассистент. Чем могу помочь сегодня?",
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "systemPrompt": "Ты — продвинутый AI-ассистент Omnicore AI. Отвечай на русском. Используй function calling для tools, если нужно взаимодействовать с внешними системами (Telegram, Google Sheets, поиск и т.д.). Будь полезным, точным, вежливым, кратким. Если задача требует инструмента — обязательно его вызывай.",
            "tools": tools
        }
    }

    print(f"Creating assistant with name: {data['name']}...")
    try:
        response = requests.post(f"{BASE_URL}/assistant", json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        assistant_id = result.get("id")
        print(f"Success! Assistant created.")
        print(f"Assistant ID: {assistant_id}")
        
        # Save to file
        output_file = "app/core/vapi_assistant_id.txt"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            f.write(assistant_id)
        print(f"Assistant ID saved to {output_file}")
        
        return assistant_id
    except requests.exceptions.RequestException as e:
        print(f"Error creating assistant: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
            # Debugging: print full data if failed
            # print(f"Data sent: {json.dumps(data, indent=2)}")
        return None

def update_assistant(assistant_id, updates: dict):
    """Update an existing Vapi assistant."""
    headers = get_headers()
    url = f"{BASE_URL}/assistant/{assistant_id}"
    
    print(f"Updating assistant {assistant_id}...")
    try:
        response = requests.patch(url, json=updates, headers=headers)
        response.raise_for_status()
        result = response.json()
        print("Assistant updated successfully.")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error updating assistant: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    # Ensure VAPI_PRIVATE_KEY is present
    if not settings.VAPI_PRIVATE_KEY:
        print("Error: VAPI_PRIVATE_KEY is not set in settings or .env")
        exit(1)
        
    create_assistant()
