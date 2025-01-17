from typing import Protocol


class AIProvider(Protocol):
    """Protocol for AI providers that can generate summaries"""

    def summarize(self, text: str) -> str:
        """Generate a summary of the given text"""

        pass
