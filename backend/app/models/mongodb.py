"""
MongoDB models for QA Bot application
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

# Removed PyObjectId - not needed for modern Pydantic v2

class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(BaseModel):
    """Document model"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: DocumentStatus = DocumentStatus.UPLOADED
    total_chunks: int = 0
    total_tokens: int = 0
    processing_time: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DocumentChunk(BaseModel):
    """Document chunk model"""
    id: Optional[str] = Field(default=None, alias="_id")
    document_id: str
    user_id: str
    chunk_index: int
    text_chunk: str
    chunk_size: int
    token_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Query(BaseModel):
    """Query model for storing user queries"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    query_text: str
    results_count: int = 0
    processing_time: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(BaseModel):
    """User model"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str = Field(unique=True)
    username: str
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    settings: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Request/Response models
class DocumentUploadRequest(BaseModel):
    """Document upload request model"""
    user_id: str
    filename: str
    file_type: str
    file_size: int

class DocumentUploadResponse(BaseModel):
    """Document upload response model"""
    document_id: str
    user_id: str
    filename: str
    status: str
    total_chunks: int
    total_tokens: int
    processing_time: float

class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    user_id: str
    top_k: int = 5
    similarity_threshold: float = 0.7

class QueryResult(BaseModel):
    """Query result model"""
    text_chunk: str
    document_name: str
    chunk_index: int
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    """Query response model"""
    query: str
    user_id: str
    results: List[QueryResult]
    total_results: int
    processing_time: float

class UserStats(BaseModel):
    """User statistics model"""
    user_id: str
    total_documents: int
    total_chunks: int
    total_queries: int
    total_tokens: int
    created_at: datetime
