import logging
from anthropic import Anthropic
from typing import Literal, Optional
from .protocol import AIProvider
from read_audio.errors import ProcessedTextError
from read_audio.constants import (
    DEFAULT_ANTRHOPIC_MODEL,
    DEFAULT_SUMMARY_PROMPT,
    DEFAULT_CONDENSE_PROMPT,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    def __init__(self, model: str = DEFAULT_ANTRHOPIC_MODEL):
        self.client = Anthropic()  # type: ignore
        self.model = model

    def process_text(self, text: str, mode: Literal["summary", "condense"], prompt: Optional[str] = None) -> str:
        if not text:
            raise ProcessedTextError("Empty text provided for processing")

        system_prompt = prompt if prompt else (
            DEFAULT_SUMMARY_PROMPT if mode == "summary" else DEFAULT_CONDENSE_PROMPT
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
                system=system_prompt,
            )

            if not response.content:
                raise ProcessedTextError("Empty response from Anthropic API")

            result = response.content[0].text
            if not result:
                raise ProcessedTextError("Empty text in Anthropic API response")

            return result

        except Exception as e:
            raise ProcessedTextError(f"Anthropic processing failed: {str(e)}")

    def summarize(self, text: str) -> str:
        return self.process_text(text, "summary")

    def condense(self, text: str) -> str:
        return self.process_text(text, "condense")
