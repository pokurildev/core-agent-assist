from pydantic import BaseModel, Field
from typing import Optional


class VapiCustomer(BaseModel):
    """Customer information from VAPI webhook"""
    number: str = Field(..., description="Customer phone number")
    name: Optional[str] = Field(None, description="Customer name if available")


class VapiCall(BaseModel):
    """Call information from VAPI webhook"""
    id: str = Field(..., description="Unique call identifier")
    customer: VapiCustomer = Field(..., description="Customer information")


class VapiMessage(BaseModel):
    """Message payload from VAPI webhook"""
    call: VapiCall = Field(..., description="Call information")
    type: str = Field(..., description="Message type (e.g., 'inbound-call')")


class VapiInboundPayload(BaseModel):
    """Complete VAPI inbound webhook payload"""
    message: VapiMessage = Field(..., description="Message containing call details")
