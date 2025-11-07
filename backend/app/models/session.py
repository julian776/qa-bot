"""
Session and Message models for chat history
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Message(BaseModel):
    """Message model for chat history"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    language: Optional[str] = None
    sources: Optional[List[dict]] = None  # List of source chunks used
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Session(BaseModel):
    """Session model for chat sessions"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    session_id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# API Models
class QueryWithSessionRequest(BaseModel):
    """Query request with session support"""
    prompt: str
    session_id: str
    user_id: Optional[str] = "default_user"
    top_k: int = 5
    similarity_threshold: float = 0.7
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
