from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import api, documents
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QA Bot API with Embeddings Database",
    version="1.0.0",
    description="A full-stack Q&A application with local vector embeddings database"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
embedding_service = EmbeddingService()
vector_store = VectorStore()

# Make services available to routers
app.embedding_service = embedding_service
app.vector_store = vector_store

# Include routers
app.include_router(api.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "QA Bot API with Embeddings Database is running!",
        "version": "1.0.0",
        "features": [
            "Document upload and processing",
            "Vector embeddings with FAISS",
            "Semantic search",
            "Q&A functionality"
        ]
    }

@app.get("/health")
async def health_check():
    stats = vector_store.get_stats()
    return {
        "status": "healthy",
        "vector_store": {
            "total_vectors": stats["total_vectors"],
            "embedding_dimension": stats["embedding_dimension"],
            "users": len(stats["users"]),
            "documents": len(stats["documents"])
        }
    }

@app.get("/stats")
async def get_stats():
    """Get detailed statistics about the system"""
    stats = vector_store.get_stats()
    return {
        "vector_store": stats,
        "embedding_model": embedding_service.model_name,
        "embedding_dimension": embedding_service.get_embedding_dimension()
    }