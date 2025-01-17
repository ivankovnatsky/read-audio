import logging
import json
import requests
from typing import Optional

from video_summarizer.constants import (
    DEFAULT_LLAMA_MODEL,
    DEFAULT_SUMMARY_PROMPT,
    OLLAMA_HOST,
)
from .protocol import AIProvider
from video_summarizer.errors import SummaryError

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    def __init__(
        self, model: str = DEFAULT_LLAMA_MODEL, max_tokens: Optional[int] = None
    ):
        """Initialize the Ollama provider."""
        self.model = model
        self.max_tokens = max_tokens
        self.host = OLLAMA_HOST

        # Verify Ollama service is running
        try:
            response = requests.get(f"{self.host}/api/version", timeout=5)
            response.raise_for_status()
            logger.info(f"Ollama version: {response.json().get('version')}")
        except requests.exceptions.RequestException as e:
            raise SummaryError(
                "Ollama service is not running. Please start it with 'ollama serve'"
            ) from e

    def summarize(self, text: str) -> str:
        """Summarize text using LLaMA via Ollama."""
        logger.info(f"Summarizing text with Ollama using model '{self.model}'")

        if not text:
            raise SummaryError("Empty text provided for summarization")

        request_body = {
            "model": self.model,
            "prompt": f"{DEFAULT_SUMMARY_PROMPT}\n\n---------------\n\n{text}",
            "stream": False,
        }

        if self.max_tokens:
            request_body["options"] = {"num_predict": self.max_tokens}

        try:
            logger.info(f"Making Ollama API request to {self.host}")
            response = requests.post(
                url=f"{self.host}/api/generate",
                json=request_body,
                timeout=None,
            )
            response.raise_for_status()

            response_data = response.json()
            summary = response_data.get("response", "")

            if not summary:
                raise SummaryError("Empty response from Ollama API")

            return summary

        except requests.exceptions.RequestException as e:
            raise SummaryError(
                f"Failed to communicate with Ollama API: {str(e)}"
            ) from e
        except (json.JSONDecodeError, KeyError) as e:
            raise SummaryError(f"Invalid response from Ollama API: {str(e)}") from e
