from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from app.core.config import settings
from app.core.logger import logger
from app.schemas.vapi import VapiInboundPayload

router = APIRouter()


# Security dependency to verify VAPI secret token
async def verify_vapi_secret(x_vapi_secret: Optional[str] = Header(None)) -> None:
    """
    Verify VAPI webhook secret token for authentication
    
    Args:
        x_vapi_secret: Secret token from request header
        
    Raises:
        HTTPException: 403 if token is invalid or missing
    """
    if not x_vapi_secret or x_vapi_secret != settings.VAPI_SECRET_TOKEN:
        logger.warning(f"Unauthorized VAPI webhook attempt with token: {x_vapi_secret}")
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing VAPI secret token"
        )
    logger.debug("VAPI secret token verified successfully")


def get_assistant_config(profile_type: str) -> dict:
    """
    Get AI assistant configuration based on customer profile
    
    This is a mock function that returns configuration for different
    customer tiers. In production, this would load from a database
    or configuration service.
    
    Args:
        profile_type: Type of customer profile ("vip", "standard", "safe")
        
    Returns:
        dict: Assistant configuration for VAPI
    """
    configs = {
        "vip": {
            "assistant": {
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "maxTokens": 500
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "premium-voice"
                },
                "firstMessage": "Hello VIP! Thank you for your loyalty. How may I assist you today?",
            }
        },
        "standard": {
            "assistant": {
                "model": {
                    "provider": "groq",
                    "model": "mixtral-8x7b-32768",
                    "temperature": 0.5,
                    "maxTokens": 300
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "standard-voice"
                },
                "firstMessage": "Hello! How can I help you today?",
            }
        },
        "safe": {
            "assistant": {
                "model": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.3,
                    "maxTokens": 200
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "default-voice"
                },
                "firstMessage": "Hello! I'm here to help you.",
            }
        }
    }
    return configs.get(profile_type, configs["safe"])


@router.post("/inbound", dependencies=[Depends(verify_vapi_secret)])
async def vapi_inbound_handler(payload: VapiInboundPayload):
    """
    VAPI Inbound Call Handler with Security and Smart Routing
    
    Features:
    - Token-based authentication via x-vapi-secret header
    - Pydantic validation for incoming webhooks
    - Blacklist filtering
    - VIP customer detection and routing
    - Graceful degradation to safe mode on errors
    
    Args:
        payload: Validated VAPI inbound webhook payload
        
    Returns:
        dict: Assistant configuration for the call
    """
    try:
        # Extract customer phone number from validated payload
        customer_number = payload.message.call.customer.number
        customer_name = payload.message.call.customer.name or "Customer"
        call_id = payload.message.call.id
        
        logger.info(
            f"Inbound call received - ID: {call_id}, "
            f"Number: {customer_number}, Name: {customer_name}"
        )
        
        # BLACKLIST CHECK: Block calls from blacklisted numbers
        if customer_number in settings.BLACKLIST_NUMBERS:
            logger.warning(f"Blocked call from blacklisted number: {customer_number}")
            return {
                "action": "block",
                "reason": "Number is blacklisted",
                "message": "This number is not authorized to use this service."
            }
        
        # VIP CHECK: Route VIP customers to premium service
        if customer_number in settings.VIP_NUMBERS:
            logger.info(f"VIP customer detected: {customer_number}")
            return get_assistant_config("vip")
        
        # STANDARD CHECK: Route regular customers to standard service
        logger.info(f"Standard customer routed: {customer_number}")
        return get_assistant_config("standard")
        
    except Exception as e:
        # GRACEFUL DEGRADATION: Return safe mode config on any error
        logger.error(
            f"Error processing inbound call: {str(e)}",
            exc_info=True
        )
        logger.warning("Falling back to Safe Mode (GPT-3.5)")
        
        return get_assistant_config("safe")
