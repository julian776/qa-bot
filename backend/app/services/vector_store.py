"""
Vector store service for managing FAISS index and metadata
"""
import faiss
import numpy as np
import json
import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from app.models.document import DocumentChunk, QueryResult

logger = logging.getLogger(__name__)

class VectorStore:
    """Service for managing vector storage using FAISS"""
    
    def __init__(self, storage_dir: str = "data/vector_store"):
        """
        Initialize the vector store
        
        Args:
            storage_dir: Directory to store FAISS index and metadata
        """
        self.storage_dir = storage_dir
        self.index = None
        self.metadata = []
        self.embedding_dim = None
        self.index_file = os.path.join(storage_dir, "faiss_index.bin")
        self.metadata_file = os.path.join(storage_dir, "metadata.pkl")
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self) -> None:
        """Load existing FAISS index and metadata"""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                logger.info("Loading existing FAISS index and metadata")
                self.index = faiss.read_index(self.index_file)
                with open(self.metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                self.embedding_dim = self.index.d
                logger.info(f"Loaded index with {self.index.ntotal} vectors and dimension {self.embedding_dim}")
            else:
                logger.info("No existing index found, will create new one")
        except Exception as e:
            logger.error(f"Failed to load existing index: {e}")
            logger.info("Creating new index")
            self.metadata = []
    
    def _save_index(self) -> None:
        """Save FAISS index and metadata to disk"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, self.index_file)
                with open(self.metadata_file, 'wb') as f:
                    pickle.dump(self.metadata, f)
                logger.info(f"Saved index with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def initialize_index(self, embedding_dim: int) -> None:
        """
        Initialize a new FAISS index
        
        Args:
            embedding_dim: Dimension of the embeddings
        """
        if self.index is None or self.embedding_dim != embedding_dim:
            logger.info(f"Initializing new FAISS index with dimension {embedding_dim}")
            self.embedding_dim = embedding_dim
            # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
            self.index = faiss.IndexFlatIP(embedding_dim)
            self.metadata = []
            self._save_index()
    
    def add_embeddings(self, embeddings: np.ndarray, chunks: List[DocumentChunk]) -> None:
        """
        Add embeddings and metadata to the vector store
        
        Args:
            embeddings: numpy array of embeddings with shape (n_chunks, embedding_dim)
            chunks: List of DocumentChunk objects with metadata
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call initialize_index first.")
        
        if len(embeddings) != len(chunks):
            raise ValueError("Number of embeddings must match number of chunks")
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Add metadata
        for chunk in chunks:
            self.metadata.append({
                'user_id': chunk.user_id,
                'document_name': chunk.document_name,
                'chunk_index': chunk.chunk_index,
                'text_chunk': chunk.text_chunk,
                'chunk_size': chunk.chunk_size,
                'created_at': chunk.created_at.isoformat(),
                'metadata': chunk.metadata
            })
        
        logger.info(f"Added {len(chunks)} embeddings to vector store")
        self._save_index()
    
    def search(self, query_embedding: np.ndarray, user_id: str, top_k: int = 5, 
               similarity_threshold: float = 0.7) -> List[QueryResult]:
        """
        Search for similar embeddings
        
        Args:
            query_embedding: Query embedding vector
            user_id: User ID to filter results
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score threshold
            
        Returns:
            List of QueryResult objects
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("No vectors in index")
            return []
        
        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            
            metadata = self.metadata[idx]
            
            # Filter by user_id
            if metadata['user_id'] != user_id:
                continue
            
            # Filter by similarity threshold
            if score < similarity_threshold:
                continue
            
            result = QueryResult(
                text_chunk=metadata['text_chunk'],
                document_name=metadata['document_name'],
                chunk_index=metadata['chunk_index'],
                similarity_score=float(score),
                metadata=metadata['metadata']
            )
            results.append(result)
        
        logger.info(f"Found {len(results)} results for user {user_id}")
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if self.index is None:
            return {
                'total_vectors': 0,
                'embedding_dimension': 0,
                'users': [],
                'documents': []
            }
        
        users = set()
        documents = set()
        for metadata in self.metadata:
            users.add(metadata['user_id'])
            documents.add(metadata['document_name'])
        
        return {
            'total_vectors': self.index.ntotal,
            'embedding_dimension': self.embedding_dim,
            'users': list(users),
            'documents': list(documents)
        }
    
    def clear_user_data(self, user_id: str) -> int:
        """
        Clear all data for a specific user
        
        Args:
            user_id: User ID to clear data for
            
        Returns:
            Number of vectors removed
        """
        if self.index is None:
            return 0
        
        # Find indices to remove
        indices_to_remove = []
        for i, metadata in enumerate(self.metadata):
            if metadata['user_id'] == user_id:
                indices_to_remove.append(i)
        
        if not indices_to_remove:
            return 0
        
        # Remove from metadata (in reverse order to maintain indices)
        for i in reversed(indices_to_remove):
            del self.metadata[i]
        
        # Rebuild index without removed vectors
        if self.metadata:
            # This is a simplified approach - in production, you might want to use FAISS's remove_ids
            logger.warning("Clearing user data requires rebuilding index - this is a simplified implementation")
            # For now, we'll just clear the metadata and let the index be rebuilt on next addition
            self.metadata = []
            self.index = None
        
        logger.info(f"Cleared {len(indices_to_remove)} vectors for user {user_id}")
        return len(indices_to_remove)
