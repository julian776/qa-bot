from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import api, documents
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_store import QdrantVectorStore
from app.database import db_config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QA Bot API with MongoDB and Qdrant",
    version="2.0.0",
    description="A production-ready Q&A application with MongoDB, Qdrant vector database, and OpenAI embeddings"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
embedding_service = None
vector_store = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global embedding_service, vector_store
    
    try:
        # Connect to MongoDB
        if not await db_config.connect():
            raise Exception("MongoDB connection failed")
        
        # Initialize services
        embedding_service = EmbeddingService()
        vector_store = QdrantVectorStore()
        
        # Test connections
        if not await embedding_service.test_connection():
            raise Exception("OpenAI API connection failed")
        
        if not vector_store.test_connection():
            raise Exception("Qdrant connection failed")
        
        # Make services available to routers
        app.embedding_service = embedding_service
        app.vector_store = vector_store
        app.db_config = db_config
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if db_config.client:
        await db_config.disconnect()

# Include routers
app.include_router(api.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "QA Bot API with MongoDB and Qdrant is running!",
        "version": "2.0.0",
        "features": [
            "Document upload and processing",
            "MongoDB for metadata storage",
            "Qdrant vector database for embeddings",
            "OpenAI embeddings API",
            "Semantic search",
            "Q&A functionality"
        ]
    }

@app.get("/health")
async def health_check():
    if not vector_store:
        return {"status": "unhealthy", "error": "Services not initialized"}
    
    stats = vector_store.get_stats()
    return {
        "status": "healthy",
        "vector_store": {
            "total_vectors": stats["total_vectors"],
            "embedding_dimension": stats["embedding_dimension"],
            "collection_name": stats["collection_name"]
        },
        "mongodb": {
            "connected": db_config.client is not None
        }
    }

@app.get("/stats")
async def get_stats():
    """Get detailed statistics about the system"""
    if not vector_store:
        return {"error": "Services not initialized"}
    
    stats = vector_store.get_stats()
    return {
        "vector_store": stats,
        "embedding_model": embedding_service.model_name if embedding_service else "Not initialized",
        "embedding_dimension": embedding_service.get_embedding_dimension() if embedding_service else 0,
        "mongodb_connected": db_config.client is not None
    }