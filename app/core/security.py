import secrets
from fastapi import Header, HTTPException, status
from app.core.config import settings

async def verify_vapi_secret(x_vapi_secret: str = Header(None)):
    """
    Security dependency to verify the VAPI secret token.
    
    Args:
        x_vapi_secret: The secret token from the header 'x-vapi-secret'
        
    Raises:
        HTTPException: 403 Forbidden if the secret is missing or invalid.
    """
    if not x_vapi_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="VAPI secret header missing"
        )
    
    # Use compare_digest to prevent timing attacks
    if not secrets.compare_digest(x_vapi_secret, settings.VAPI_SECRET_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid VAPI secret"
        )
