import requests
import json
import os

# Используем localhost, так как backend запущен локально.
# Если нужно проверить именно через ngrok, поменяйте на ваш ngrok URL.
URL = "http://localhost:8000/vapi/tool"

payload = {
    "message": {
        "type": "tool-calls",
        "toolCallList": [
            {
                "id": "test-call-telegram",
                "name": "send_telegram_message",
                "arguments": {
                    "text": "Тестовое сообщение из Python-скрипта! 🚀"
                }
            },
            {
                "id": "test-call-sheets",
                "name": "add_to_google_sheets",
                "arguments": {
                    "name": "Тестовый Клиент", 
                    "phone": "+79998887766", 
                    "notes": "Проверка записи из скрипта"
                }
            }
        ]
    }
}

print(f"📡 Отправляю запрос на {URL}...")
print(f"📦 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(URL, json=payload)
    print(f"\n✅ Status Code: {response.status_code}")
    try:
        data = response.json()
        print("📄 Response JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print("Response text:", response.text)
except Exception as e:
    print(f"\n❌ Ошибка подключения: {e}")
    print("Проверьте, запущен ли сервер (uvicorn) на порту 8000.")
