"""
Base Agent class for all agents in the Multi-Agent Research Platform.

This provides common functionality like LLM initialization, prompt templates,
and error handling that all agents share.
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# LangChain imports (modern core messages API)
from langchain_core.messages import HumanMessage, SystemMessage

from ..utils.gemini_client import create_llm

load_dotenv()


class BaseAgent(ABC):
    """
    Base class for all agents in the research platform.

    Provides common functionality:
    - LLM initialization and configuration
    - Prompt template management
    - Error handling
    - Output parsing
    """

    def __init__(
        self,
        role: str,
        system_prompt: str,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the base agent.

        Args:
            role: The role/name of this agent
            system_prompt: System prompt defining the agent's behavior
            model_name: Gemini model name (if None, uses GEMINI_MODEL env var or defaults to gemini-3.5-flash-lite)
            temperature: Temperature for LLM responses
            api_key: Gemini API key (if not provided, uses GEMINI_API_KEY env var)
        """
        self.role = role
        
        # Add current date to system prompt to prevent temporal hallucinations
        import datetime
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.system_prompt = f"Today's date is {current_date}.\n\n{system_prompt}"

        # Initialize LLM client via LangChain factory
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = (
            model_name or os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite"
        )
        _m = (self.model_name or "").lower()
        if _m.startswith("gpt-") or ("gemini" not in _m):
            self.model_name = "gemini-3.5-flash-lite"
        self.temperature = temperature
        self.llm: Any = create_llm(
            model_name=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
        )

        # Determine parameter name based on model
        if self.model_name.startswith("gpt-5"):
            self.max_tokens_param = "max_completion_tokens"
        else:
            self.max_tokens_param = "max_tokens"

    def _invoke(self, input_text: str, **kwargs) -> str:
        """
        Invoke the agent's chain with input and optional context.

        Args:
            input_text: The input text for the agent
            **kwargs: Additional context variables for the prompt

        Returns:
            Agent's response as string
        """
        try:
            # Build LangChain messages
            messages: list[Any] = [SystemMessage(content=self.system_prompt)]
            # Optional context insertion
            if "context" in kwargs and kwargs["context"]:
                messages.append(HumanMessage(content=f"Context: {kwargs['context']}"))
            messages.append(HumanMessage(content=input_text))

            # Call the LangChain ChatGemini instance (v1+ API)
            # Use .invoke(...) instead of calling the object directly
            try:
                response = self.llm.invoke(messages)
            except AttributeError:
                # Fallback for older LangChain versions
                response = self.llm(messages)

            # Extract content from LangChain response
            if hasattr(response, "content"):
                return response.content
            # ChatGemini may return an AIMessage or object with 'generations'
            if hasattr(response, "generations"):
                try:
                    return response.generations[0][0].text
                except Exception:
                    pass
            # Fallback to string representation
            return str(response)

        except Exception as e:
            error_msg = f"[{self.role}] Error processing request: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg) from e

    @abstractmethod
    def process(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Process a request. Must be implemented by subclasses.

        Returns:
            Dictionary with agent's output and metadata
        """
        pass

    def get_role(self) -> str:
        """Get the agent's role."""
        return self.role
