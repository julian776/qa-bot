"""
Session router for handling chat sessions with LLM responses
"""
import time
import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.session import (
    QueryWithSessionRequest, QueryWithSessionResponse,
    SessionCreateRequest, SessionCreateResponse,
    MessageListResponse, Session, Message
)
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_store import QdrantVectorStore
from app.services.llm_service import LLMService
from app.services.language_detector import LanguageDetector
from app.database import db_config

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
language_detector = LanguageDetector()


def get_embedding_service() -> EmbeddingService:
    """Dependency to get embedding service"""
    from app.main import app
    return app.embedding_service


def get_vector_store() -> QdrantVectorStore:
    """Dependency to get vector store"""
    from app.main import app
    return app.vector_store


def get_llm_service() -> LLMService:
    """Dependency to get LLM service"""
    from app.main import app
    return app.llm_service


@router.post("/session/create", response_model=SessionCreateResponse)
async def create_session(request: SessionCreateRequest):
    """
    Create a new chat session

    Args:
        request: Session creation request with user_id

    Returns:
        SessionCreateResponse with new session_id
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Create session document
        session = Session(
            session_id=session_id,
            user_id=request.user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            message_count=0
        )

        # Insert into MongoDB
        db = db_config.get_database()
        await db.sessions.insert_one(session.model_dump())

        logger.info(f"Created session {session_id} for user {request.user_id}")

        return SessionCreateResponse(
            session_id=session_id,
            user_id=request.user_id,
            created_at=session.created_at
        )

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.post("/query", response_model=QueryWithSessionResponse)
async def query_with_llm(
    request: QueryWithSessionRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: QdrantVectorStore = Depends(get_vector_store),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Query documents with LLM-powered response and save to session history

    Args:
        request: Query request with prompt, session_id, and optional filters
        embedding_service: Embedding service dependency
        vector_store: Vector store dependency
        llm_service: LLM service dependency

    Returns:
        QueryWithSessionResponse with LLM answer and sources
    """
    start_time = time.time()

    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        # Detect language of the prompt
        detected_language = language_detector.detect_language(request.prompt)
        language = request.language or detected_language
        logger.info(f"Query language: {language}")

        # Generate embedding for the prompt
        query_embedding = await embedding_service.generate_single_embedding(request.prompt)

        # Search for similar documents WITHOUT language filter (allows cross-language search)
        # This is important because embeddings can match semantically across languages
        search_results = await vector_store.search(
            query_embedding=query_embedding,
            user_id=request.user_id,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            language=None  # Don't filter by language - allow cross-language semantic search
        )

        # Convert search results to dict format for LLM
        sources = []
        for result in search_results:
            sources.append({
                'text_chunk': result.text_chunk,
                'document_name': result.document_name,
                'chunk_index': result.chunk_index,
                'score': result.similarity_score,
                'metadata': result.metadata
            })

        # Generate LLM response
        if sources:
            answer = llm_service.generate_response(
                prompt=request.prompt,
                context_chunks=sources,
                language=language
            )
        else:
            # No relevant documents found
            if language == 'es':
                answer = "Lo siento, no encontré información relevante en los documentos disponibles para responder tu pregunta."
            else:
                answer = "I'm sorry, I couldn't find relevant information in the available documents to answer your question."

        # Calculate processing time
        processing_time = time.time() - start_time

        # Save user message to MongoDB
        db = db_config.get_database()
        user_message = Message(
            session_id=request.session_id,
            role="user",
            content=request.prompt,
            language=language,
            created_at=datetime.utcnow()
        )
        await db.messages.insert_one(user_message.model_dump())

        # Save assistant message to MongoDB
        assistant_message = Message(
            session_id=request.session_id,
            role="assistant",
            content=answer,
            language=language,
            sources=sources,
            created_at=datetime.utcnow()
        )
        await db.messages.insert_one(assistant_message.model_dump())

        # Update session message count and updated_at
        await db.sessions.update_one(
            {"session_id": request.session_id},
            {
                "$inc": {"message_count": 2},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        logger.info(f"Query processed in {processing_time:.2f}s with {len(sources)} sources")

        return QueryWithSessionResponse(
            session_id=request.session_id,
            prompt=request.prompt,
            answer=answer,
            language=language,
            sources=sources,
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/session/{session_id}/messages", response_model=MessageListResponse)
async def get_session_messages(session_id: str):
    """
    Get all messages for a session

    Args:
        session_id: Session ID to retrieve messages for

    Returns:
        MessageListResponse with all messages in the session
    """
    try:
        db = db_config.get_database()

        # Get messages for this session
        messages_cursor = db.messages.find(
            {"session_id": session_id}
        ).sort("created_at", 1)

        messages = []
        async for msg in messages_cursor:
            messages.append({
                'role': msg['role'],
                'content': msg['content'],
                'language': msg.get('language'),
                'sources': msg.get('sources', []) if msg['role'] == 'assistant' else None,
                'created_at': msg['created_at'].isoformat()
            })

        logger.info(f"Retrieved {len(messages)} messages for session {session_id}")

        return MessageListResponse(
            session_id=session_id,
            messages=messages,
            total_messages=len(messages)
        )

    except Exception as e:
        logger.error(f"Error retrieving messages for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")


@router.get("/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """
    Get all sessions for a user

    Args:
        user_id: User ID to retrieve sessions for

    Returns:
        List of sessions with metadata
    """
    try:
        db = db_config.get_database()

        # Get sessions for this user
        sessions_cursor = db.sessions.find(
            {"user_id": user_id}
        ).sort("updated_at", -1)

        sessions = []
        async for session in sessions_cursor:
            sessions.append({
                'session_id': session['session_id'],
                'user_id': session['user_id'],
                'message_count': session['message_count'],
                'created_at': session['created_at'].isoformat(),
                'updated_at': session['updated_at'].isoformat()
            })

        logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")

        return {
            "user_id": user_id,
            "sessions": sessions,
            "total_sessions": len(sessions)
        }

    except Exception as e:
        logger.error(f"Error retrieving sessions for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")
