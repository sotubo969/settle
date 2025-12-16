"""
MongoDB connection for Emergent Auth
Handles user sessions and OAuth user data
"""
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'afromarket')

# MongoDB Client (singleton)
mongo_client = None
mongo_db = None


def get_mongo_db():
    """Get MongoDB database instance"""
    global mongo_client, mongo_db
    
    if mongo_db is None:
        mongo_client = AsyncIOMotorClient(MONGO_URL)
        mongo_db = mongo_client[DB_NAME]
    
    return mongo_db


async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongo_client
    if mongo_client:
        mongo_client.close()


async def init_mongo_indexes():
    """Initialize MongoDB indexes for performance"""
    db = get_mongo_db()
    
    # Users collection indexes
    await db.users.create_index("user_id", unique=True)
    await db.users.create_index("email", unique=True)
    
    # Sessions collection indexes
    await db.user_sessions.create_index("session_token", unique=True)
    await db.user_sessions.create_index("user_id")
    await db.user_sessions.create_index("expires_at")
    
    print("MongoDB indexes created successfully")
