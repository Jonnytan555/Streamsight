from abc import ABC, abstractmethod


class WebSearchReader(ABC):
    """
    Base interface for web search readers.

    Implementations call a specific search API (Perplexity, Google, etc.)
    and return a list of article dicts in a common shape for SearchResultMapper.
    """

    @abstractmethod
    def read(self) -> list[dict]:
        """Search and return a list of raw article dicts."""
