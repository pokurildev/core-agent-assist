import httpx
import sys
from app.core.config import settings


async def send_telegram_message(text: str) -> None:
    """
    Send a message to Telegram admin chat via Bot API
    
    This function is designed to be resilient - if Telegram API fails,
    it fails silently with stderr logging to avoid infinite logging loops.
    
    Args:
        text: Message text to send to admin chat
    """
    # Skip if Telegram is not configured
    if not settings.TELEGRAM_BOT_TOKEN or not settings.ADMIN_CHAT_ID:
        print(
            "[Telegram] Skipping alert - TELEGRAM_BOT_TOKEN or ADMIN_CHAT_ID not configured",
            file=sys.stderr
        )
        return
    
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        payload = {
            "chat_id": settings.ADMIN_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
    except httpx.TimeoutException:
        # Use stderr to avoid triggering more log events
        print(
            f"[Telegram] Timeout sending alert: {text[:100]}...",
            file=sys.stderr
        )
    except httpx.HTTPStatusError as e:
        print(
            f"[Telegram] HTTP error {e.response.status_code} sending alert",
            file=sys.stderr
        )
    except Exception as e:
        print(
            f"[Telegram] Unexpected error sending alert: {type(e).__name__}: {e}",
            file=sys.stderr
        )
