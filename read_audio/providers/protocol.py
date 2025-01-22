from typing import Protocol, Literal, Optional


class AIProvider(Protocol):
    """Protocol for AI providers that can generate summaries"""

    def process_text(self, text: str, mode: Literal["summary", "condense"], prompt: Optional[str] = None) -> str:
        """Process text in either summary or condense mode with optional custom prompt"""
        pass

    def summarize(self, text: str) -> str:
        """Generate a summary of the given text"""
        return self.process_text(text, "summary")

    def condense(self, text: str) -> str:
        """Generate a condensed version of the given text"""
        return self.process_text(text, "condense")
