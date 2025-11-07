from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentChunk(BaseModel):
    """Model for a document chunk with metadata"""
    user_id: str
    document_name: str
    chunk_index: int
    text_chunk: str
    chunk_size: int
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class DocumentUpload(BaseModel):
    """Model for document upload response"""
    user_id: str
    document_name: str
    total_chunks: int
    total_tokens: int
    processing_time: float
    status: str

class QueryRequest(BaseModel):
    """Model for query request"""
    query: str
    user_id: str
    top_k: int = 5
    similarity_threshold: float = 0.3  # Lowered from 0.7 for better results with OpenAI embeddings

class QueryResult(BaseModel):
    """Model for query result"""
    text_chunk: str
    document_name: str
    chunk_index: int
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    """Model for query response"""
    query: str
    user_id: str
    results: List[QueryResult]
    total_results: int
    processing_time: float
