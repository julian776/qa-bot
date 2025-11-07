"""
Document router for handling file uploads and vector queries
"""
import os
import tempfile
import time
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging

from app.models.document import (
    DocumentUpload, QueryRequest, QueryResponse, QueryResult
)
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_store import QdrantVectorStore

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize document processor
document_processor = DocumentProcessor()

def get_embedding_service() -> EmbeddingService:
    """Dependency to get embedding service"""
    from app.main import app
    return app.embedding_service

def get_vector_store() -> QdrantVectorStore:
    """Dependency to get vector store"""
    from app.main import app
    return app.vector_store

@router.post("/upload", response_model=DocumentUpload)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: QdrantVectorStore = Depends(get_vector_store)
):
    """
    Upload a document and process it into embeddings
    
    Args:
        file: Uploaded file (supports .txt and .pdf)
        user_id: User ID for the document
        embedding_service: Embedding service dependency
        vector_store: Vector store dependency
        
    Returns:
        DocumentUpload response with processing information
    """
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.txt', '.pdf']:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Only .txt and .pdf files are supported."
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the document (returns chunks and detected language)
            logger.info(f"Processing document {file.filename} for user {user_id}")
            chunks, language = await document_processor.process_file(
                temp_file_path, user_id, file.filename
            )

            if not chunks:
                raise HTTPException(status_code=400, detail="No content found in document")

            logger.info(f"Detected language: {language} for document {file.filename}")

            # Generate embeddings for chunks
            texts = [chunk.text_chunk for chunk in chunks]
            embeddings = embedding_service.generate_embeddings(texts)

            # Store embeddings and metadata in Qdrant
            await vector_store.add_embeddings(embeddings, chunks)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Get chunk statistics
            stats = document_processor.get_chunk_stats(chunks)
            
            logger.info(f"Successfully processed {file.filename} into {len(chunks)} chunks")
            
            return DocumentUpload(
                user_id=user_id,
                document_name=file.filename,
                total_chunks=len(chunks),
                total_tokens=stats['total_tokens'],
                processing_time=processing_time,
                status="success"
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: QdrantVectorStore = Depends(get_vector_store)
):
    """
    Query documents using semantic search
    
    Args:
        request: Query request with query text, user_id, and search parameters
        embedding_service: Embedding service dependency
        vector_store: Vector store dependency
        
    Returns:
        QueryResponse with matching document chunks
    """
    start_time = time.time()
    
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Generate embedding for query
        query_embedding = embedding_service.generate_single_embedding(request.query)
        
        # Search for similar documents
        results = vector_store.search(
            query_embedding=query_embedding,
            user_id=request.user_id,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        logger.info(f"Query '{request.query}' returned {len(results)} results for user {request.user_id}")
        
        return QueryResponse(
            query=request.query,
            user_id=request.user_id,
            results=results,
            total_results=len(results),
            processing_time=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/documents/{user_id}")
async def get_user_documents(
    user_id: str,
    vector_store: QdrantVectorStore = Depends(get_vector_store)
):
    """
    Get all documents for a specific user
    
    Args:
        user_id: User ID to get documents for
        vector_store: Vector store dependency
        
    Returns:
        List of documents with metadata
    """
    try:
        stats = vector_store.get_stats()
        
        # Filter documents by user_id
        user_documents = []
        for metadata in vector_store.metadata:
            if metadata['user_id'] == user_id:
                # Check if document is already in our list
                doc_name = metadata['document_name']
                if not any(doc['document_name'] == doc_name for doc in user_documents):
                    user_documents.append({
                        'document_name': doc_name,
                        'user_id': user_id,
                        'created_at': metadata['created_at']
                    })
        
        return {
            "user_id": user_id,
            "documents": user_documents,
            "total_documents": len(user_documents)
        }
    
    except Exception as e:
        logger.error(f"Error getting documents for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")

@router.delete("/documents/{user_id}")
async def clear_user_documents(
    user_id: str,
    vector_store: QdrantVectorStore = Depends(get_vector_store)
):
    """
    Clear all documents for a specific user
    
    Args:
        user_id: User ID to clear documents for
        vector_store: Vector store dependency
        
    Returns:
        Confirmation of deletion
    """
    try:
        removed_count = vector_store.clear_user_data(user_id)
        
        logger.info(f"Cleared {removed_count} vectors for user {user_id}")
        
        return {
            "user_id": user_id,
            "removed_vectors": removed_count,
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Error clearing documents for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")

@router.get("/search/{user_id}")
async def search_user_documents(
    user_id: str,
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.7,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: QdrantVectorStore = Depends(get_vector_store)
):
    """
    Search documents for a specific user (GET endpoint for easy testing)
    
    Args:
        user_id: User ID to search documents for
        query: Search query
        top_k: Number of results to return
        similarity_threshold: Minimum similarity score
        embedding_service: Embedding service dependency
        vector_store: Vector store dependency
        
    Returns:
        Search results
    """
    request = QueryRequest(
        query=query,
        user_id=user_id,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    
    return await query_documents(request, embedding_service, vector_store)
