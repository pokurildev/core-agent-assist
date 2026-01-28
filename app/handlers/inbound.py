from fastapi import APIRouter, Request
from app.core.logger import logger

router = APIRouter()

@router.post("/inbound")
async def vapi_inbound_handler(request: Request):
    """
    VAPI Inbound Call Handler with VIP Routing Logic
    
    Routes incoming calls to appropriate AI models based on caller number:
    - VIP customers (+1111111111): GPT-4o
    - Regular customers: Faster model (Groq/Haiku)
    
    Implements graceful degradation - if any error occurs, returns a safe
    fallback configuration to ensure the call continues.
    """
    try:
        # Parse incoming VAPI webhook payload
        payload = await request.json()
        logger.info(f"Received inbound call webhook: {payload}")
        
        # Extract customer phone number from payload
        customer_number = payload.get("message", {}).get("customer", {}).get("number", "")
        logger.info(f"Caller number: {customer_number}")
        
        # VIP Detection Logic
        if customer_number == "+1111111111":
            # VIP customer - route to GPT-4o
            logger.info("VIP customer detected - routing to GPT-4o")
            return {
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
                    "firstMessage": "Hello VIP! How may I assist you today?",
                }
            }
        else:
            # Regular customer - route to faster model
            logger.info("Regular customer - routing to Groq/Haiku")
            return {
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
            }
            
    except Exception as e:
        # Graceful Degradation: If anything fails, return safe mode config
        logger.error(f"Error processing inbound call: {str(e)}", exc_info=True)
        logger.warning("Falling back to Safe Mode (GPT-3.5)")
        
        return {
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
