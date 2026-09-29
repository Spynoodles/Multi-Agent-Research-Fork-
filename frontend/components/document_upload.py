"""
Document Upload Component for Streamlit UI.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st

from backend.tools.pdf_parser import PDFParser


def render_document_upload() -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Render document upload component.

    Returns:
        Tuple of (document texts, metadata list)
    """
    st.markdown("### Upload Documents")
    st.markdown(
        "Upload PDF documents to enhance your research. Documents will be processed and added to the knowledge base."
    )

    uploaded_files = st.file_uploader(
        "Choose PDF files to upload",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or more PDF files. They will be processed and indexed for semantic search.",
    )

    documents = []
    metadata_list = []
    pdf_parser = PDFParser()

    if uploaded_files:
        st.markdown("---")
        st.markdown(f"### {len(uploaded_files)} file(s) ready to process")
        include_map = {}

        # Show file cards and parse each with a spinner
        for uploaded_file in uploaded_files:
            name = uploaded_file.name
            container = st.container()
            with container:
                cols = st.columns([5, 1])
                with cols[0]:
                    st.markdown(f"**{name}**")
                    st.caption("PDF file")
                with cols[1]:
                    include_map[name] = st.checkbox(
                        "Include", value=True, key=f"include_{name}"
                    )

            # Parse file immediately (keeps behavior compatible with orchestrator.load_documents)
            if include_map.get(name):
                try:
                    with st.spinner(f"Parsing {name}..."):
                        upload_dir = Path("data/documents")
                        upload_dir.mkdir(parents=True, exist_ok=True)
                        file_path = upload_dir / name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        parsed = pdf_parser.parse_file(
                            str(file_path), extract_metadata=True
                        )

                    documents.append(parsed.get("text", ""))
                    metadata_list.append(
                        {
                            "document_id": name,
                            "source": name,
                            "title": parsed.get("metadata", {}).get("title") or name,
                            "author": parsed.get("metadata", {}).get("author"),
                            "num_pages": parsed.get("num_pages", 0),
                        }
                    )

                    st.success(
                        f"Loaded: **{name}** ({parsed.get('num_pages', 0)} pages)"
                    )
                    with st.expander("Preview parsed text", expanded=False):
                        preview_text = parsed.get("text", "")[:1000]
                        st.text_area(
                            "Preview",
                            value=preview_text,
                            height=150,
                            key=f"preview_{name}",
                        )

                except Exception as e:
                    st.error(f"Error processing {name}: {str(e)}")

        st.markdown("---")

    return documents, metadata_list
