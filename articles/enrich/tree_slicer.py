from abc import ABC, abstractmethod


class TreeSlicer(ABC):
    @abstractmethod
    def slice(self, commodity_group: str | None, commodity_classification: str | None) -> str: ...
