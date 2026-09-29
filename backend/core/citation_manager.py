"""
Citation Manager for the Multi-Agent Research Platform.

Tracks citations from multiple sources and formats them consistently.
"""

from typing import Any, Dict, List, Optional

from ..tools.citation_extractor import CitationExtractor


class CitationManager:
    """
    Manages citations throughout the research process.

    Features:
    - Track citations from web sources
    - Track citations from documents
    - Format citations in multiple styles
    - Generate citation lists
    """

    def __init__(self):
        """Initialize the citation manager."""
        self.citations: List[Dict[str, Any]] = []
        self.extractor = CitationExtractor()
        self.citation_counter = 0

    def add_web_citation(
        self,
        url: str,
        title: Optional[str] = None,
        content_snippet: Optional[str] = None,
    ) -> str:
        """
        Add a citation from a web source.

        Args:
            url: Web URL
            title: Optional page title
            content_snippet: Optional content snippet

        Returns:
            Citation ID for referencing
        """
        citation = self.extractor.extract_from_url(url, title)
        citation["id"] = f"web_{self.citation_counter}"
        citation["content_snippet"] = content_snippet
        self.citation_counter += 1

        self.citations.append(citation)
        return citation["id"]

    def add_document_citation(
        self,
        document_id: str,
        page: Optional[int] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        content_snippet: Optional[str] = None,
    ) -> str:
        """
        Add a citation from a document.

        Args:
            document_id: Document identifier
            page: Optional page number
            title: Document title
            author: Document author
            content_snippet: Optional content snippet

        Returns:
            Citation ID for referencing
        """
        citation = self.extractor.extract_from_document(
            document_id, page, title, author
        )
        citation["id"] = f"doc_{self.citation_counter}"
        citation["content_snippet"] = content_snippet
        self.citation_counter += 1

        self.citations.append(citation)
        return citation["id"]

    def get_citation(self, citation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a citation by ID.

        Args:
            citation_id: Citation ID

        Returns:
            Citation dictionary or None
        """
        for citation in self.citations:
            if citation.get("id") == citation_id:
                return citation
        return None

    def get_all_citations(self) -> List[Dict[str, Any]]:
        """Get all citations."""
        return self.citations.copy()

    def format_citations(
        self, format_type: str = "apa", include_ids: bool = False
    ) -> List[str]:
        """
        Format all citations in the specified style.

        Args:
            format_type: "apa", "mla", or "chicago"
            include_ids: Whether to include citation IDs

        Returns:
            List of formatted citation strings
        """
        formatted = []
        for citation in self.citations:
            formatted_citation = self.extractor.format_citation(citation, format_type)
            if include_ids:
                formatted_citation = f"[{citation['id']}] {formatted_citation}"
            formatted.append(formatted_citation)

        return formatted

    def generate_reference_list(self, format_type: str = "apa") -> str:
        """
        Generate a formatted reference list.

        Args:
            format_type: Citation format style

        Returns:
            Formatted reference list string
        """
        formatted_citations = self.format_citations(format_type)

        header = "References" if format_type.lower() == "apa" else "Works Cited"
        references = [header, "=" * len(header), ""]

        for i, citation in enumerate(formatted_citations, 1):
            references.append(f"{i}. {citation}")

        return "\n".join(references)

    def clear(self):
        """Clear all citations."""
        self.citations = []
        self.citation_counter = 0

    def get_citation_count(self) -> int:
        """Get the total number of citations."""
        return len(self.citations)

    def get_web_citations(self) -> List[Dict[str, Any]]:
        """Get all web citations."""
        return [c for c in self.citations if c.get("type") == "web"]

    def get_document_citations(self) -> List[Dict[str, Any]]:
        """Get all document citations."""
        return [c for c in self.citations if c.get("type") == "document"]
