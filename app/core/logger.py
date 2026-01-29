import sys
import json
import asyncio
import threading
from loguru import logger


def telegram_sink(message):
    """
    Custom Loguru sink that sends ERROR and CRITICAL logs to Telegram
    
    This sink runs in a separate thread to avoid blocking the logger
    and handles the async-to-sync bridge for the Telegram API call.
    """
    record = message.record
    
    # Only process ERROR and CRITICAL logs
    if record["level"].name not in ["ERROR", "CRITICAL"]:
        return
    
    # Format the alert message
    alert_text = (
        f"🚨 <b>{record['level'].name}</b>\n\n"
        f"<b>Module:</b> {record['module']}\n"
        f"<b>Function:</b> {record['function']}\n"
        f"<b>Line:</b> {record['line']}\n\n"
        f"<b>Message:</b>\n{record['message']}"
    )
    
    # Truncate if too long (Telegram has a 4096 character limit)
    if len(alert_text) > 4000:
        alert_text = alert_text[:3997] + "..."
    
    # Run the async Telegram function in a separate thread
    def send_in_thread():
        try:
            # Import here to avoid circular dependency
            from app.adapters.telegram import send_message
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(send_message(alert_text))
            finally:
                loop.close()
        except Exception as e:
            # Use stderr to avoid infinite logging loop
            print(f"[Telegram Sink] Error: {e}", file=sys.stderr)
    
    # Start thread and don't wait for it (fire-and-forget)
    thread = threading.Thread(target=send_in_thread, daemon=True)
    thread.start()


from app.core.config import settings

def configure_logging():
    """
    Configures logging based on application environment.
    """
    # Remove default handler
    logger.remove()
    
    # 1. Console Output
    if settings.APP_ENV == "prod":
        # JSON format for production (better for CloudWatch / ELK)
        logger.add(sys.stderr, serialize=True, level="INFO")
    else:
        # Pretty colored format for development
        logger.add(
            sys.stderr, 
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
            level="DEBUG"
        )

    # 2. File Output (Always JSON for machine readability)
    logger.add(
        "logs/app.json", 
        rotation="10 MB", 
        serialize=True,
        level="INFO"
    )

    # 3. Telegram Alerting (ERROR+)
    if settings.TELEGRAM_BOT_TOKEN and settings.ADMIN_CHAT_ID:
        logger.add(
            telegram_sink,
            level="ERROR",
            format="{message}"
        )
