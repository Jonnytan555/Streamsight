import logging
from abc import ABC, abstractmethod

import appsettings as _settings
from utils.tracking.cost_threshold import BudgetExceededError
from utils.tracking.llm_usage_tracker import LlmUsageTracker


class BudgetChecker(ABC):
    """Interface for budget enforcement before LLM calls."""

    @abstractmethod
    def check(self) -> None:
        """Raise BudgetExceededError if spend limit is exceeded."""


class LlmBudgetChecker(BudgetChecker):
    """Checks LLM spend against the configured daily limit."""

    def __init__(
        self,
        usage_tracker: LlmUsageTracker | None = None,
        max_daily_usd: float | None = None,
        enabled: bool | None = None,
    ) -> None:
        self.usage_tracker  = usage_tracker or LlmUsageTracker(caller="article_enrichment")
        self.max_daily_usd  = max_daily_usd  if max_daily_usd  is not None else _settings.MAX_DAILY_LLM_SPEND_USD
        self.enabled        = enabled        if enabled        is not None else _settings.COST_TRACKING_ENABLED

    def check(self) -> None:
        if not self.enabled:
            return
        spend = self.usage_tracker.get_spend(hours=24)
        if spend >= self.max_daily_usd:
            raise BudgetExceededError(
                f"LLM budget exceeded: ${spend:.4f} >= ${self.max_daily_usd:.2f} over last 24h."
            )
        logging.info("[budget] LLM spend $%.4f / $%.2f. OK.", spend, self.max_daily_usd)
