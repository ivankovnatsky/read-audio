import logging
from openai import OpenAI
from .protocol import AIProvider
from video_summarizer.errors import SummaryError
from video_summarizer.constants import DEFAULT_OPENAI_MODEL, DEFAULT_SUMMARY_PROMPT

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    def __init__(self, model: str = DEFAULT_OPENAI_MODEL):
        self.client = OpenAI()
        self.model = model

    def summarize(self, text: str) -> str:
        if not text:
            raise SummaryError("Empty text provided for summarization")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": DEFAULT_SUMMARY_PROMPT,
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                temperature=0.7,
            )

            if not response.choices:
                raise SummaryError("No completion choices returned from OpenAI")

            return response.choices[0].message.content

        except Exception as e:
            raise SummaryError(f"OpenAI summarization failed: {str(e)}")
