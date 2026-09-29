"""
Web Search Tool for the Multi-Agent Research Platform.

Supports multiple search APIs:
- Tavily API (primary)
- Serper API (alternative)
"""

import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class WebSearchTool:
    """
    Web search tool that supports multiple search APIs.

    Primary: Tavily API
    Alternative: Serper API
    """

    def __init__(self, api_type: str = "tavily"):
        """
        Initialize the web search tool.

        Args:
            api_type: "tavily" or "serper"
        """
        self.api_type = api_type.lower()

        if self.api_type == "tavily":
            self.api_key = os.getenv("TAVILY_API_KEY")
            if not self.api_key:
                print("Warning: TAVILY_API_KEY not found. Web search will be limited.")
        elif self.api_type == "serper":
            self.api_key = os.getenv("SERPER_API_KEY")
            if not self.api_key:
                print("Warning: SERPER_API_KEY not found. Web search will be limited.")
        else:
            raise ValueError(
                f"Unsupported API type: {api_type}. Use 'tavily' or 'serper'"
            )

    def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search the web for information.

        Args:
            query: Search query
            max_results: Maximum number of results
            include_domains: Optional list of domains to include
            exclude_domains: Optional list of domains to exclude

        Returns:
            Dictionary with search results and sources
        """
        if self.api_type == "tavily":
            return self._search_tavily(
                query, max_results, include_domains, exclude_domains
            )
        elif self.api_type == "serper":
            return self._search_serper(
                query, max_results, include_domains, exclude_domains
            )
        else:
            return {
                "results": [],
                "sources": [],
                "error": f"Unsupported API type: {self.api_type}",
            }

    def _search_tavily(
        self,
        query: str,
        max_results: int,
        include_domains: Optional[List[str]],
        exclude_domains: Optional[List[str]],
    ) -> Dict[str, Any]:
        """Search using Tavily API."""
        if not self.api_key:
            return {
                "results": [],
                "sources": [],
                "error": "Tavily API key not configured",
            }

        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
            }

            if include_domains:
                payload["include_domains"] = include_domains
            if exclude_domains:
                payload["exclude_domains"] = exclude_domains

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()

            results = []
            sources = []

            for result in data.get("results", []):
                results.append(
                    {
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "score": result.get("score", 0.0),
                    }
                )
                sources.append(
                    {
                        "url": result.get("url", ""),
                        "title": result.get("title", ""),
                        "published_date": result.get("published_date"),
                    }
                )

            return {
                "results": results,
                "sources": sources,
                "query": query,
                "num_results": len(results),
            }

        except requests.exceptions.Timeout:
            return {
                "results": [],
                "sources": [],
                "error": "Tavily API timeout. Please try again.",
            }
        except requests.exceptions.RequestException as e:
            return {
                "results": [],
                "sources": [],
                "error": f"Tavily API error: {str(e)}",
            }
        except Exception as e:
            return {
                "results": [],
                "sources": [],
                "error": f"Unexpected error: {str(e)}",
            }

    def _search_serper(
        self,
        query: str,
        max_results: int,
        include_domains: Optional[List[str]],
        exclude_domains: Optional[List[str]],
    ) -> Dict[str, Any]:
        """Search using Serper API."""
        if not self.api_key:
            return {
                "results": [],
                "sources": [],
                "error": "Serper API key not configured",
            }

        try:
            url = "https://google.serper.dev/search"
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

            payload = {"q": query, "num": max_results}

            if include_domains:
                payload["gl"] = "us"  # Country code

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            results = []
            sources = []

            # Process organic results
            for result in data.get("organic", []):
                results.append(
                    {
                        "title": result.get("title", ""),
                        "content": result.get("snippet", ""),
                        "url": result.get("link", ""),
                        "score": 1.0,  # Serper doesn't provide scores
                    }
                )
                sources.append(
                    {
                        "url": result.get("link", ""),
                        "title": result.get("title", ""),
                        "published_date": result.get("date"),
                    }
                )

            return {
                "results": results,
                "sources": sources,
                "query": query,
                "num_results": len(results),
            }

        except requests.exceptions.Timeout:
            return {
                "results": [],
                "sources": [],
                "error": "Serper API timeout. Please try again.",
            }
        except requests.exceptions.RequestException as e:
            return {
                "results": [],
                "sources": [],
                "error": f"Serper API error: {str(e)}",
            }
        except Exception as e:
            return {
                "results": [],
                "sources": [],
                "error": f"Unexpected error: {str(e)}",
            }

    def format_results_for_agent(self, search_results: Dict[str, Any]) -> str:
        """
        Format search results for agent consumption.

        Args:
            search_results: Results from search() method

        Returns:
            Formatted string with search results
        """
        if search_results.get("error"):
            return f"Search error: {search_results['error']}"

        if not search_results.get("results"):
            return "No search results found."

        formatted = []
        formatted.append(f"Search Query: {search_results.get('query', 'Unknown')}\n")
        formatted.append(f"Found {search_results.get('num_results', 0)} results:\n")

        for i, result in enumerate(search_results.get("results", []), 1):
            formatted.append(f"\n[{i}] {result.get('title', 'No title')}")
            formatted.append(f"URL: {result.get('url', 'No URL')}")
            formatted.append(f"Content: {result.get('content', 'No content')[:300]}...")

        return "\n".join(formatted)
