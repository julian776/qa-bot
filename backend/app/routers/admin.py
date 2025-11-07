"""
Admin router for administrative operations (clear data, etc.)
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from app.services.qdrant_store import QdrantVectorStore
from app.database import db_config

logger = logging.getLogger(__name__)

router = APIRouter()


def get_vector_store() -> QdrantVectorStore:
    """Dependency to get vector store"""
    from app.main import app
    return app.vector_store


@router.post("/admin/clear")
async def clear_all_data(vector_store: QdrantVectorStore = Depends(get_vector_store)):
    """
    Clear all data from the system (Qdrant + MongoDB)

    WARNING: This will delete ALL data including:
    - All vector embeddings
    - All documents
    - All chunks
    - All sessions
    - All messages

    This endpoint is intended for testing and development only.

    Returns:
        Confirmation with counts of deleted items
    """
    try:
        db = db_config.get_database()

        # Clear MongoDB collections
        documents_result = await db.documents.delete_many({})
        chunks_result = await db.chunks.delete_many({})
        sessions_result = await db.sessions.delete_many({})
        messages_result = await db.messages.delete_many({})
        queries_result = await db.queries.delete_many({})

        # Clear Qdrant collection by recreating it
        try:
            vector_store.client.delete_collection(vector_store.collection_name)
            vector_store._ensure_collection_exists()
            logger.info(f"Recreated Qdrant collection: {vector_store.collection_name}")
        except Exception as e:
            logger.warning(f"Error clearing Qdrant collection: {e}")

        logger.info("Cleared all data from the system")

        return {
            "status": "success",
            "message": "All data cleared successfully",
            "deleted": {
                "documents": documents_result.deleted_count,
                "chunks": chunks_result.deleted_count,
                "sessions": sessions_result.deleted_count,
                "messages": messages_result.deleted_count,
                "queries": queries_result.deleted_count,
                "qdrant_vectors": "all (collection recreated)"
            }
        }

    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")


@router.post("/admin/clear/user/{user_id}")
async def clear_user_data(
    user_id: str,
    vector_store: QdrantVectorStore = Depends(get_vector_store)
):
    """
    Clear all data for a specific user

    Args:
        user_id: User ID to clear data for

    Returns:
        Confirmation with counts of deleted items
    """
    try:
        db = db_config.get_database()

        # Clear MongoDB collections for this user
        documents_result = await db.documents.delete_many({"user_id": user_id})
        chunks_result = await db.chunks.delete_many({"user_id": user_id})
        sessions_result = await db.sessions.delete_many({"user_id": user_id})

        # Get session IDs for this user to delete messages
        session_ids = []
        async for session in db.sessions.find({"user_id": user_id}):
            session_ids.append(session['session_id'])

        messages_result = await db.messages.delete_many({"session_id": {"$in": session_ids}})
        queries_result = await db.queries.delete_many({"user_id": user_id})

        # Clear Qdrant vectors for this user
        vector_store.clear_user_data(user_id)

        logger.info(f"Cleared all data for user {user_id}")

        return {
            "status": "success",
            "message": f"All data cleared for user {user_id}",
            "user_id": user_id,
            "deleted": {
                "documents": documents_result.deleted_count,
                "chunks": chunks_result.deleted_count,
                "sessions": sessions_result.deleted_count,
                "messages": messages_result.deleted_count,
                "queries": queries_result.deleted_count,
                "qdrant_vectors": "cleared"
            }
        }

    except Exception as e:
        logger.error(f"Error clearing data for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing user data: {str(e)}")


@router.get("/admin/stats")
async def get_system_stats(vector_store: QdrantVectorStore = Depends(get_vector_store)):
    """
    Get system statistics

    Returns:
        System statistics including counts of documents, sessions, messages, etc.
    """
    try:
        db = db_config.get_database()

        # Get counts from MongoDB
        documents_count = await db.documents.count_documents({})
        chunks_count = await db.chunks.count_documents({})
        sessions_count = await db.sessions.count_documents({})
        messages_count = await db.messages.count_documents({})
        queries_count = await db.queries.count_documents({})

        # Get Qdrant stats
        qdrant_stats = vector_store.get_stats()

        return {
            "mongodb": {
                "documents": documents_count,
                "chunks": chunks_count,
                "sessions": sessions_count,
                "messages": messages_count,
                "queries": queries_count
            },
            "qdrant": qdrant_stats
        }

    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")
