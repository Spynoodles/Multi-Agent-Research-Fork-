"""
Session Management Component for Streamlit UI.
"""

from typing import List, Optional

import streamlit as st

from backend.core.memory_manager import ResearchSession


def render_session_history(sessions: List[ResearchSession]):
    """
    Render session history in Streamlit.

    Args:
        sessions: List of research sessions
    """
    if not sessions:
        st.info("No previous research sessions.")
        return

    # Display recent sessions with better design
    st.markdown(f"### Showing {min(len(sessions), 10)} Recent Sessions")

    for i, session in enumerate(sessions[:10], 1):  # Show last 10
        created_date = (
            session.created_at[:10]
            if hasattr(session, "created_at") and session.created_at
            else "Unknown"
        )
        title = session.query[:70] + ("..." if len(session.query) > 70 else "")

        with st.expander(f"Session {i}: {title}", expanded=False):
            left, right = st.columns([3, 1])

            with left:
                st.markdown(f"**Created:** {created_date}")
                if hasattr(session, "updated_at") and session.updated_at:
                    st.markdown(f"**Updated:** {session.updated_at[:10]}")

                if session.report:
                    st.markdown("---")
                    st.markdown("**Report Preview:**")
                    preview = session.report[:600] + (
                        "..." if len(session.report) > 600 else ""
                    )
                    st.markdown(preview)

            with right:
                st.markdown(f"**Session ID:** `{session.id[:8]}...`")
                if session.quality_scores:
                    avg_score = sum(session.quality_scores.values()) / len(
                        session.quality_scores
                    )
                    st.metric("Quality Score", f"{avg_score:.1f}/10")

                # Actions: download report
                if session.report:
                    st.download_button(
                        label="Download Report",
                        data=session.report,
                        file_name=f"session_{session.id[:8]}_report.md",
                        mime="text/markdown",
                        key=f"download_{session.id}",
                    )

            # Show individual quality scores in a compact row
            if session.quality_scores:
                st.markdown("---")
                cols = st.columns(min(len(session.quality_scores), 4))
                for j, (metric, score) in enumerate(session.quality_scores.items()):
                    with cols[j % len(cols)]:
                        st.metric(metric.replace("_", " ").title(), f"{score:.1f}")


def render_session_selector(sessions: List[ResearchSession]) -> Optional[str]:
    """
    Render session selector dropdown.

    Args:
        sessions: List of research sessions

    Returns:
        Selected session ID or None
    """
    if not sessions:
        return None

    session_options = {
        f"{s.query[:50]}... ({s.created_at[:10]})": s.id for s in sessions
    }

    selected = st.selectbox(
        "Load Previous Session",
        options=["None"] + list(session_options.keys()),
        key="session_selector",
    )

    if selected and selected != "None":
        return session_options[selected]

    return None
