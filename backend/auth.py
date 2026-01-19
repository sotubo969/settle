from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'afromarket-secret-key-2025')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Simple user info class to mimic User object attributes
class UserInfo:
    def __init__(self, id: int, email: str, name: str = None, role: str = None):
        self.id = id
        self.email = email
        self.name = name or email.split('@')[0]  # Default name from email
        self.role = role

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Dependency that extracts and validates the JWT token.
    Returns a UserInfo object with id, email, name attributes.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        name = payload.get("name")
        role = payload.get("role")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token - missing user ID")
        
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token - missing email")
        
        return UserInfo(id=int(user_id), email=email, name=name, role=role)
    except JWTError as e:
        print(f"JWT Decode Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user_from_db(credentials: HTTPAuthorizationCredentials = Security(security), db: AsyncSession = None):
    """Get full user object from database"""
    from database import User
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if db is None:
        # Return UserInfo if no db provided
        return UserInfo(id=int(user_id), email=payload.get("email"))
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

async def get_current_vendor(current_user = Depends(get_current_user)):
    if current_user.role != 'vendor':
        raise HTTPException(status_code=403, detail="Vendor access required")
    return current_user
