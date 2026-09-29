"""
Main Orchestrator for the Multi-Agent Research Platform.

Coordinates all agents and manages the research workflow.
"""

from typing import Any, Callable, Dict, List, Optional

from .agents.evaluator_agent import EvaluatorAgent
from .agents.fact_checker_agent import FactCheckerAgent
from .agents.researcher_agent import ResearcherAgent
from .agents.synthesizer_agent import SynthesizerAgent
from .core.citation_manager import CitationManager
from .core.memory_manager import MemoryManager, ResearchSession
from .core.rag_system import RAGSystem
from .core.router import Router
from .tools.web_search import WebSearchTool


class ResearchOrchestrator:
    """
    Main orchestrator that coordinates all agents and manages research workflow.

    Workflow:
    1. Router determines research strategy
    2. Researcher Agent gathers information
    3. Fact-Checker Agent verifies facts
    4. Synthesizer Agent creates structured report
    5. Evaluator Agent assesses quality
    6. Memory Manager saves session
    """

    def __init__(
        self,
        rag_system: Optional[RAGSystem] = None,
        web_search_tool: Optional[WebSearchTool] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Research Orchestrator.

        Args:
            rag_system: RAG system for document retrieval
            web_search_tool: Web search tool
            model_name: Gemini model name (if None, uses GEMINI_MODEL env var or defaults to gemini-3.5-flash-lite)
            temperature: LLM temperature
            api_key: Gemini API key (if not provided, uses GEMINI_API_KEY env var)
        """
        # Initialize core systems
        # Initialize Router; only provide temperature if supplied
        self.router = Router(
            model_name=model_name, temperature=temperature, api_key=api_key
        )
        self.citation_manager = CitationManager()
        self.memory_manager = MemoryManager()

        # Initialize RAG if not provided
        if rag_system is None:
            self.rag_system = RAGSystem(api_key=api_key)
        else:
            self.rag_system = rag_system

        # Initialize web search if not provided
        self.web_search_tool: Optional[WebSearchTool]
        if web_search_tool is None:
            try:
                self.web_search_tool = WebSearchTool(api_type="tavily")
            except Exception:
                try:
                    self.web_search_tool = WebSearchTool(api_type="serper")
                except Exception:
                    print(
                        "Warning: No web search API configured. Web search will be disabled."
                    )
                    self.web_search_tool = None
        else:
            self.web_search_tool = web_search_tool

        # Initialize agents
        self.researcher_agent = ResearcherAgent(
            rag_system=self.rag_system,
            web_search_tool=self.web_search_tool,
            citation_manager=self.citation_manager,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
        )

        self.fact_checker_agent = FactCheckerAgent(
            model_name=model_name, temperature=temperature, api_key=api_key
        )

        self.synthesizer_agent = SynthesizerAgent(
            model_name=model_name, temperature=temperature, api_key=api_key
        )

        self.evaluator_agent = EvaluatorAgent(
            model_name=model_name, temperature=temperature, api_key=api_key
        )

    def research(
        self,
        query: str,
        use_web_search: bool = True,
        use_rag: bool = True,
        save_session: bool = True,
        on_progress: Optional[Callable[[int, str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive research using all agents.

        Args:
            query: Research query
            use_web_search: Whether to use web search
            use_rag: Whether to use RAG document retrieval
            save_session: Whether to save the research session
            on_progress: Optional callback for progress updates (agent_idx, status, message)

        Returns:
            Complete research result with report, citations, and quality scores
        """
        try:
            # Step 1: Router determines strategy
            if on_progress:
                on_progress(0, "active", "Analyzing query")
            
            routing = self.router.route(query)
            strategy = routing.get("strategy", {})

            # Override strategy with explicit parameters
            if not use_web_search:
                strategy["use_web_search"] = False
            if not use_rag:
                strategy["use_rag"] = False

            if on_progress:
                on_progress(0, "completed", "Strategy set")

            # Step 2: Researcher gathers information
            if on_progress:
                on_progress(1, "active", "Searching sources")
            
            research_findings = self.researcher_agent.process(
                query=query,
                use_web_search=strategy.get("use_web_search", True),
                use_rag=strategy.get("use_rag", True),
                max_web_results=strategy.get("max_web_results", 5),
                max_rag_results=strategy.get("max_rag_results", 5),
            )

            if on_progress:
                on_progress(1, "completed", f"Found {len(research_findings.get('sources', []))} sources")

            # Step 3: Fact-Checker verifies
            if on_progress:
                on_progress(2, "active", "Verifying facts")
            
            verified_findings = self.fact_checker_agent.process(
                findings=research_findings, sources=research_findings.get("sources", [])
            )

            if on_progress:
                on_progress(2, "completed", "Facts verified")

            # Step 4: Synthesizer creates report
            if on_progress:
                on_progress(3, "active", "Creating report")
            
            synthesized = self.synthesizer_agent.process(
                verified_findings=verified_findings, query=query
            )

            if on_progress:
                on_progress(3, "completed", "Report ready")

            # Step 5: Evaluator assesses quality
            # (No UI card for evaluator, but we can update status text)
            evaluation = self.evaluator_agent.process(
                report=synthesized.get("report", ""),
                query=query,
                sources_count=len(research_findings.get("sources", [])),
            )

            # Step 6: Create session and save
            session = None
            if save_session:
                session = self.memory_manager.create_session(query)
                self.memory_manager.save_session(
                    session=session,
                    report=synthesized.get("report", ""),
                    quality_scores=evaluation.get("scores", {}),
                    citations=self.citation_manager.get_all_citations(),
                )

            # Compile final result
            result = {
                "query": query,
                "report": synthesized.get("report", ""),
                "summary": synthesized.get("summary", ""),
                "sources": research_findings.get("sources", []),
                "citations": self.citation_manager.get_all_citations(),
                "quality_scores": evaluation.get("scores", {}),
                "average_quality_score": evaluation.get("average_score", 0.0),
                "evaluation": evaluation.get("evaluation_text", ""),
                "confidence_score": verified_findings.get("confidence_score", 0.0),
                "session_id": session.id if session else None,
                "strategy": strategy,
            }

            print("[Orchestrator] Research complete!")
            return result

        except Exception as e:
            error_msg = f"Research orchestration error: {str(e)}"
            print(f"[Orchestrator] Error: {error_msg}")

            # Try fallback: simpler workflow without fact-checking
            try:
                print("[Orchestrator] Attempting fallback workflow...")

                # Ensure strategy exists for fallback
                if not strategy:
                    strategy = {
                        "use_web_search": use_web_search,
                        "use_rag": use_rag,
                        "max_web_results": 3,
                        "max_rag_results": 3,
                        "complexity": "medium",
                    }

                research_findings = self.researcher_agent.process(
                    query=query,
                    use_web_search=use_web_search,
                    use_rag=use_rag,
                    max_web_results=3,
                    max_rag_results=3,
                )

                # Skip fact-checking, go straight to synthesis
                synthesized = self.synthesizer_agent.process(
                    verified_findings={
                        "findings": research_findings,
                        "confidence_score": 5.0,
                        "verification_report": "Fallback mode: Fact-checking skipped",
                    },
                    query=query,
                )

                # Basic evaluation
                evaluation = self.evaluator_agent.process(
                    report=synthesized.get("report", ""),
                    query=query,
                    sources_count=len(research_findings.get("sources", [])),
                )

                session = None
                if save_session:
                    session = self.memory_manager.create_session(query)
                    self.memory_manager.save_session(
                        session=session,
                        report=synthesized.get("report", ""),
                        quality_scores=evaluation.get("scores", {}),
                        citations=self.citation_manager.get_all_citations(),
                    )

                return {
                    "query": query,
                    "report": synthesized.get("report", ""),
                    "sources": research_findings.get("sources", []),
                    "citations": self.citation_manager.get_all_citations(),
                    "quality_scores": evaluation.get("scores", {}),
                    "average_quality_score": evaluation.get("average_score", 0.0),
                    "evaluation": evaluation.get("evaluation_text", ""),
                    "confidence_score": 5.0,
                    "session_id": session.id if session else None,
                    "strategy": strategy,
                    "warning": "Fallback mode: Some features may be limited",
                }

            except Exception as fallback_error:
                raise RuntimeError(
                    f"Research failed. Original error: {str(e)}. "
                    f"Fallback also failed: {str(fallback_error)}"
                ) from fallback_error

    def load_documents(
        self, documents: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Load documents into the RAG system.

        Args:
            documents: List of document texts
            metadata_list: Optional metadata for each document
        """
        self.rag_system.load_documents(documents, metadata_list)
        self.rag_system.save_vectorstore()

    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        """Get a research session by ID."""
        return self.memory_manager.get_session(session_id)

    def get_recent_sessions(self, limit: int = 10) -> List[ResearchSession]:
        """Get recent research sessions."""
        return self.memory_manager.get_recent_sessions(limit)

    def get_all_sessions(self) -> List[ResearchSession]:
        """Get all stored research sessions."""
        return self.memory_manager.get_all_sessions()
