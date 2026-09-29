"""
Tools for the Multi-Agent Research Platform.
"""

from .citation_extractor import CitationExtractor
from .pdf_parser import PDFParser
from .web_search import WebSearchTool

__all__ = [
    "WebSearchTool",
    "PDFParser",
    "CitationExtractor",
]
