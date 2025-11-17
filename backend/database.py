"""MongoDB database connection setup using Motor and Beanie ODM."""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/push_db")
DATABASE_NAME = os.getenv("DATABASE_NAME", "push_db")


async def init_database(document_models=None):
    """Initialize MongoDB connection and Beanie ODM."""
    if document_models is None:
        document_models = []
    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(database=client[DATABASE_NAME], document_models=document_models)

