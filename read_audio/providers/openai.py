import logging
from openai import OpenAI
from typing import Literal, Optional
from .protocol import AIProvider
from read_audio.errors import ProcessedTextError
from read_audio.constants import (
    DEFAULT_OPENAI_MODEL,
    DEFAULT_SUMMARY_PROMPT,
    DEFAULT_CONDENSE_PROMPT,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    def __init__(self, model: str = DEFAULT_OPENAI_MODEL):
        self.client = OpenAI()
        self.model = model

    def process_text(self, text: str, mode: Literal["summary", "condense"], prompt: Optional[str] = None) -> str:
        if not text:
            raise ProcessedTextError("Empty text provided for processing")

        system_prompt = prompt if prompt else (
            DEFAULT_SUMMARY_PROMPT if mode == "summary" else DEFAULT_CONDENSE_PROMPT
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                temperature=0.7,
            )

            if not response.choices:
                raise ProcessedTextError("No completion choices returned from OpenAI")

            result = response.choices[0].message.content
            if not result:
                raise ProcessedTextError("Empty response content from OpenAI")

            return result

        except Exception as e:
            raise ProcessedTextError(f"OpenAI processing failed: {str(e)}")

    def summarize(self, text: str) -> str:
        return self.process_text(text, "summary")

    def condense(self, text: str) -> str:
        return self.process_text(text, "condense")
