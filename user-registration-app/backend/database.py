"""MongoDB database connection setup using Motor and Beanie ODM."""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/user_registration_db")
DATABASE_NAME = os.getenv("DATABASE_NAME", "user_registration_db")


async def init_database(document_models=None):
    """Initialize MongoDB connection and Beanie ODM."""
    if document_models is None:
        document_models = []
    # Add connection timeout parameters
    client = AsyncIOMotorClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,  # 10 seconds
        connectTimeoutMS=10000
    )
    await init_beanie(database=client[DATABASE_NAME], document_models=document_models)

