"""
Vector store service for managing embeddings in PostgreSQL database
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from app.models.document import DocumentChunk, QueryResult
from app.models.database import DocumentChunk as DBDocumentChunk, Embedding as DBEmbedding, QueryLog as DBQueryLog
from app.database import get_db

logger = logging.getLogger(__name__)

class VectorStore:
    """Service for managing vector storage using PostgreSQL"""
    
    def __init__(self):
        """Initialize the vector store"""
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        logger.info("Initialized PostgreSQL vector store")
    
    def add_embeddings(self, embeddings: np.ndarray, chunks: List[DocumentChunk]) -> None:
        """
        Add embeddings and metadata to the vector store
        
        Args:
            embeddings: numpy array of embeddings with shape (n_chunks, embedding_dim)
            chunks: List of DocumentChunk objects with metadata
        """
        if len(embeddings) != len(chunks):
            raise ValueError("Number of embeddings must match number of chunks")
        
        db = next(get_db())
        try:
            for embedding, chunk in zip(embeddings, chunks):
                # Create document chunk record
                db_chunk = DBDocumentChunk(
                    user_id=chunk.user_id,
                    document_name=chunk.document_name,
                    chunk_index=chunk.chunk_index,
                    text_chunk=chunk.text_chunk,
                    chunk_size=chunk.chunk_size,
                    created_at=chunk.created_at,
                    metadata=chunk.metadata
                )
                db.add(db_chunk)
                db.flush()  # Get the ID
                
                # Create embedding record
                db_embedding = DBEmbedding(
                    chunk_id=db_chunk.id,
                    user_id=chunk.user_id,
                    document_name=chunk.document_name,
                    embedding_vector=embedding.tolist(),  # Convert numpy array to list
                    embedding_dimension=self.embedding_dim
                )
                db.add(db_embedding)
            
            db.commit()
            logger.info(f"Added {len(chunks)} embeddings to PostgreSQL vector store")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add embeddings: {e}")
            raise
        finally:
            db.close()
    
    def search(self, query_embedding: np.ndarray, user_id: str, top_k: int = 5,
               similarity_threshold: float = 0.3) -> List[QueryResult]:
        """
        Search for similar embeddings using PostgreSQL vector operations
        
        Args:
            query_embedding: Query embedding vector
            user_id: User ID to filter results
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score threshold
            
        Returns:
            List of QueryResult objects
        """
        db = next(get_db())
        try:
            # Convert query embedding to list for PostgreSQL
            query_vector = query_embedding.tolist()
            
            # Use PostgreSQL's cosine similarity operator
            # We'll use the <-> operator for cosine distance (1 - cosine similarity)
            query = text("""
                SELECT 
                    dc.text_chunk,
                    dc.document_name,
                    dc.chunk_index,
                    dc.metadata,
                    (1 - (e.embedding_vector <-> :query_vector)) as similarity_score
                FROM embeddings e
                JOIN document_chunks dc ON e.chunk_id = dc.id
                WHERE e.user_id = :user_id
                AND (1 - (e.embedding_vector <-> :query_vector)) >= :threshold
                ORDER BY e.embedding_vector <-> :query_vector
                LIMIT :top_k
            """)
            
            result = db.execute(query, {
                'query_vector': query_vector,
                'user_id': user_id,
                'threshold': similarity_threshold,
                'top_k': top_k
            })
            
            results = []
            for row in result:
                result_obj = QueryResult(
                    text_chunk=row.text_chunk,
                    document_name=row.document_name,
                    chunk_index=row.chunk_index,
                    similarity_score=float(row.similarity_score),
                    metadata=row.metadata
                )
                results.append(result_obj)
            
            logger.info(f"Found {len(results)} results for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search embeddings: {e}")
            raise
        finally:
            db.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        db = next(get_db())
        try:
            # Get total embeddings count
            total_embeddings = db.query(DBEmbedding).count()
            
            # Get unique users
            users = db.query(DBEmbedding.user_id).distinct().all()
            user_list = [user[0] for user in users]
            
            # Get unique documents
            documents = db.query(DBEmbedding.document_name).distinct().all()
            document_list = [doc[0] for doc in documents]
            
            return {
                'total_vectors': total_embeddings,
                'embedding_dimension': self.embedding_dim,
                'users': user_list,
                'documents': document_list
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                'total_vectors': 0,
                'embedding_dimension': self.embedding_dim,
                'users': [],
                'documents': []
            }
        finally:
            db.close()
    
    def clear_user_data(self, user_id: str) -> int:
        """
        Clear all data for a specific user
        
        Args:
            user_id: User ID to clear data for
            
        Returns:
            Number of vectors removed
        """
        db = next(get_db())
        try:
            # Count embeddings before deletion
            count_before = db.query(DBEmbedding).filter(DBEmbedding.user_id == user_id).count()
            
            # Delete embeddings first (due to foreign key constraint)
            db.query(DBEmbedding).filter(DBEmbedding.user_id == user_id).delete()
            
            # Delete document chunks
            db.query(DBDocumentChunk).filter(DBDocumentChunk.user_id == user_id).delete()
            
            db.commit()
            
            logger.info(f"Cleared {count_before} vectors for user {user_id}")
            return count_before
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to clear user data: {e}")
            raise
        finally:
            db.close()
    
    def log_query(self, user_id: str, query_text: str, query_embedding: np.ndarray, 
                  results_count: int, processing_time: float) -> None:
        """
        Log a query for analytics
        
        Args:
            user_id: User ID
            query_text: Query text
            query_embedding: Query embedding vector
            results_count: Number of results returned
            processing_time: Time taken to process query
        """
        db = next(get_db())
        try:
            query_log = DBQueryLog(
                user_id=user_id,
                query_text=query_text,
                query_embedding=query_embedding.tolist(),
                results_count=results_count,
                processing_time=processing_time
            )
            db.add(query_log)
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to log query: {e}")
        finally:
            db.close()
