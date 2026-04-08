from abc import ABC, abstractmethod


class Enrichment(ABC):
    """
    Base interface for enrichment pipelines.
    Each implementation defines a fixed summarisation strategy for a source type.
    """

    @abstractmethod
    def run(self) -> None:
        """Read pending articles from queue, enrich, and write to articles table."""
