
from fastapi import Request, HTTPException
from app.core.config import settings
import hmac
import hashlib


async def verify_webhook_signature_middleware(request: Request) -> bool:
    """
    Verify webhook signature for security.

    Args:
        request: FastAPI request object

    Returns:
        bool: True if signature is valid

    Raises:
        HTTPException: If signature verification fails
    """
    payload = await request.body()
    if not settings.WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured

    signature = request.headers.get("X-Webhook-Signature")
    if not signature:
        raise HTTPException(
            status_code=401, detail="Missing webhook signature")

    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(f"sha256={expected_signature}", signature):
        raise HTTPException(
            status_code=401, detail="Invalid webhook signature")

    return True
