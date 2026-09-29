"""
Fact-Checker Agent for the Multi-Agent Research Platform.

Verifies information accuracy using guardrails pattern:
- Cross-reference multiple sources
- Identify contradictions
- Flag uncertain information
- Provide confidence scores
"""

from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent


class FactCheckerAgent(BaseAgent):
    """
    Agent specialized in verifying information accuracy.

    Uses guardrails pattern to:
    - Cross-reference multiple sources
    - Identify contradictions
    - Flag uncertain information
    - Provide confidence scores
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Fact-Checker Agent.

        Args:
            model_name: Model name (if None, uses env vars: OPENROUTER_MODEL or defaults to gpt-4)
            temperature: LLM temperature (lower for more consistent verification)
            api_key: API key (if not provided, uses env var: OPENROUTER_API_KEY or GEMINI_API_KEY)
        """
        system_prompt = """You are a fact-checking specialist. Your role is to verify 
information accuracy by:
1. Cross-referencing information across multiple sources
2. Identifying contradictions or inconsistencies
3. Flagging uncertain or unverified claims
4. Providing confidence scores for each fact
5. Suggesting additional verification when needed

Be thorough and conservative. When in doubt, flag information as uncertain."""

        super().__init__(
            role="Fact-Checker",
            system_prompt=system_prompt,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
        )

    def process(
        self, findings: Dict[str, Any], sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify facts from research findings.

        Args:
            findings: Research findings from Researcher Agent
            sources: List of sources used

        Returns:
            Dictionary with verified facts, confidence scores, and flags
        """
        # Prepare verification prompt
        verification_input = f"""Research Findings:
{findings.get("synthesized_findings", "")}

Sources Used:
{self._format_sources(sources)}

Please verify the accuracy of the research findings by:
1. Cross-referencing claims across sources
2. Identifying any contradictions
3. Flagging uncertain or unverified information
4. Providing confidence scores (0-10) for key facts
5. Suggesting areas that need additional verification

Format your response as:
- Verified Facts: [list of verified facts with confidence scores]
- Contradictions: [any contradictions found]
- Uncertain Claims: [claims that need more verification]
- Overall Confidence: [0-10 score]
- Recommendations: [suggestions for improvement]"""

        verification_result = self._invoke(verification_input)

        # Extract confidence score
        confidence_score = self._extract_confidence_score(verification_result)

        return {
            "verification_report": verification_result,
            "confidence_score": confidence_score,
            "sources_checked": len(sources),
            "findings": findings,
            "verified": confidence_score >= 7.0,
        }

    def verify_claim(self, claim: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify a specific claim against sources.

        Args:
            claim: Specific claim to verify
            sources: List of sources to check against

        Returns:
            Verification result with confidence score
        """
        verification_input = f"""Claim to verify: {claim}

Sources:
{self._format_sources(sources)}

Verify this claim by:
1. Checking if sources support the claim
2. Identifying any contradictions
3. Providing a confidence score (0-10)
4. Explaining your reasoning"""

        verification_result = self._invoke(verification_input)
        confidence_score = self._extract_confidence_score(verification_result)

        return {
            "claim": claim,
            "verification": verification_result,
            "confidence_score": confidence_score,
            "verified": confidence_score >= 7.0,
        }

    def _format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources for the prompt."""
        formatted = []
        for i, source in enumerate(sources, 1):
            source_type = source.get("type", "unknown")
            if source_type == "web":
                formatted.append(
                    f"[{i}] Web: {source.get('title', 'Unknown')} - {source.get('url', 'No URL')}"
                )
            elif source_type == "document":
                formatted.append(
                    f"[{i}] Document: {source.get('document_id', 'Unknown')} (Page {source.get('page', 'N/A')})"
                )

        return "\n".join(formatted) if formatted else "No sources provided"

    def _extract_confidence_score(self, verification_text: str) -> float:
        """Extract confidence score from verification text."""
        import re

        # Look for "confidence: X" or "score: X" patterns
        patterns = [
            r"confidence[:\s]+(\d+(?:\.\d+)?)",
            r"score[:\s]+(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)/10",
            r"(\d+(?:\.\d+)?) out of 10",
        ]

        for pattern in patterns:
            match = re.search(pattern, verification_text.lower())
            if match:
                try:
                    score = float(match.group(1))
                    # Normalize to 0-10 scale if needed
                    if score > 10:
                        score = score / 10.0
                    return min(max(score, 0.0), 10.0)
                except ValueError:
                    continue

        # Default to medium confidence if not found
        return 5.0
