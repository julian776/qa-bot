#!/usr/bin/env python3
"""
Migration script to move data from PostgreSQL to MongoDB
This script migrates document chunks and embeddings from PostgreSQL to MongoDB + Qdrant
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import numpy as np

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataMigration:
    """Handles migration from PostgreSQL to MongoDB + Qdrant"""
    
    def __init__(self):
        # PostgreSQL connection (source)
        self.postgres_url = os.getenv("POSTGRES_URL", "postgresql://qa_bot_user:qa_bot_password@localhost:5432/qa_bot")
        
        # MongoDB connection (destination)
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://admin:password123@localhost:27017/qa_bot?authSource=admin")
        
        # Qdrant connection (destination)
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        # Initialize connections
        self.postgres_engine = None
        self.mongodb_client = None
        self.qdrant_client = None
        
    def connect_postgres(self):
        """Connect to PostgreSQL"""
        try:
            self.postgres_engine = create_engine(self.postgres_url)
            Session = sessionmaker(bind=self.postgres_engine)
            session = Session()
            
            # Test connection
            result = session.execute(text("SELECT 1")).fetchone()
            logger.info("Connected to PostgreSQL successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongodb_client = MongoClient(self.mongodb_url)
            db = self.mongodb_client["qa_bot"]
            
            # Test connection
            db.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def connect_qdrant(self):
        """Connect to Qdrant"""
        try:
            self.qdrant_client = QdrantClient(url=self.qdrant_url)
            
            # Test connection
            collections = self.qdrant_client.get_collections()
            logger.info("Connected to Qdrant successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            return False
    
    def migrate_document_chunks(self):
        """Migrate document chunks from PostgreSQL to MongoDB"""
        try:
            Session = sessionmaker(bind=self.postgres_engine)
            session = Session()
            
            # Get all document chunks from PostgreSQL
            query = text("""
                SELECT 
                    id,
                    user_id,
                    document_name,
                    chunk_index,
                    text_chunk,
                    chunk_size,
                    created_at,
                    metadata
                FROM document_chunks
                ORDER BY user_id, document_name, chunk_index
            """)
            
            result = session.execute(query).fetchall()
            logger.info(f"Found {len(result)} document chunks to migrate")
            
            # Prepare MongoDB documents
            mongodb_db = self.mongodb_client["qa_bot"]
            chunks_collection = mongodb_db["chunks"]
            
            migrated_count = 0
            for row in result:
                chunk_doc = {
                    "_id": str(uuid.uuid4()),  # Generate new MongoDB ObjectId
                    "postgres_id": str(row.id),  # Keep reference to original ID
                    "user_id": row.user_id,
                    "document_name": row.document_name,
                    "chunk_index": row.chunk_index,
                    "text_chunk": row.text_chunk,
                    "chunk_size": row.chunk_size,
                    "token_count": len(row.text_chunk.split()),  # Estimate token count
                    "created_at": row.created_at,
                    "metadata": row.metadata or {},
                    "migrated_at": datetime.utcnow()
                }
                
                chunks_collection.insert_one(chunk_doc)
                migrated_count += 1
                
                if migrated_count % 100 == 0:
                    logger.info(f"Migrated {migrated_count} chunks...")
            
            logger.info(f"Successfully migrated {migrated_count} document chunks to MongoDB")
            return migrated_count
            
        except Exception as e:
            logger.error(f"Failed to migrate document chunks: {e}")
            raise
    
    def migrate_embeddings(self):
        """Migrate embeddings from PostgreSQL to Qdrant"""
        try:
            Session = sessionmaker(bind=self.postgres_engine)
            session = Session()
            
            # Get all embeddings from PostgreSQL
            query = text("""
                SELECT 
                    e.id,
                    e.chunk_id,
                    e.user_id,
                    e.document_name,
                    e.embedding_vector,
                    e.embedding_dimension,
                    e.created_at,
                    dc.text_chunk,
                    dc.chunk_index,
                    dc.chunk_size
                FROM embeddings e
                JOIN document_chunks dc ON e.chunk_id = dc.id
                ORDER BY e.user_id, e.document_name, e.chunk_index
            """)
            
            result = session.execute(query).fetchall()
            logger.info(f"Found {len(result)} embeddings to migrate")
            
            # Ensure Qdrant collection exists
            collection_name = "qa_bot_embeddings"
            try:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {collection_name}")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info(f"Qdrant collection {collection_name} already exists")
                else:
                    raise
            
            # Migrate embeddings to Qdrant
            points = []
            migrated_count = 0
            
            for row in result:
                point_id = str(uuid.uuid4())
                
                payload = {
                    "postgres_id": str(row.id),
                    "chunk_id": str(row.chunk_id),
                    "user_id": row.user_id,
                    "document_name": row.document_name,
                    "text_chunk": row.text_chunk,
                    "chunk_index": row.chunk_index,
                    "chunk_size": row.chunk_size,
                    "created_at": row.created_at.isoformat(),
                    "migrated_at": datetime.utcnow().isoformat()
                }
                
                point = PointStruct(
                    id=point_id,
                    vector=row.embedding_vector,  # Should be a list of floats
                    payload=payload
                )
                points.append(point)
                
                # Insert in batches
                if len(points) >= 100:
                    self.qdrant_client.upsert(
                        collection_name=collection_name,
                        points=points
                    )
                    migrated_count += len(points)
                    points = []
                    logger.info(f"Migrated {migrated_count} embeddings...")
            
            # Insert remaining points
            if points:
                self.qdrant_client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                migrated_count += len(points)
            
            logger.info(f"Successfully migrated {migrated_count} embeddings to Qdrant")
            return migrated_count
            
        except Exception as e:
            logger.error(f"Failed to migrate embeddings: {e}")
            raise
    
    def create_mongodb_indexes(self):
        """Create necessary indexes in MongoDB"""
        try:
            mongodb_db = self.mongodb_client["qa_bot"]
            chunks_collection = mongodb_db["chunks"]
            
            # Create indexes
            chunks_collection.create_index("user_id")
            chunks_collection.create_index("document_name")
            chunks_collection.create_index("chunk_index")
            chunks_collection.create_index([("user_id", 1), ("document_name", 1)])
            chunks_collection.create_index("postgres_id")
            
            logger.info("Created MongoDB indexes successfully")
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB indexes: {e}")
            raise
    
    def verify_migration(self):
        """Verify the migration was successful"""
        try:
            # Check PostgreSQL counts
            Session = sessionmaker(bind=self.postgres_engine)
            session = Session()
            
            postgres_chunks = session.execute(text("SELECT COUNT(*) FROM document_chunks")).fetchone()[0]
            postgres_embeddings = session.execute(text("SELECT COUNT(*) FROM embeddings")).fetchone()[0]
            
            # Check MongoDB counts
            mongodb_db = self.mongodb_client["qa_bot"]
            mongodb_chunks = mongodb_db["chunks"].count_documents({})
            
            # Check Qdrant counts
            collection_info = self.qdrant_client.get_collection("qa_bot_embeddings")
            qdrant_embeddings = collection_info.points_count
            
            logger.info("Migration verification:")
            logger.info(f"PostgreSQL chunks: {postgres_chunks}")
            logger.info(f"MongoDB chunks: {mongodb_chunks}")
            logger.info(f"PostgreSQL embeddings: {postgres_embeddings}")
            logger.info(f"Qdrant embeddings: {qdrant_embeddings}")
            
            if mongodb_chunks == postgres_chunks and qdrant_embeddings == postgres_embeddings:
                logger.info("✅ Migration verification successful!")
                return True
            else:
                logger.warning("⚠️ Migration verification failed - counts don't match")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify migration: {e}")
            return False
    
    def run_migration(self):
        """Run the complete migration process"""
        logger.info("Starting data migration from PostgreSQL to MongoDB + Qdrant")
        
        # Connect to all databases
        if not self.connect_postgres():
            return False
        if not self.connect_mongodb():
            return False
        if not self.connect_qdrant():
            return False
        
        try:
            # Run migration steps
            logger.info("Step 1: Migrating document chunks...")
            chunks_migrated = self.migrate_document_chunks()
            
            logger.info("Step 2: Migrating embeddings...")
            embeddings_migrated = self.migrate_embeddings()
            
            logger.info("Step 3: Creating MongoDB indexes...")
            self.create_mongodb_indexes()
            
            logger.info("Step 4: Verifying migration...")
            verification_success = self.verify_migration()
            
            if verification_success:
                logger.info("🎉 Migration completed successfully!")
                logger.info(f"Migrated {chunks_migrated} chunks and {embeddings_migrated} embeddings")
            else:
                logger.error("❌ Migration verification failed")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        finally:
            # Close connections
            if self.postgres_engine:
                self.postgres_engine.dispose()
            if self.mongodb_client:
                self.mongodb_client.close()

def main():
    """Main function to run the migration"""
    migration = DataMigration()
    success = migration.run_migration()
    
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
