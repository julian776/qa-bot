"""
Qdrant vector store service for managing embeddings and similarity search
"""
import numpy as np
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import uuid

from app.models.mongodb import DocumentChunk, QueryResult

logger = logging.getLogger(__name__)

class QdrantVectorStore:
    """Service for managing vector storage using Qdrant"""
    
    def __init__(self, collection_name: str = "qa_bot_embeddings"):
        """
        Initialize the Qdrant vector store
        
        Args:
            collection_name: Name of the Qdrant collection
        """
        self.collection_name = collection_name
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.embedding_dim = 1536  # OpenAI text-embedding-3-small dimension
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Qdrant client"""
        try:
            self.client = QdrantClient(url=self.qdrant_url)
            logger.info(f"Connected to Qdrant at {self.qdrant_url}")
            self._ensure_collection_exists()
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists, create if it doesn't"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            raise
    
    async def add_embeddings(self, embeddings: np.ndarray, chunks: List[DocumentChunk]) -> None:
        """
        Add embeddings and metadata to the vector store
        
        Args:
            embeddings: numpy array of embeddings with shape (n_chunks, embedding_dim)
            chunks: List of DocumentChunk objects with metadata
        """
        if len(embeddings) != len(chunks):
            raise ValueError("Number of embeddings must match number of chunks")
        
        try:
            points = []
            for i, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
                point_id = str(uuid.uuid4())
                
                # Create payload with metadata
                payload = {
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "user_id": chunk.user_id,
                    "chunk_index": chunk.chunk_index,
                    "text_chunk": chunk.text_chunk,
                    "chunk_size": chunk.chunk_size,
                    "token_count": chunk.token_count,
                    "created_at": chunk.created_at.isoformat(),
                    "metadata": chunk.metadata or {}
                }
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload=payload
                )
                points.append(point)
            
            # Insert points into Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(chunks)} embeddings to Qdrant vector store")
            
        except Exception as e:
            logger.error(f"Failed to add embeddings to Qdrant: {e}")
            raise
    
    async def search(self, query_embedding: np.ndarray, user_id: str, top_k: int = 5,
                   similarity_threshold: float = 0.7, language: Optional[str] = None) -> List[QueryResult]:
        """
        Search for similar embeddings using Qdrant

        Args:
            query_embedding: Query embedding vector
            user_id: User ID to filter results
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score threshold
            language: Optional language filter ('en' or 'es')

        Returns:
            List of QueryResult objects
        """
        try:
            # Build filter conditions
            filter_conditions = [
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=user_id)
                )
            ]

            # Add language filter if specified
            if language:
                filter_conditions.append(
                    models.FieldCondition(
                        key="metadata.language",
                        match=models.MatchValue(value=language)
                    )
                )

            # Search in Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                query_filter=models.Filter(must=filter_conditions),
                limit=top_k,
                score_threshold=similarity_threshold
            )
            
            results = []
            for hit in search_result:
                payload = hit.payload
                
                result = QueryResult(
                    text_chunk=payload["text_chunk"],
                    document_name=payload.get("document_name", "Unknown"),
                    chunk_index=payload["chunk_index"],
                    similarity_score=float(hit.score),
                    metadata=payload.get("metadata", {})
                )
                results.append(result)
            
            logger.info(f"Found {len(results)} results for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search embeddings in Qdrant: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            # Get unique users and documents
            users = set()
            documents = set()
            
            # This is a simplified approach - in production you might want to maintain separate metadata
            # For now, we'll return basic collection stats
            return {
                'total_vectors': collection_info.points_count,
                'embedding_dimension': self.embedding_dim,
                'collection_name': self.collection_name,
                'users': list(users),
                'documents': list(documents)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Qdrant stats: {e}")
            return {
                'total_vectors': 0,
                'embedding_dimension': self.embedding_dim,
                'collection_name': self.collection_name,
                'users': [],
                'documents': []
            }
    
    def clear_user_data(self, user_id: str) -> int:
        """
        Clear all data for a specific user
        
        Args:
            user_id: User ID to clear data for
            
        Returns:
            Number of vectors removed
        """
        try:
            # Delete points matching the user_id
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="user_id",
                                match=models.MatchValue(value=user_id)
                            )
                        ]
                    )
                )
            )
            
            logger.info(f"Cleared data for user {user_id} from Qdrant")
            return 0  # Qdrant doesn't return count, so we return 0
            
        except Exception as e:
            logger.error(f"Failed to clear user data from Qdrant: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test Qdrant connection
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            collections = self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant connection test failed: {e}")
            return False
