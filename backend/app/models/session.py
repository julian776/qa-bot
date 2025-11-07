"""
Session and Message models for chat history
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Message model for chat history"""
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    language: Optional[str] = None
    sources: Optional[List[dict]] = None  # List of source chunks used
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    """Session model for chat sessions"""
    session_id: str
    user_id: str
    title: Optional[str] = None  # Custom session title (default: auto-generated)
    document_ids: List[str] = Field(default_factory=list)  # Linked document IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0


# API Models
class QueryWithSessionRequest(BaseModel):
    """Query request with session support"""
    prompt: str
    session_id: str
    user_id: Optional[str] = "default_user"
    top_k: int = 10
    similarity_threshold: float = 0.1  # Lowered from 0.7 - OpenAI embeddings typically score 0.3-0.5 for relevant matches
    language: Optional[str] = None  # Optional language filter


class QueryWithSessionResponse(BaseModel):
    """Query response with LLM answer and session"""
    session_id: str
    prompt: str
    answer: str
    language: Optional[str] = None
    sources: List[dict]
    processing_time: float


class SessionCreateRequest(BaseModel):
    """Request to create a new session"""
    user_id: str = "default_user"


class SessionCreateResponse(BaseModel):
    """Response with new session ID"""
    session_id: str
    user_id: str
    created_at: datetime


class MessageListResponse(BaseModel):
    """Response with session messages"""
    session_id: str
    messages: List[dict]
    total_messages: int


class SessionUpdateTitleRequest(BaseModel):
    """Request to update session title"""
    title: str


class SessionListResponse(BaseModel):
    """Response with user sessions"""
    sessions: List[dict]
    total_sessions: int


class SessionDocumentsResponse(BaseModel):
    """Response with documents linked to a session"""
    session_id: str
    documents: List[dict]
    total_documents: int
