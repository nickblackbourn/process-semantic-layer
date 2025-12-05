"""
Embedding engine for document and query vectorization.
Uses sentence-transformers for generating embeddings and computing similarity.
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Optional
from src.models import TaggedDocument


class EmbeddingEngine:
    """Generates embeddings and computes similarity scores."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding engine with a sentence-transformer model.
        
        Args:
            model_name: Name of the sentence-transformer model to use
                       (default: all-MiniLM-L6-v2 - fast, 384-dim)
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"Model loaded successfully")
    
    def embed_documents(self, docs: list[TaggedDocument]) -> list[TaggedDocument]:
        """
        Generate embeddings for a list of documents.
        Updates the embedding field in each document object.
        
        Args:
            docs: List of TaggedDocument objects
            
        Returns:
            Same list with embeddings populated
        """
        if not docs:
            return docs
        
        print(f"Generating embeddings for {len(docs)} documents...")
        
        # Prepare text for embedding (combine title and content)
        texts = [f"{doc.title}. {doc.content}" for doc in docs]
        
        # Generate embeddings in batch
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Assign embeddings to documents
        for doc, embedding in zip(docs, embeddings):
            doc.embedding = embedding
        
        print(f"Embeddings generated (dimension: {embeddings.shape[1]})")
        return docs
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query string.
        
        Args:
            query: Query text
            
        Returns:
            Numpy array containing the query embedding
        """
        if not query:
            raise ValueError("Query cannot be empty")
        
        embedding = self.model.encode([query], show_progress_bar=False)[0]
        return embedding
    
    def rank_by_similarity(
        self, 
        query_embedding: np.ndarray, 
        docs: list[TaggedDocument]
    ) -> list[tuple[TaggedDocument, float]]:
        """
        Rank documents by cosine similarity to query embedding.
        
        Args:
            query_embedding: Query embedding vector
            docs: List of documents with embeddings
            
        Returns:
            List of (document, similarity_score) tuples, sorted by score descending
        """
        if not docs:
            return []
        
        # Filter out documents without embeddings
        docs_with_embeddings = [doc for doc in docs if doc.embedding is not None]
        
        if not docs_with_embeddings:
            return []
        
        # Stack document embeddings into a matrix
        doc_embeddings = np.vstack([doc.embedding for doc in docs_with_embeddings])
        
        # Reshape query embedding for sklearn
        query_embedding_2d = query_embedding.reshape(1, -1)
        
        # Compute cosine similarity
        similarities = cosine_similarity(query_embedding_2d, doc_embeddings)[0]
        
        # Create (document, score) tuples
        doc_scores = list(zip(docs_with_embeddings, similarities))
        
        # Sort by similarity score (descending)
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        return doc_scores
