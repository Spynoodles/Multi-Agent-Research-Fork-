"""
Evaluator Agent for the Multi-Agent Research Platform.

Assesses research quality using evaluation pattern:
- Score completeness, accuracy, relevance
- Provide improvement suggestions
- Rate overall quality
"""

from typing import Any, Dict, Optional

from .base_agent import BaseAgent


class EvaluatorAgent(BaseAgent):
    """
    Agent specialized in evaluating research quality.

    Uses evaluation pattern (LLM-as-a-Judge) to:
    - Score research on multiple dimensions
    - Provide improvement suggestions
    - Rate overall quality
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Evaluator Agent.

        Args:
            model_name: Model name (if None, uses env vars: OPENROUTER_MODEL or defaults to gpt-4)
            temperature: LLM temperature (lower for more consistent evaluation)
            api_key: API key (if not provided, uses env var: OPENROUTER_API_KEY or GEMINI_API_KEY)
        """
        system_prompt = """You are a research quality evaluator. Your role is to assess 
research reports on multiple dimensions:

1. Completeness (0-10): Does the report fully address the query?
2. Accuracy (0-10): Are the facts correct and well-verified?
3. Relevance (0-10): Is the information relevant to the query?
4. Clarity (0-10): Is the report well-written and easy to understand?
5. Source Quality (0-10): Are the sources reliable and appropriate?
   - CRITICAL: If information is explicitly cited from "Uploaded Documents" or "[Doc X]", treat these as authoritative sources provided by the user. Do NOT flag them as hallucinations or "future-dated" just because they are not in your training data or mention dates up to the current date.
   - Web sources should be evaluated for credibility (ArXiv, official docs, etc.).
6. Citation Quality (0-10): Are citations properly included and formatted?

Provide specific scores for each dimension, an overall average score, and actionable 
suggestions for improvement."""

        super().__init__(
            role="Evaluator",
            system_prompt=system_prompt,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
        )

    def process(
        self, report: str, query: str, sources_count: int = 0
    ) -> Dict[str, Any]:
        """
        Evaluate a research report.

        Args:
            report: Research report to evaluate
            query: Original research query
            sources_count: Number of sources used

        Returns:
            Dictionary with evaluation scores and feedback
        """
        evaluation_input = f"""Research Query: {query}

Research Report:
{report}

Number of Sources: {sources_count}

Evaluate this research report on the following dimensions (0-10 scale):

1. Completeness: Does the report fully address the query?
2. Accuracy: Are the facts correct and well-verified?
3. Relevance: Is the information relevant to the query?
4. Clarity: Is the report well-written and easy to understand?
5. Source Quality: Are the sources reliable and appropriate?
6. Citation Quality: Are citations properly included and formatted?

Provide:
- Score for each dimension (0-10)
- Overall average score
- Specific strengths
- Specific weaknesses
- Actionable improvement suggestions

Format your response clearly with scores and explanations."""

        evaluation_text = self._invoke(evaluation_input)

        # Extract scores
        scores = self._extract_scores(evaluation_text)

        # Calculate average
        if scores:
            average_score = sum(scores.values()) / len(scores)
        else:
            average_score = 5.0

        return {
            "evaluation_text": evaluation_text,
            "scores": scores,
            "average_score": average_score,
            "query": query,
            "sources_count": sources_count,
            "strengths": self._extract_section(evaluation_text, "strength"),
            "weaknesses": self._extract_section(evaluation_text, "weakness"),
            "suggestions": self._extract_section(evaluation_text, "suggestion"),
        }

    def _extract_scores(self, evaluation_text: str) -> Dict[str, float]:
        """Extract dimension scores from evaluation text."""
        import re

        scores = {}
        dimensions = [
            "completeness",
            "accuracy",
            "relevance",
            "clarity",
            "source quality",
            "citation quality",
        ]

        text_lower = evaluation_text.lower()

        for dimension in dimensions:
            # Look for patterns like "completeness: 8" or "completeness 8/10"
            patterns = [
                rf"{dimension}[:\s]+(\d+(?:\.\d+)?)",
                rf"{dimension}[:\s]+(\d+(?:\.\d+)?)/10",
                rf"{dimension}[:\s]+(\d+(?:\.\d+)?)\s+out\s+of\s+10",
            ]

            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        score = float(match.group(1))
                        if score > 10:
                            score = score / 10.0
                        scores[dimension] = min(max(score, 0.0), 10.0)
                        break
                    except ValueError:
                        continue

        return scores

    def _extract_section(self, text: str, section_type: str) -> str:
        """Extract a specific section from evaluation text."""
        import re

        patterns = [
            rf"{section_type}s?[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)",
            rf"{section_type}[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)",
        ]

        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""
