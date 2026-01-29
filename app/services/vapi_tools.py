from app.core.config import settings

def define_telegram_tool():
    """Tool definition for sending Telegram messages."""
    return {
        "type": "function",
        "function": {
            "name": "send_telegram_message",
            "description": "Send a message to the admin via Telegram.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string", 
                        "description": "The text message to send."
                    },
                    # Note: We can make chat_id optional if we use the admin ID from settings by default
                    "chat_id": {
                        "type": "string", 
                        "description": "Optional chat ID. Defaults to admin."
                    }
                },
                "required": ["text"]
            }
        },
        "server": {
            "url": f"{settings.VAPI_SERVER_URL.rstrip('/')}/vapi/tool"
        }
    }

def define_sheets_tool():
    """Tool definition for adding data to Google Sheets."""
    return {
        "type": "function",
        "function": {
            "name": "add_to_google_sheets",
            "description": "Add lead information to Google Sheets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer name"},
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "notes": {"type": "string", "description": "Any additional notes"}
                },
                "required": ["name", "phone"]
            }
        },
        "server": {
            "url": f"{settings.VAPI_SERVER_URL.rstrip('/')}/vapi/tool"
        }
    }

def get_all_tools():
    """Return list of all tool definitions."""
    return [
        define_telegram_tool(),
        define_sheets_tool()
    ]
