"""
Embedding service for generating and managing document embeddings using OpenAI API
"""
import numpy as np
import openai
import os
from typing import List, Tuple
import logging
import asyncio
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using OpenAI API"""
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize the embedding service
        
        Args:
            model_name: Name of the OpenAI embedding model to use
        """
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_dim = 1536  # text-embedding-3-small has 1536 dimensions
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        logger.info(f"Initialized embedding service with model: {model_name}")
    
    async def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts using OpenAI API
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        try:
            if not texts:
                return np.array([])
            
            logger.info(f"Generating embeddings for {len(texts)} texts using OpenAI API")
            
            # Process texts in batches to avoid rate limits
            batch_size = 100  # OpenAI allows up to 2048 inputs per request
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.model_name,
                    input=batch_texts
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
            
            embeddings_array = np.array(all_embeddings, dtype=np.float32)
            logger.info(f"Generated embeddings with shape: {embeddings_array.shape}")
            return embeddings_array
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def generate_single_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of embedding with shape (embedding_dim,)
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model"""
        return self.embedding_dim
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        # Normalize embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    async def test_connection(self) -> bool:
        """
        Test the OpenAI API connection
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_embedding = await self.generate_single_embedding("test")
            return len(test_embedding) == self.embedding_dim
        except Exception as e:
            logger.error(f"OpenAI API connection test failed: {e}")
            return False
