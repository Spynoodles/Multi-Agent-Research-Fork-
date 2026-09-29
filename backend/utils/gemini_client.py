"""Gemini LLM client utility using LangChain's GooglePalm (API key).

This helper constructs a LangChain `GooglePalm` chat model using an
API key from the `GEMINI_API_KEY` environment variable.
"""

import os
from typing import Any, Dict, Optional

# Import at top level to avoid E402
from langchain.chat_models import init_chat_model

# DEBUG: snapshot at import time


def create_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
) -> object:
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")
    gemini_model = model_name or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    fallback_model = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite")

    # Clean approach: prefer direct use of google.genai when a GEMINI API key
    # is provided to avoid any LangChain/provider code paths that may default
    # to other providers or vendored model names.
    if gemini_key:
        try:
            import google.genai as genai

            client = genai.Client(api_key=gemini_key)

            class _GenAIWrapper:
                def __init__(self, client, model, temperature=None):
                    self.client = client
                    self.model = model
                    self.temperature = temperature

                def invoke(self, messages: list):
                    # Convert LangChain messages to a simple string prompt for this demo wrapper
                    # In a real app, you'd map SystemMessage/HumanMessage to genai's structure
                    prompt = ""
                    for msg in messages:
                        if hasattr(msg, "content"):
                            prompt += f"{msg.content}\n"
                        else:
                            prompt += f"{str(msg)}\n"
                    
                    models_to_try = [self.model]
                    if fallback_model and fallback_model not in models_to_try:
                        models_to_try.append(fallback_model)

                    last_error = None
                    for model in models_to_try:
                        try:
                            response = self.client.models.generate_content(
                                model=model, contents=prompt
                            )
                            break
                        except Exception as error:
                            last_error = error
                            status_code = getattr(error, "status_code", None)
                            error_text = str(error).upper()
                            retryable = status_code in {429, 500, 502, 503, 504}
                            retryable = retryable or any(
                                marker in error_text
                                for marker in ("429", "500", "502", "503", "504", "UNAVAILABLE")
                            )
                            if not retryable:
                                raise
                    else:
                        raise last_error
                    
                    # Mock a LangChain-like response object with a .content attribute
                    class _Response:
                        def __init__(self, content):
                            self.content = content
                    
                    return _Response(response.text)

            return _GenAIWrapper(client, gemini_model, temperature)
        except Exception:
            # If google.genai isn't available, fall back to LangChain below.
            pass

    # Fallback: try LangChain google_genai provider if available
    try:
        import importlib.util

        if importlib.util.find_spec("langchain_google_genai"):
            from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

            llm_kwargs: Dict[str, Any] = {"model": gemini_model}
            if temperature is not None:
                llm_kwargs["temperature"] = temperature
            if gemini_key is not None:
                llm_kwargs["api_key"] = gemini_key
            return ChatGoogleGenerativeAI(**llm_kwargs)
    except Exception:
        pass

    try:
        base_kwargs: Dict[str, Any] = {}
        if temperature is not None:
            base_kwargs["temperature"] = temperature
        if gemini_key:
            base_kwargs["api_key"] = gemini_key
        return init_chat_model(
            gemini_model, provider="google_genai", **base_kwargs
        )
    except Exception as e:  # pragma: no cover - environment dependent
        raise ImportError(
            "Could not initialize Gemini model. Install google-genai SDK or langchain-google-genai. Original error: "
            + str(e)
        )
