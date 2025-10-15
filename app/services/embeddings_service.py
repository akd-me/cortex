import os
import numpy as np
from typing import List, Optional, Union
from sentence_transformers import SentenceTransformer
from ..logger import get_logger

logger = get_logger(__name__)

class EmbeddingsService:
    """Service for generating text embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    def generate_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text string or list of text strings
            
        Returns:
            numpy array of embeddings
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            logger.debug(f"Generated embeddings for {len(texts)} texts, shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return self.model.get_sentence_embedding_dimension()
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a search query for semantic search
        
        Args:
            query: Search query string
            
        Returns:
            numpy array of query embedding
        """
        return self.generate_embeddings(query)
    
    def encode_documents(self, documents: List[str]) -> np.ndarray:
        """
        Encode multiple documents for indexing
        
        Args:
            documents: List of document texts
            
        Returns:
            numpy array of document embeddings
        """
        return self.generate_embeddings(documents)
