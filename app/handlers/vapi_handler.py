from fastapi import APIRouter, Depends, BackgroundTasks
from app.schemas.vapi import VapiPayload
from app.core.config import settings
from app.core.security import verify_vapi_secret
from app.core.logger import logger
from app.services import crm_service

router = APIRouter() # No prefix here if we include with prefix in main, or prefix here if not. 
# User asked for: @router.post("/tool") and prefix="/vapi" in the router definition or main.
# User code: router = APIRouter(prefix="/vapi") ... @router.post("/tool")
# I will follow that.

router = APIRouter(prefix="/vapi")

@router.post("/tool", dependencies=[Depends(verify_vapi_secret)])
async def handle_tool(payload: VapiPayload, background_tasks: BackgroundTasks):
    results = []
    logger.info(f"Received Vapi tool call payload: {payload.message.toolCallList}")
    
    for call in payload.message.toolCallList:
        tool_id = call.id
        name = call.name
        args = call.arguments
        
        result = "Processing" # Default immediate response
        
        try:
            if name == "send_telegram_message":
                chat_id = args.get("chat_id")
                text = args.get("text", "")
                
                # Run in background for speed
                background_tasks.add_task(crm_service.send_telegram, text, chat_id)
                result = "Message queued"
                
            elif name == "add_to_google_sheets":
                username = args.get("name", "Unknown")
                phone = args.get("phone", "Unknown")
                notes = args.get("notes", "")
                
                # Run in background
                background_tasks.add_task(crm_service.add_lead, username, phone, notes)
                result = "Lead processing started"
                
            else:
                result = f"Tool {name} не реализован"
                logger.warning(f"Unknown tool called: {name}")
                
        except Exception as e:
            logger.error(f"Error handling tool {name}: {e}")
            result = f"Error: {str(e)}"

        results.append({"toolCallId": tool_id, "result": result})

    return {"results": results}
