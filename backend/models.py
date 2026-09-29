"""
Data models for the Multi-Agent Research Platform.

Uses Pydantic for data validation and type safety.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Request model for research queries."""

    query: str = Field(..., description="Research query")
    use_web_search: bool = Field(True, description="Whether to use web search")
    use_rag: bool = Field(True, description="Whether to use RAG document retrieval")
    document_ids: Optional[List[str]] = Field(
        None, description="Specific document IDs to search"
    )


class ResearchResult(BaseModel):
    """Result model for research output."""

    query: str
    report: str
    sources: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    quality_scores: Dict[str, float]
    session_id: str
    created_at: str


class SourceInfo(BaseModel):
    """Information about a source."""

    type: str = Field(..., description="Source type: 'web' or 'document'")
    url: Optional[str] = Field(None, description="URL for web sources")
    document_id: Optional[str] = Field(
        None, description="Document ID for document sources"
    )
    title: Optional[str] = Field(None, description="Source title")
    page: Optional[int] = Field(None, description="Page number for documents")
    citation_id: Optional[str] = Field(None, description="Citation ID")


class QualityScores(BaseModel):
    """Quality scores for research evaluation."""

    completeness: float = Field(0.0, ge=0.0, le=10.0)
    accuracy: float = Field(0.0, ge=0.0, le=10.0)
    relevance: float = Field(0.0, ge=0.0, le=10.0)
    clarity: float = Field(0.0, ge=0.0, le=10.0)
    source_quality: float = Field(0.0, ge=0.0, le=10.0)
    citation_quality: float = Field(0.0, ge=0.0, le=10.0)
    average: float = Field(0.0, ge=0.0, le=10.0)
