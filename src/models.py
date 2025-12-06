"""
Data models for the semantic layer PoC.
Defines concepts, documents, and query/response structures.
"""
from typing import Optional
from pydantic import BaseModel, Field
import numpy as np


class Concept(BaseModel):
    """Represents a business concept in the semantic graph."""
    id: str
    name: str
    synonyms: list[str] = Field(default_factory=list)
    related_to: list[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


class Document(BaseModel):
    """Represents a raw document before tagging."""
    doc_id: str
    title: str
    content: str

    class Config:
        arbitrary_types_allowed = True


class TaggedDocument(Document):
    """Document enriched with matched concepts and embeddings."""
    matched_concepts: list[str] = Field(default_factory=list)
    embedding: Optional[np.ndarray] = None

    class Config:
        arbitrary_types_allowed = True


class QueryRequest(BaseModel):
    """Request model for querying the pipeline."""
    query: str = Field(..., min_length=1, description="The search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class QueryResponse(BaseModel):
    """Response model containing ranked document results."""
    doc_id: str
    title: str
    matched_concepts: list[str]
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    snippet: str

    class Config:
        arbitrary_types_allowed = True
