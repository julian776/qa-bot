"""
Embedding service for generating and managing document embeddings using Hugging Face API
"""
import numpy as np
import requests
import os
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using Hugging Face API"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding service
        
        Args:
            model_name: Name of the Hugging Face model to use
        """
        self.model_name = model_name
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.embedding_dim = 384  # all-MiniLM-L6-v2 has 384 dimensions
        
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable is required")
        
        logger.info(f"Initialized embedding service with model: {model_name}")
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts using Hugging Face API
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        try:
            if not texts:
                return np.array([])
            
            logger.info(f"Generating embeddings for {len(texts)} texts using Hugging Face API")
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare payload
            payload = {
                "inputs": texts,
                "options": {
                    "wait_for_model": True,
                    "use_cache": True
                }
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                raise Exception(f"API request failed: {response.text}")
            
            # Parse response
            embeddings = response.json()
            
            # Convert to numpy array
            if isinstance(embeddings, list) and len(embeddings) > 0:
                if isinstance(embeddings[0], list):
                    # Multiple embeddings
                    embeddings_array = np.array(embeddings, dtype=np.float32)
                else:
                    # Single embedding
                    embeddings_array = np.array([embeddings], dtype=np.float32)
            else:
                raise Exception("Invalid response format from API")
            
            logger.info(f"Generated embeddings with shape: {embeddings_array.shape}")
            return embeddings_array
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of embedding with shape (embedding_dim,)
        """
        return self.generate_embeddings([text])[0]
    
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
