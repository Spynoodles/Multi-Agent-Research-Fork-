"""
Research Display Component for Streamlit UI.
"""

from typing import Any, Dict

import plotly.graph_objects as go
import streamlit as st


def render_research_results(result: Dict[str, Any]):
    """
    Render research results in Streamlit with enhanced modern UI.

    Args:
        result: Research result dictionary from orchestrator
    """
    if not result:
        st.error("No research results to display")
        return

    # Clean query display
    query = result.get("query", "Unknown query")
    st.markdown(f"**Research Query:** {query}")
    st.markdown("---")

    # Research report
    st.markdown("### Research Report")
    report = result.get("report", "No report generated.")
    summary = result.get("summary")
    if summary:
        st.info(summary)

    st.markdown(report)

    st.markdown("---")

    # Quality evaluation (now in expander and below report)
    with st.expander("🔍 View Quality Evaluation & Analysis", expanded=False):
        st.markdown("### Internal Quality Assessment")
        evaluation_text = result.get("evaluation")
        if evaluation_text:
            st.info(evaluation_text)

        quality_scores = result.get("quality_scores", {})
        if quality_scores:
            # Simple metric display
            metrics = list(quality_scores.items())
            cols = st.columns(min(len(metrics), 4))

            for i, (metric, score) in enumerate(metrics):
                with cols[i % 4]:
                    metric_name = metric.replace("_", " ").title()
                    st.metric(metric_name, f"{score:.1f}/10")

            # Create radar chart
            categories = list(quality_scores.keys())
            values = [quality_scores[k] for k in categories]

            fig = go.Figure()

            fig.add_trace(
                go.Scatterpolar(
                    r=values + [values[0]],  # Close the loop
                    theta=[c.replace("_", " ").title() for c in categories]
                    + [categories[0].replace("_", " ").title()],
                    fill="toself",
                    name="Quality Scores",
                    fillcolor="rgba(31, 119, 180, 0.2)",
                    line=dict(color="rgb(31, 119, 180)", width=3),
                )
            )

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10))
                ),
                showlegend=False,
                title=dict(text="Quality Dimensions", font=dict(size=16)),
                height=350,
                margin=dict(l=40, r=40, t=40, b=40),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Display average score
            avg_score = result.get("average_quality_score", 0)
            if avg_score >= 8:
                st.success(f"**Overall Quality Score: {avg_score:.1f}/10 - Excellent**")
            elif avg_score >= 6:
                st.info(f"**Overall Quality Score: {avg_score:.1f}/10 - Good**")
            else:
                st.warning(f"**Overall Quality Score: {avg_score:.1f}/10 - Needs Improvement**")

    # Display sources with better design
    st.markdown("---")
    st.markdown("## Sources")
    sources = result.get("sources", [])
    if sources:
        st.success(f"Found {len(sources)} source(s)")
        for i, source in enumerate(sources, 1):
            source_type = source.get("type", "unknown")
            title = (
                source.get("title")
                or source.get("document_id")
                or source.get("url", "Unknown")
            )
            badge = "📄" if source_type == "document" else "🌐"
            with st.expander(f"{badge} Source {i}: {title}", expanded=False):
                if source_type == "web":
                    url = source.get("url", "N/A")
                    st.markdown(f"**URL:** [{url}]({url})")
                    if source.get("snippet"):
                        st.markdown(
                            f"**Preview:** {source.get('snippet')[:500]}{('...' if len(source.get('snippet')) > 500 else '')}"
                        )
                elif source_type == "document":
                    st.markdown(f"**Document:** {source.get('document_id', 'N/A')}")
                    if source.get("page"):
                        st.markdown(f"**Page:** {source.get('page')}")
                    if source.get("snippet"):
                        st.markdown(
                            f"**Excerpt:** {source.get('snippet')[:500]}{('...' if len(source.get('snippet')) > 500 else '')}"
                        )
                else:
                    st.markdown(str(source))
    else:
        st.info("No sources available.")

    # Display citations with better formatting
    st.markdown("---")
    st.markdown("## Citations")
    citations = result.get("citations", [])
    if citations:
        st.success(f"{len(citations)} citation(s) generated")
        citation_format = st.selectbox(
            "Select Citation Format",
            ["APA", "MLA", "Chicago"],
            key="citation_format",
            help="Choose your preferred citation style",
        )

        from backend.core.citation_manager import CitationManager

        citation_manager = CitationManager()
        citation_manager.citations = citations

        formatted_citations = citation_manager.format_citations(
            format_type=citation_format.lower()
        )

        st.markdown("---")
        for i, citation in enumerate(formatted_citations, 1):
            st.markdown(f"**{i}.** {citation}")
        # Provide download option
        citation_text = "\n".join(formatted_citations)
        st.download_button(
            "Download Citations",
            data=citation_text,
            file_name="citations.txt",
            mime="text/plain",
        )
    else:
        st.info("No citations available.")
