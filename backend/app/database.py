"""
MongoDB database configuration and connection setup
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://admin:password123@localhost:27017/qa_bot?authSource=admin")
        self.database_name = "qa_bot"
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.database = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_database(self):
        """Get the database instance"""
        return self.database

    async def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self.database:
            await self.connect()
        return self.database[collection_name]

# Global database instance
db_config = DatabaseConfig()

async def get_database():
    """Get database instance"""
    if not db_config.database:
        await db_config.connect()
    return db_config.database

async def get_collection(collection_name: str):
    """Get a specific collection"""
    return await db_config.get_collection(collection_name)

# Synchronous client for migration scripts
def get_sync_client():
    """Get synchronous MongoDB client for migration scripts"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://admin:password123@localhost:27017/qa_bot?authSource=admin")
    return MongoClient(mongodb_url)

def get_sync_database():
    """Get synchronous database instance"""
    client = get_sync_client()
    return client["qa_bot"]