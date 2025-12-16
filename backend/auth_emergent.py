"""
Emergent Auth Integration Module
Handles Google OAuth via Emergent's authentication service
"""
import httpx
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Cookie, Header
from typing import Optional
import uuid

# Emergent Auth Configuration
EMERGENT_AUTH_API = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
SESSION_EXPIRY_DAYS = 7


async def exchange_session_id(session_id: str) -> dict:
    """
    Exchange session_id from Emergent auth for user data
    
    Args:
        session_id: Temporary session ID from URL fragment
        
    Returns:
        dict with user data: id, email, name, picture, session_token
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                EMERGENT_AUTH_API,
                headers={"X-Session-ID": session_id}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401, 
                    detail=f"Failed to verify session: {response.text}"
                )
            
            user_data = response.json()
            return user_data
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, 
            detail="Authentication service timeout"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Authentication service error: {str(e)}"
        )


def generate_user_id() -> str:
    """Generate a unique user_id using UUID"""
    return f"user_{uuid.uuid4().hex[:12]}"


async def get_current_user_from_token(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    db = None
) -> dict:
    """
    Get current user from session_token (cookie or Authorization header)
    
    Priority: Cookie first, then Authorization header
    """
    token = session_token
    
    # Fallback to Authorization header if no cookie
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # MongoDB query to get session
    session_doc = await db.user_sessions.find_one(
        {"session_token": token},
        {"_id": 0}
    )
    
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry with timezone awareness
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user data
    user_doc = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0}
    )
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_doc


async def create_or_update_user(db, user_data: dict) -> str:
    """
    Create new user or update existing user from OAuth data
    
    Returns:
        user_id: The user's unique identifier
    """
    email = user_data.get("email")
    
    # Check if user exists
    existing_user = await db.users.find_one(
        {"email": email},
        {"_id": 0}
    )
    
    if existing_user:
        # Update existing user
        await db.users.update_one(
            {"email": email},
            {
                "$set": {
                    "name": user_data.get("name", existing_user.get("name")),
                    "picture": user_data.get("picture", existing_user.get("picture")),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        return existing_user["user_id"]
    else:
        # Create new user with custom user_id
        user_id = generate_user_id()
        await db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "name": user_data.get("name", ""),
            "picture": user_data.get("picture", ""),
            "role": "customer",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })
        return user_id


async def save_session(db, user_id: str, session_token: str):
    """Save user session to database"""
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS),
        "created_at": datetime.now(timezone.utc)
    })


async def delete_session(db, session_token: str):
    """Delete user session from database"""
    await db.user_sessions.delete_one({"session_token": session_token})
