from fastapi import APIRouter
from app.schemas.vapi import VapiPayload
from app.core.config import settings

router = APIRouter() # No prefix here if we include with prefix in main, or prefix here if not. 
# User asked for: @router.post("/tool") and prefix="/vapi" in the router definition or main.
# User code: router = APIRouter(prefix="/vapi") ... @router.post("/tool")
# I will follow that.

router = APIRouter(prefix="/vapi")

@router.post("/tool")
async def handle_tool(payload: VapiPayload):
    results = []
    print(f"Received Vapi tool call payload: {payload}")
    
    for call in payload.message.toolCallList:
        tool_id = call.id
        name = call.name
        args = call.arguments
        
        result = ""

        if name == "send_telegram_message":
            chat_id = args.get("chat_id") or settings.ADMIN_CHAT_ID
            text = args.get("text")
            
            if not text:
                result = "Ошибка: текст сообщения не указан"
            else:
                try:
                    # Simple HTTP request to Telegram Bot API to avoid async loop issues with Aiogram in this simple handler for now
                    # or use httpx which is async friendly.
                    import httpx
                    
                    if not settings.TELEGRAM_BOT_TOKEN:
                        result = "Ошибка: TELEGRAM_BOT_TOKEN не настроен"
                    else:
                        telegram_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
                        async with httpx.AsyncClient() as client:
                            resp = await client.post(telegram_url, json={"chat_id": chat_id, "text": text})
                            if resp.status_code == 200:
                                result = "Сообщение успешно отправлено в Telegram"
                            else:
                                result = f"Ошибка Telegram API: {resp.text}"
                except Exception as e:
                    result = f"Ошибка при отправке в Telegram: {str(e)}"
            
            print(f"Executed tool {name}: {result}")
            
        elif name == "add_to_google_sheets":
            try:
                # Google Sheets Logic
                from google.oauth2.service_account import Credentials
                from googleapiclient.discovery import build
                import json
                
                if not settings.GOOGLE_CREDENTIALS_JSON or not settings.SPREADSHEET_ID:
                     result = "Ошибка: Настройки Google Sheets не заполнены"
                else:
                    # Parse JSON credentials
                    creds_dict = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
                    creds = Credentials.from_service_account_info(
                        creds_dict,
                        scopes=["https://www.googleapis.com/auth/spreadsheets"]
                    )
                    service = build("sheets", "v4", credentials=creds)
                    
                    # Prepare row data
                    customer_name = args.get("name", "Unknown")
                    phone = args.get("phone", "Unknown")
                    notes = args.get("notes", "")
                    row = [[customer_name, phone, notes]]
                    
                    sheet_range = f"{settings.GOOGLE_SHEET_NAME}!A:C"
                    
                    service.spreadsheets().values().append(
                        spreadsheetId=settings.SPREADSHEET_ID,
                        range=sheet_range,
                        valueInputOption="USER_ENTERED",
                        body={"values": row}
                    ).execute()
                    
                    result = "Данные успешно добавлены в Google таблицу"
            except Exception as e:
                result = f"Ошибка Google Sheets: {str(e)}"
                
            print(f"Executed tool {name}: {result}")
            
        else:
            result = f"Tool {name} не реализован"
            print(f"Unknown tool {name}")

        results.append({"toolCallId": tool_id, "result": result})

    return {"results": results}
