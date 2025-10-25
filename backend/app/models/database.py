"""
Database models for QA Bot application
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from app.database import Base
import uuid

class DocumentChunk(Base):
    """Database model for document chunks"""
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    document_name = Column(String(500), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    text_chunk = Column(Text, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Composite index for efficient querying
    __table_args__ = (
        Index('idx_user_document', 'user_id', 'document_name'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )

class Embedding(Base):
    """Database model for storing embeddings"""
    __tablename__ = "embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    document_name = Column(String(500), nullable=False, index=True)
    embedding_vector = Column(ARRAY(Float), nullable=False)  # PostgreSQL array of floats
    embedding_dimension = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Composite index for efficient querying
    __table_args__ = (
        Index('idx_user_document_embedding', 'user_id', 'document_name'),
        Index('idx_chunk_embedding', 'chunk_id'),
    )

class QueryLog(Base):
    """Database model for logging queries"""
    __tablename__ = "query_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    query_embedding = Column(ARRAY(Float), nullable=True)
    results_count = Column(Integer, nullable=False, default=0)
    processing_time = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Index for efficient querying
    __table_args__ = (
        Index('idx_user_query_time', 'user_id', 'created_at'),
    )
