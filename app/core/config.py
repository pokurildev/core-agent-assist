from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Omnicore AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "dev"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # VAPI Settings
    VAPI_PRIVATE_KEY: str = ""
    VAPI_PUBLIC_KEY: str = ""
    VAPI_WEBHOOK_SECRET: str = ""
    VAPI_SECRET_TOKEN: str = ""
    
    # VAPI Call Routing
    VIP_NUMBERS: List[str] = ["+1111111111"]
    BLACKLIST_NUMBERS: List[str] = []
    
    # AI Providers
    OPENAI_API_KEY: str = ""

    # Telegram Monitoring
    TELEGRAM_BOT_TOKEN: str = ""
    ADMIN_CHAT_ID: str = ""
    
    # Google Sheets Integration
    GOOGLE_CREDENTIALS_JSON: str = ""
    SPREADSHEET_ID: str = ""
    GOOGLE_SHEET_NAME: str = "Leads"
    
    # Frontend Auth
    VITE_ADMIN_PASSWORD: str = ""
    
    # Vapi Server URL for Tools
    VAPI_SERVER_URL: str = "https://your-domain.ngrok-free.app"

    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        env_file_encoding='utf-8'
    )

settings = Settings()
