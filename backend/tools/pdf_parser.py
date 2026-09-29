"""
PDF Parser Tool for the Multi-Agent Research Platform.

Supports multiple PDF parsing libraries:
- pdfplumber (primary, better for text extraction)
- PyPDF2 (fallback)
"""

import os
from io import BytesIO
from typing import Any, Dict

import pdfplumber
import PyPDF2


class PDFParser:
    """
    PDF parsing tool that extracts text and metadata from PDF files.

    Uses pdfplumber as primary parser, PyPDF2 as fallback.
    """

    def __init__(self):
        """Initialize the PDF parser."""
        pass

    def parse_file(
        self, file_path: str, extract_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Parse a PDF file from disk.

        Args:
            file_path: Path to PDF file
            extract_metadata: Whether to extract metadata

        Returns:
            Dictionary with text, metadata, and page information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            return self._parse_with_pdfplumber(file_path, extract_metadata)
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {str(e)}")
            try:
                return self._parse_with_pypdf2(file_path, extract_metadata)
            except Exception as e2:
                raise RuntimeError(
                    f"Both PDF parsers failed. pdfplumber: {str(e)}, PyPDF2: {str(e2)}"
                )

    def parse_bytes(
        self,
        pdf_bytes: bytes,
        filename: str = "document.pdf",
        extract_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Parse a PDF from bytes (e.g., from file upload).

        Args:
            pdf_bytes: PDF file as bytes
            filename: Original filename
            extract_metadata: Whether to extract metadata

        Returns:
            Dictionary with text, metadata, and page information
        """
        try:
            return self._parse_bytes_with_pdfplumber(
                pdf_bytes, filename, extract_metadata
            )
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {str(e)}")
            try:
                return self._parse_bytes_with_pypdf2(
                    pdf_bytes, filename, extract_metadata
                )
            except Exception as e2:
                raise RuntimeError(
                    f"Both PDF parsers failed. pdfplumber: {str(e)}, PyPDF2: {str(e2)}"
                )

    def _parse_with_pdfplumber(
        self, file_path: str, extract_metadata: bool
    ) -> Dict[str, Any]:
        """Parse PDF using pdfplumber."""
        text_parts = []
        pages_data = []

        with pdfplumber.open(file_path) as pdf:
            metadata = {}
            if extract_metadata:
                metadata = {
                    "title": pdf.metadata.get("Title", ""),
                    "author": pdf.metadata.get("Author", ""),
                    "subject": pdf.metadata.get("Subject", ""),
                    "creator": pdf.metadata.get("Creator", ""),
                    "producer": pdf.metadata.get("Producer", ""),
                    "creation_date": str(pdf.metadata.get("CreationDate", "")),
                    "modification_date": str(pdf.metadata.get("ModDate", "")),
                    "num_pages": len(pdf.pages),
                }

            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
                pages_data.append(
                    {
                        "page_number": page_num,
                        "text": page_text,
                        "char_count": len(page_text),
                    }
                )

        full_text = "\n\n".join(text_parts)

        return {
            "text": full_text,
            "metadata": metadata,
            "pages": pages_data,
            "num_pages": len(pages_data),
            "total_chars": len(full_text),
            "parser": "pdfplumber",
        }

    def _parse_with_pypdf2(
        self, file_path: str, extract_metadata: bool
    ) -> Dict[str, Any]:
        """Parse PDF using PyPDF2."""
        text_parts = []
        pages_data = []

        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)

            metadata = {}
            if extract_metadata and pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                    "creator": pdf_reader.metadata.get("/Creator", ""),
                    "producer": pdf_reader.metadata.get("/Producer", ""),
                    "creation_date": str(pdf_reader.metadata.get("/CreationDate", "")),
                    "modification_date": str(pdf_reader.metadata.get("/ModDate", "")),
                    "num_pages": len(pdf_reader.pages),
                }

            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
                pages_data.append(
                    {
                        "page_number": page_num,
                        "text": page_text,
                        "char_count": len(page_text),
                    }
                )

        full_text = "\n\n".join(text_parts)

        return {
            "text": full_text,
            "metadata": metadata,
            "pages": pages_data,
            "num_pages": len(pages_data),
            "total_chars": len(full_text),
            "parser": "pypdf2",
        }

    def _parse_bytes_with_pdfplumber(
        self, pdf_bytes: bytes, filename: str, extract_metadata: bool
    ) -> Dict[str, Any]:
        """Parse PDF bytes using pdfplumber."""
        text_parts = []
        pages_data = []

        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            metadata: Dict[str, Any] = {"filename": filename}
            if extract_metadata:
                metadata.update(
                    {
                        "title": pdf.metadata.get("Title", ""),
                        "author": pdf.metadata.get("Author", ""),
                        "subject": pdf.metadata.get("Subject", ""),
                        "creator": pdf.metadata.get("Creator", ""),
                        "producer": pdf.metadata.get("Producer", ""),
                        "creation_date": str(pdf.metadata.get("CreationDate", "")),
                        "modification_date": str(pdf.metadata.get("ModDate", "")),
                        "num_pages": len(pdf.pages),
                    }
                )

            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
                pages_data.append(
                    {
                        "page_number": page_num,
                        "text": page_text,
                        "char_count": len(page_text),
                    }
                )

        full_text = "\n\n".join(text_parts)

        return {
            "text": full_text,
            "metadata": metadata,
            "pages": pages_data,
            "num_pages": len(pages_data),
            "total_chars": len(full_text),
            "parser": "pdfplumber",
        }

    def _parse_bytes_with_pypdf2(
        self, pdf_bytes: bytes, filename: str, extract_metadata: bool
    ) -> Dict[str, Any]:
        """Parse PDF bytes using PyPDF2."""
        text_parts = []
        pages_data = []

        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        metadata: Dict[str, Any] = {"filename": filename}
        if extract_metadata and pdf_reader.metadata:
            metadata.update(
                {
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                    "creator": pdf_reader.metadata.get("/Creator", ""),
                    "producer": pdf_reader.metadata.get("/Producer", ""),
                    "creation_date": str(pdf_reader.metadata.get("/CreationDate", "")),
                    "modification_date": str(pdf_reader.metadata.get("/ModDate", "")),
                    "num_pages": len(pdf_reader.pages),
                }
            )

        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
            pages_data.append(
                {
                    "page_number": page_num,
                    "text": page_text,
                    "char_count": len(page_text),
                }
            )

        full_text = "\n\n".join(text_parts)

        return {
            "text": full_text,
            "metadata": metadata,
            "pages": pages_data,
            "num_pages": len(pages_data),
            "total_chars": len(full_text),
            "parser": "pypdf2",
        }
