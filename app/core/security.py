"""
Security utilities for webhook validation and authentication.
Handles signature verification and request validation.
"""
from fastapi import Security, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from passlib.context import CryptContext
from datetime import datetime, timedelta
# from jose import JWTError, jwt
from app.core.config import settings
import hmac
import hashlib

# Security-related functions for authentication and authorization

# Define the OAuth2 scheme
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Function to hash passwords
# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# # Function to verify passwords
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# # Function to create JWT tokens
# def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt

# # Function to decode JWT tokens
# def decode_access_token(token: str):
#     credentials_exception = HTTPException(
#         status_code=401,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         return payload
#     except JWTError:
#         raise credentials_exception

# # Function to get the current user from the token
# def get_current_user(token: str = Security(oauth2_scheme)):
#     credentials = decode_access_token(token)
#     return credentials


def verify_webhook_signature(request: Request, payload: bytes) -> bool:
    """
    Verify webhook signature for security.
    
    Args:
        request: FastAPI request object
        payload: Raw request payload bytes
        
    Returns:
        bool: True if signature is valid
        
    Raises:
        HTTPException: If signature verification fails
    """
    if not settings.WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured
        
    signature = request.headers.get("X-Webhook-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing webhook signature")
    
    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(f"sha256={expected_signature}", signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    return True