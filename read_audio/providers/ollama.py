import logging
import json
import requests
from typing import Optional, Literal

from read_audio.constants import (
    DEFAULT_LLAMA_MODEL,
    DEFAULT_SUMMARY_PROMPT,
    DEFAULT_CONDENSE_PROMPT,
    OLLAMA_HOST,
)
from .protocol import AIProvider
from read_audio.errors import ProcessedTextError

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
            raise ProcessedTextError(
                "Ollama service is not running. Please start it with 'ollama serve'"
            ) from e

    def process_text(self, text: str, mode: Literal["summary", "condense"], prompt: Optional[str] = None) -> str:
        if not text:
            raise ProcessedTextError("Empty text provided for processing")

        system_prompt = prompt if prompt else (
            DEFAULT_SUMMARY_PROMPT if mode == "summary" else DEFAULT_CONDENSE_PROMPT
        )

        request_body = {
            "model": self.model,
            "prompt": f"""
                {system_prompt}
                ---------------
                {text}
            """,
            "stream": False,
        }

        if self.max_tokens:
            request_body["options"] = {"num_predict": self.max_tokens}

        try:
            response = requests.post(f"{self.host}/api/generate", json=request_body)
            response.raise_for_status()
            result = response.json()["response"]

            if not result:
                raise ProcessedTextError("Empty response from Ollama")

            return result

        except Exception as e:
            raise ProcessedTextError(f"Ollama processing failed: {str(e)}")

    def summarize(self, text: str) -> str:
        return self.process_text(text, "summary")

    def condense(self, text: str) -> str:
        return self.process_text(text, "condense")
