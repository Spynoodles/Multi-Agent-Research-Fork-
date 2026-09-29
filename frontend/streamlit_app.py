"""
Main Streamlit Application for the Multi-Agent Research Platform.
"""

# Fix Python 3.12 compatibility with Pydantic v1 - MUST BE FIRST
import json
import sys
import time
import traceback
from pathlib import Path


# #region agent log
def _debug_log(location, message, data=None, hypothesis_id=None):
    try:
        log_entry = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id or "A",
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": __import__("time").time() * 1000,
        }
        with open(
            r"c:\Users\GIGABYTE\Desktop\Agentic Design Patterns\.cursor\debug.log",
            "a",
            encoding="utf-8",
        ) as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass


# #endregion

# Add project root to path to allow absolute imports
root_path = Path(__file__).parent.parent.absolute()
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Apply compatibility fix before ANY other imports
fix_path = root_path / "fix_pydantic_compat.py"
_debug_log(
    "streamlit_app.py:12",
    "Checking fix_pydantic_compat.py",
    {"exists": fix_path.exists(), "path": str(fix_path)},
    "A",
)
if fix_path.exists():
    try:
        _debug_log("streamlit_app.py:15", "Executing fix_pydantic_compat.py", {}, "A")
        exec(open(fix_path).read())
        _debug_log(
            "streamlit_app.py:17",
            "fix_pydantic_compat.py executed successfully",
            {},
            "A",
        )
    except Exception as e:
        _debug_log(
            "streamlit_app.py:19",
            "Error executing fix_pydantic_compat.py",
            {"error": str(e), "traceback": traceback.format_exc()},
            "A",
        )
        raise

import streamlit as st  # noqa: E402

try:
    _debug_log("streamlit_app.py:23", "Starting backend imports", {}, "B")
    from backend.orchestrator import ResearchOrchestrator

    _debug_log("streamlit_app.py:25", "ResearchOrchestrator imported", {}, "B")
    from frontend.components.document_upload import render_document_upload
    from frontend.components.research_display import render_research_results
    from frontend.components.session_manager import render_session_history

    _debug_log("streamlit_app.py:31", "All imports successful", {}, "B")
except Exception as e:
    _debug_log(
        "streamlit_app.py:33",
        "Import error",
        {"error": str(e), "traceback": traceback.format_exc()},
        "B",
    )
    raise

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Research Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

# Load external CSS (moved long styles into frontend/styles.css)
css_file = Path(__file__).parent / "styles.css"
if css_file.exists():
    try:
        st.markdown(
            f"<style>{css_file.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown("<!-- Failed to load styles.css -->", unsafe_allow_html=True)
else:
    st.markdown(
        "<!-- styles.css not found in frontend/; using default Streamlit styles -->",
        unsafe_allow_html=True,
    )

# Initialize session state
if "orchestrator" not in st.session_state:
    try:
        _debug_log("streamlit_app.py:132", "Initializing ResearchOrchestrator", {}, "B")
        st.session_state.orchestrator = ResearchOrchestrator()
        st.session_state.documents_loaded = False
        _debug_log(
            "streamlit_app.py:135",
            "ResearchOrchestrator initialized successfully",
            {},
            "B",
        )
    except Exception as e:
        _debug_log(
            "streamlit_app.py:137",
            "Orchestrator initialization failed",
            {"error": str(e), "traceback": traceback.format_exc()},
            "B",
        )
        st.error(f"Failed to initialize orchestrator: {str(e)}")
        st.stop()

if "research_result" not in st.session_state:
    st.session_state.research_result = None

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None


def main():
    """Main application function."""
    _debug_log("streamlit_app.py:145", "main() function called", {}, "C")

    # Header (uses centralized styles in frontend/styles.css)
    st.markdown(
        """
    <div class="app-header">
        <div style="flex: 1;">
            <h1 class="app-title">Multi-Agent Research Platform</h1>
            <p class="app-subtitle">AI-powered research with specialized agent collaboration</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Clean, minimalist sidebar
    with st.sidebar:
        st.markdown(
            """
        <div style="padding: 1rem 0; border-bottom: 1px solid #e5e7eb; margin-bottom: 1.5rem;">
            <h3 style="color: #374151; font-weight: 600; margin: 0; font-size: 1rem;">
                Navigation
            </h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Clean page selector
        pages = {"Research": "research", "Documents": "documents", "History": "history"}

        selected_page = st.radio(
            "Select Page",
            list(pages.keys()),
            key="page_selector",
            label_visibility="collapsed",
        )

        page = pages[selected_page]

        st.markdown("---")

        # Minimal system status
        st.markdown("**System Status**")

        if st.session_state.orchestrator:
            st.success("Ready")

            # Clean document count
            if st.session_state.orchestrator.rag_system:
                doc_count = (
                    st.session_state.orchestrator.rag_system.get_document_count()
                )
                if doc_count > 0:
                    st.metric("Documents", doc_count)
                else:
                    st.caption("No documents loaded")

        # Clean footer
        st.markdown("---")
        st.caption("Powered by Agentic Design Patterns")

        st.markdown("---")

        # Display recent sessions
        if st.session_state.orchestrator:
            recent_sessions = st.session_state.orchestrator.get_recent_sessions(5)
            if recent_sessions:
                st.markdown("### Recent Sessions")
                for i, session in enumerate(recent_sessions, 1):
                    st.markdown(f"**{i}.** {session.query[:35]}...")
                    st.caption(
                        f"{session.created_at[:10] if hasattr(session, 'created_at') else 'N/A'}"
                    )

        st.markdown("---")
        st.caption("Built with LangChain & Streamlit")

    # Main content area
    _debug_log("streamlit_app.py:195", "Rendering page", {"page": page}, "C")
    try:
        if page == "research":
            render_research_page()
        elif page == "documents":
            render_documents_page()
        elif page == "history":
            render_history_page()
        _debug_log(
            "streamlit_app.py:203", "Page rendered successfully", {"page": page}, "C"
        )
    except Exception as e:
        _debug_log(
            "streamlit_app.py:205",
            "Error rendering page",
            {"page": page, "error": str(e), "traceback": traceback.format_exc()},
            "C",
        )
        st.error(f"Error rendering {page} page: {str(e)}")
        raise


def render_research_page():
    """Render the main research page."""
    st.markdown(
        """
    <div style="padding: 2rem 0; margin-bottom: 2rem;">
        <h2 style="color: #1e293b; margin-bottom: 0.5rem; font-weight: 600; font-size: 1.5rem;">
            Conduct Research
        </h2>
        <p style="color: #6b7280; margin: 0; font-size: 1rem;">
            Enter your research question and let AI agents collaborate to deliver comprehensive results.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Clean research query input
    st.markdown("**Research Query**")

    _debug_log(
        "streamlit_app.py:230",
        "Getting research_result from session_state",
        {"has_result": st.session_state.research_result is not None},
        "D",
    )
    query_value = ""
    if st.session_state.research_result:
        try:
            query_value = st.session_state.research_result.get("query", "")
            _debug_log(
                "streamlit_app.py:234",
                "Extracted query from research_result",
                {"query_length": len(query_value)},
                "D",
            )
        except AttributeError as e:
            _debug_log(
                "streamlit_app.py:236",
                "AttributeError accessing research_result",
                {
                    "error": str(e),
                    "type": type(st.session_state.research_result).__name__,
                },
                "D",
            )
            query_value = ""

    # Textarea/input styling provided by frontend/styles.css

    query = st.text_area(
        "What would you like to research?",
        value=query_value,
        height=100,
        placeholder="e.g., What are the latest developments in quantum computing for drug discovery?",
        key="research_query",
        help="Be specific and clear about what you want to research",
    )

    # Clean research options
    st.markdown("**Research Options**")

    col1, col2, col3 = st.columns(3)

    with col1:
        use_web_search = st.checkbox(
            "Web Search",
            value=True,
            key="use_web_search",
            help="Search the internet for current information",
        )

    with col2:
        use_rag = st.checkbox(
            "Document Search",
            value=True,
            key="use_rag",
            help="Search through uploaded documents",
        )

    with col3:
        if st.session_state.orchestrator and st.session_state.orchestrator.rag_system:
            doc_count = st.session_state.orchestrator.rag_system.get_document_count()
            st.metric("Documents", doc_count)
        else:
            st.metric("Documents", 0)

    # Clean research button
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Research", use_container_width=True, type="primary"):
            if not query:
                st.warning("Please enter a research query.")
                return

            # Clean research progress
            st.markdown("### Research in Progress")

            # Agent workflow visualization
            agent_status = st.empty()
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Agent status containers
            col1, col2, col3, col4 = st.columns(4)
            agent_containers = [col1.empty(), col2.empty(), col3.empty(), col4.empty()]
            agent_names = ["Router", "Researcher", "Fact-Checker", "Synthesizer"]
            agent_statuses = ["pending"] * 4

            def update_agent_status(agent_idx, status, message=""):
                agent_statuses[agent_idx] = status
                status_labels = {
                    "pending": "WAITING",
                    "active": "WORKING",
                    "completed": "DONE",
                    "error": "ERROR",
                }
                
                status_icons = {
                    "pending": "🕒",
                    "active": "⚡",
                    "completed": "✅",
                    "error": "❌",
                }

                css_class = f"agent-card agent-{status}"
                agent_containers[agent_idx].markdown(
                    f"""
                <div class="{css_class}" style="padding:0.8rem; position: relative; overflow: hidden;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
                        <div class="agent-status">{status_labels.get(status, "")}</div>
                        <div style="font-size: 1.1rem;">{status_icons.get(status, "")}</div>
                    </div>
                    <div class="agent-name">{agent_names[agent_idx]}</div>
                    {f'<div class="agent-msg">{message}</div>' if message else ""}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            # Initialize all agents as pending
            for i in range(4):
                update_agent_status(i, "pending")

            try:
                _debug_log(
                    "streamlit_app.py:260",
                    "Starting research",
                    {
                        "query": query[:50],
                        "use_web_search": use_web_search,
                        "use_rag": use_rag,
                    },
                    "E",
                )

                # Progress callback for the orchestrator
                def on_research_progress(agent_idx, status, message):
                    update_agent_status(agent_idx, status, message)
                    # Update progress bar and status text
                    progress_map = {0: 20, 1: 50, 2: 75, 3: 90}
                    progress_bar.progress(progress_map.get(agent_idx, 0))
                    
                    names = ["Router", "Researcher", "Fact-Checker", "Synthesizer"]
                    if status == "active":
                        status_text.info(f"{names[agent_idx]}: {message}")
                    elif status == "completed":
                        status_text.success(f"{names[agent_idx]}: {message}")

                result = st.session_state.orchestrator.research(
                    query=query,
                    use_web_search=use_web_search,
                    use_rag=use_rag,
                    save_session=True,
                    on_progress=on_research_progress
                )

                _debug_log(
                    "streamlit_app.py:272",
                    "Research completed",
                    {
                        "has_result": result is not None,
                        "has_report": "report" in result if result else False,
                        "session_id": result.get("session_id") if result else None,
                    },
                    "E",
                )

                status_text.success("Research Complete! Compiling final results...")
                progress_bar.progress(100)
                time.sleep(1)
                st.balloons()
                time.sleep(0.5)

                st.session_state.research_result = result
                st.session_state.current_session_id = result.get("session_id")
                st.rerun()

            except Exception as e:
                _debug_log(
                    "streamlit_app.py:285",
                    "Research failed",
                    {
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc(),
                    },
                    "E",
                )
                st.error(f"Research failed: {str(e)}")
                st.exception(e)

                # Provide helpful error message
                error_msg = str(e).lower()
                if "api key" in error_msg:
                    st.info(
                        "Tip: Make sure your Gemini API key is set in the .env file."
                    )
                elif "timeout" in error_msg:
                    st.info(
                        "Tip: The request timed out. Try again or simplify your query."
                    )
                elif "rate limit" in error_msg:
                    st.info(
                        "Tip: API rate limit exceeded. Please wait a moment and try again."
                    )

    # Display results
    if st.session_state.research_result:
        _debug_log(
            "streamlit_app.py:300",
            "Rendering research results",
            {
                "has_result": True,
                "result_keys": list(st.session_state.research_result.keys())
                if isinstance(st.session_state.research_result, dict)
                else "not_dict",
            },
            "D",
        )
        st.markdown("---")
        try:
            render_research_results(st.session_state.research_result)
            _debug_log(
                "streamlit_app.py:304",
                "Research results rendered successfully",
                {},
                "D",
            )
        except Exception as e:
            _debug_log(
                "streamlit_app.py:306",
                "Error rendering research results",
                {"error": str(e), "traceback": traceback.format_exc()},
                "D",
            )
            st.error(f"Error displaying results: {str(e)}")
            raise

        # Export options with better design
        st.markdown("---")
        st.markdown("## Export Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            markdown_content = f"# Research Report\n\n**Query:** {st.session_state.research_result.get('query', '')}\n\n{st.session_state.research_result.get('report', '')}"
            st.download_button(
                label="Download Report (Markdown)",
                data=markdown_content,
                file_name="research_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col2:
            from backend.core.citation_manager import CitationManager

            citation_manager = CitationManager()
            citation_manager.citations = st.session_state.research_result.get(
                "citations", []
            )
            citations_text = citation_manager.generate_reference_list("apa")
            st.download_button(
                label="Download Citations (APA)",
                data=citations_text,
                file_name="citations.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with col3:
            # JSON export
            import json

            json_content = json.dumps(st.session_state.research_result, indent=2)
            st.download_button(
                label="Download Full Data (JSON)",
                data=json_content,
                file_name="research_data.json",
                mime="application/json",
                use_container_width=True,
            )


def render_documents_page():
    """Render the documents management page."""
    st.markdown("## Document Management")
    st.markdown(
        "Upload PDF documents to enhance your research with custom knowledge sources."
    )

    # Upload documents
    documents, metadata_list = render_document_upload()

    if documents:
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button(
                "Load Documents into RAG System",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Processing documents and creating embeddings..."):
                    try:
                        st.session_state.orchestrator.load_documents(
                            documents, metadata_list
                        )
                        st.session_state.documents_loaded = True
                        st.success(
                            f"Successfully loaded {len(documents)} document(s) into the RAG system!"
                        )
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error loading documents: {str(e)}")
                        error_msg = str(e).lower()
                        if "pdf" in error_msg or "parse" in error_msg:
                            st.info(
                                "Tip: Make sure the PDF file is not corrupted or password-protected."
                            )
                        elif "vector" in error_msg or "embedding" in error_msg:
                            st.info("Tip: Check your Gemini API key is set correctly.")

        # Display loaded documents info
        if st.session_state.documents_loaded:
            st.info(
                f"{len(documents)} document(s) are now available for research queries."
            )

    # Document statistics with better design
    st.markdown("---")
    st.markdown("### Document Statistics")

    if st.session_state.orchestrator and st.session_state.orchestrator.rag_system:
        doc_count = st.session_state.orchestrator.rag_system.get_document_count()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Documents", doc_count)
        with col2:
            if metadata_list:
                total_pages = sum(m.get("num_pages", 0) for m in metadata_list)
                st.metric("Total Pages", total_pages)
        with col3:
            status = "Ready" if doc_count > 0 else "No Documents"
            st.metric("System Status", status)
    else:
        st.info("No documents loaded yet. Upload PDF files above to get started.")


def render_history_page():
    """Render the history page."""
    st.markdown("## Research History")
    st.markdown("View and manage your previous research sessions.")

    if st.session_state.orchestrator:
        all_sessions = st.session_state.orchestrator.get_all_sessions()

        if all_sessions:
            st.metric("Total Sessions", len(all_sessions))
            st.markdown("---")
            render_session_history(all_sessions)

            # Session actions with better design
            st.markdown("---")
            st.markdown("### Session Actions")

            session_ids = {f"{s.query[:50]}...": s.id for s in all_sessions}
            selected_session = st.selectbox(
                "Select a session to manage",
                options=["None"] + list(session_ids.keys()),
                key="history_session_selector",
                help="Choose a session to load or delete",
            )

            if selected_session and selected_session != "None":
                session_id = session_ids[selected_session]
                session = st.session_state.orchestrator.get_session(session_id)

                if session:
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "Load Session", use_container_width=True, type="primary"
                        ):
                            st.session_state.research_result = {
                                "query": session.query,
                                "report": session.report,
                                "quality_scores": session.quality_scores,
                                "citations": session.citations,
                            }
                            st.session_state.current_session_id = session.id
                            st.success(
                                "Session loaded! Switch to Research page to view."
                            )

                    with col2:
                        if st.button("Delete Session", use_container_width=True):
                            st.session_state.orchestrator.memory_manager.delete_session(
                                session_id
                            )
                            st.success("Session deleted!")
                            st.rerun()
        else:
            st.info(
                "No research sessions yet. Start a research query on the Research page!"
            )


if __name__ == "__main__":
    main()
