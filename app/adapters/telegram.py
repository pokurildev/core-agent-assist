import httpx
from app.core.config import settings
from app.core.logger import logger

async def send_message(text: str, chat_id: str = None) -> str:
    """
    Sends a message to a Telegram chat asynchronously using httpx.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    target_chat = chat_id or settings.ADMIN_CHAT_ID

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN is not set")
        return "Error: Bot token missing"
    
    if not target_chat:
        logger.warning("No chat_id provided and ADMIN_CHAT_ID is missing")
        return "Error: No chat ID"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": target_chat, "text": text}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Telegram message sent to {target_chat}")
            return "Message sent successfully"
    except httpx.HTTPStatusError as e:
        logger.error(f"Telegram API error: {e.response.text}")
        return f"Telegram API Error: {e.response.status_code}"
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return f"Error: {str(e)}"
