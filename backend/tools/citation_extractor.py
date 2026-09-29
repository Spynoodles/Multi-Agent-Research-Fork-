"""
Citation Extractor Tool for the Multi-Agent Research Platform.

Extracts and formats citations from various sources:
- Web URLs
- Document references
- Academic sources
"""

from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlparse


class CitationExtractor:
    """
    Citation extraction and formatting tool.

    Supports multiple citation formats:
    - APA
    - MLA
    - Chicago
    """

    def __init__(self):
        """Initialize the citation extractor."""
        pass

    def extract_from_url(self, url: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract citation information from a URL.

        Args:
            url: Web URL
            title: Optional page title

        Returns:
            Dictionary with citation metadata
        """
        parsed = urlparse(url)

        citation = {
            "type": "web",
            "url": url,
            "domain": parsed.netloc,
            "path": parsed.path,
            "title": title or self._extract_title_from_url(url),
            "accessed_date": datetime.now().strftime("%Y-%m-%d"),
            "raw": url,
        }

        return citation

    def extract_from_document(
        self,
        document_id: str,
        page: Optional[int] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract citation information from a document.

        Args:
            document_id: Document identifier
            page: Optional page number
            title: Document title
            author: Document author

        Returns:
            Dictionary with citation metadata
        """
        citation = {
            "type": "document",
            "document_id": document_id,
            "title": title or f"Document {document_id}",
            "author": author,
            "page": page,
            "raw": f"{title or document_id}" + (f", p. {page}" if page else ""),
        }

        return citation

    def format_citation(
        self, citation: Dict[str, Any], format_type: str = "apa"
    ) -> str:
        """
        Format a citation in the specified style.

        Args:
            citation: Citation dictionary
            format_type: "apa", "mla", or "chicago"

        Returns:
            Formatted citation string
        """
        if format_type.lower() == "apa":
            return self._format_apa(citation)
        elif format_type.lower() == "mla":
            return self._format_mla(citation)
        elif format_type.lower() == "chicago":
            return self._format_chicago(citation)
        else:
            return citation.get("raw", str(citation))

    def _format_apa(self, citation: Dict[str, Any]) -> str:
        """Format citation in APA style."""
        if citation.get("type") == "web":
            title = citation.get("title", "Untitled")
            url = citation.get("url", "")
            accessed = citation.get("accessed_date", "")

            # Try to extract author from domain or title
            author = citation.get("author", "")
            if not author and citation.get("domain"):
                # Use domain as organization author
                domain = citation.get("domain", "").replace("www.", "")
                author = domain.split(".")[0].title()

            if author:
                return f"{author}. ({accessed[:4]}). {title}. Retrieved from {url}"
            else:
                return f"{title}. (n.d.). Retrieved {accessed} from {url}"

        elif citation.get("type") == "document":
            author = citation.get("author", "")
            title = citation.get("title", "")
            page = citation.get("page")

            if author:
                result = f"{author}. {title}"
            else:
                result = title

            if page:
                result += f" (p. {page})"

            return result

        return citation.get("raw", str(citation))

    def _format_mla(self, citation: Dict[str, Any]) -> str:
        """Format citation in MLA style."""
        if citation.get("type") == "web":
            title = citation.get("title", "Untitled")
            url = citation.get("url", "")
            accessed = citation.get("accessed_date", "")

            author = citation.get("author", "")
            if author:
                return f'"{title}." {url}. Accessed {accessed}.'
            else:
                return f'"{title}." {url}. Accessed {accessed}.'

        elif citation.get("type") == "document":
            author = citation.get("author", "")
            title = citation.get("title", "")
            page = citation.get("page")

            if author:
                result = f"{author}. {title}"
            else:
                result = title

            if page:
                result += f" (p. {page})"

            return result

        return citation.get("raw", str(citation))

    def _format_chicago(self, citation: Dict[str, Any]) -> str:
        """Format citation in Chicago style."""
        if citation.get("type") == "web":
            title = citation.get("title", "Untitled")
            url = citation.get("url", "")
            accessed = citation.get("accessed_date", "")

            return f'"{title}." {url}. Accessed {accessed}.'

        elif citation.get("type") == "document":
            author = citation.get("author", "")
            title = citation.get("title", "")
            page = citation.get("page")

            if author:
                result = f"{author}. {title}"
            else:
                result = title

            if page:
                result += f", {page}"

            return result

        return citation.get("raw", str(citation))

    def _extract_title_from_url(self, url: str) -> str:
        """Extract a title-like string from URL."""
        parsed = urlparse(url)
        path = parsed.path.strip("/")

        if path:
            # Use last part of path
            parts = path.split("/")
            title = parts[-1].replace("-", " ").replace("_", " ").title()
            return title

        # Use domain
        domain = parsed.netloc.replace("www.", "")
        return domain.split(".")[0].title()
