from pydantic import BaseModel
from typing import List, Any, Dict

class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]

class VapiMessage(BaseModel):
    type: str
    toolCallList: List[ToolCall]

class VapiPayload(BaseModel):
    message: VapiMessage
