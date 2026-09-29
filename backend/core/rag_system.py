"""
Minimal RAG System for the Multi-Agent Research Platform.

Basic document storage for demo purposes.
"""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()


class RAGSystem:
    """
    Minimal RAG system for demo purposes.

    Exposes a stable query(...) interface so orchestrators/agents can
    depend on a single method name regardless of the underlying
    retrieval implementation.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Basic search - returns mock results."""
        # In a real system, this would perform vector search
        # For now, return the actual documents if they exist
        results = []
        sources = []
        
        for i, (doc, meta) in enumerate(zip(self.documents[:n_results], self.metadata[:n_results])):
            results.append(doc)
            sources.append({
                "document_id": meta.get("document_id", f"doc_{i}"),
                "source": meta.get("source", "Uploaded Document"),
                "content": doc[:200] + "..." if len(doc) > 200 else doc,
                "page": meta.get("page", 1)
            })
            
        return {
            "retrieved_documents": results,
            "sources": sources
        }

    def query(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Canonical retrieval entrypoint.

        For now, delegates to search(...). Replace/extend this to wire
        real vector search, hybrid retrieval, filters, rerankers, etc.
        """
        return self.search(query=query, n_results=k)

    def add_documents(
        self, documents: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Add documents."""
        self.documents.extend(documents)
        if metadata_list:
            self.metadata.extend(metadata_list)
        else:
            self.metadata.extend([{} for _ in documents])
        return f"Added {len(documents)} documents"

    def load_documents(
        self, documents: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Load documents."""
        return self.add_documents(documents, metadata_list)

    def save_vectorstore(self) -> None:
        """Save the vectorstore to disk."""
        # For this minimal version, we don't need to do anything
        pass

    def get_document_count(self) -> int:
        """Get the number of documents in the system."""
        return len(self.documents)
