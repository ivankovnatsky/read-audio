import logging
from anthropic import Anthropic
from .protocol import AIProvider
from video_summarizer.errors import SummaryError
from video_summarizer.constants import DEFAULT_SUMMARY_PROMPT, DEFAULT_ANTRHOPIC_MODEL

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    def __init__(self, model: str = DEFAULT_ANTRHOPIC_MODEL):
        self.client = Anthropic()  # type: ignore
        self.model = model

    def summarize(self, text: str) -> str:
        if not text:
            raise SummaryError("Empty text provided for summarization")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=DEFAULT_SUMMARY_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
            )

            if not response.content:
                raise SummaryError("Empty response from Anthropic API")

            return response.content[0].text

        except Exception as e:
            raise SummaryError(f"Anthropic summarization failed: {str(e)}")
