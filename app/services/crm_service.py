from app.adapters.telegram import send_message
from app.adapters.google_sheets import sheets_manager
from app.core.config import settings
from app.core.logger import logger

async def send_telegram(text: str, chat_id: str = None) -> str:
    """
    Service method to send telegram message.
    """
    logger.info(f"Service: Sending Telegram message: {text[:20]}...")
    return await send_message(text, chat_id)

async def add_lead(name: str, phone: str, notes: str) -> str:
    """
    Service method to add a lead to CRM (Google Sheets).
    """
    logger.info(f"Service: Adding lead {name}, {phone}")
    
    if not settings.SPREADSHEET_ID:
        logger.error("SPREADSHEET_ID is not configured")
        return "Error: Spreadsheet ID missing"
        
    range_name = f"{settings.GOOGLE_SHEET_NAME}!A:C"
    row = [name, phone, notes]
    
    return await sheets_manager.append_row(settings.SPREADSHEET_ID, range_name, row)
