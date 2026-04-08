"""
cost_threshold
--------------
Decorator that checks LLM spend before allowing a function to run.
Mirrors the shape of mem_threshold / cpu_threshold exactly.

Usage:
    from tracking.cost_threshold import cost_threshold

    class WebCandidatePipeline:

        @cost_threshold(max_daily_usd=10.0)
        @retry(tries=3, delay=2, backoff=2)
        def run(self, settings):
            ...

Parameters:
    max_daily_usd     — spend limit in USD over the look-back window.
                        Also reads MAX_DAILY_LLM_SPEND_USD env var as fallback.
    period_hours      — look-back window in hours (default 24).
    wait_seconds      — how long to sleep between re-checks (default 60).
    timeout_seconds   — how long to wait before raising (default 0 = fail immediately).
                        Set > 0 if you want to wait for the budget window to roll over.
"""
import logging
import os
import time


class BudgetExceededError(Exception):
    pass


def cost_threshold(
    max_daily_usd: float | None = None,
    period_hours: int = 24,
    wait_seconds: int = 60,
    timeout_seconds: int = 0,
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            limit = max_daily_usd
            if limit is None:
                limit = float(os.getenv("MAX_DAILY_LLM_SPEND_USD", "50.0"))

            from utils.tracking.llm_usage_tracker import LlmUsageTracker
            tracker = LlmUsageTracker()

            spend = tracker.get_spend(hours=period_hours)
            if spend >= limit:
                logging.warning(
                    f"[cost_threshold] LLM spend ${spend:.4f} >= limit ${limit:.2f} "
                    f"over last {period_hours}h. Blocking."
                )
                if timeout_seconds == 0:
                    raise BudgetExceededError(
                        f"LLM budget exceeded: ${spend:.4f} >= ${limit:.2f} over last {period_hours}h."
                    )
                start_time = time.time()
                while spend >= limit and not _timedout(start_time, timeout_seconds):
                    time.sleep(wait_seconds)
                    spend = tracker.get_spend(hours=period_hours)
                if spend >= limit:
                    raise BudgetExceededError(
                        f"LLM budget exceeded and timed out waiting. "
                        f"Spend: ${spend:.4f} / limit: ${limit:.2f} over last {period_hours}h."
                    )
            else:
                logging.info(f"[cost_threshold] LLM spend ${spend:.4f} / ${limit:.2f} over last {period_hours}h. OK.")

            return func(*args, **kwargs)

        return wrapper
    return decorator


def _over_budget(tracker, limit: float, period_hours: int) -> bool:
    spend = tracker.get_spend(hours=period_hours)
    if spend >= limit:
        logging.warning(
            f"[cost_threshold] LLM spend ${spend:.4f} >= limit ${limit:.2f} "
            f"over last {period_hours}h. Blocking."
        )
        return True
    logging.info(f"[cost_threshold] LLM spend ${spend:.4f} / ${limit:.2f} over last {period_hours}h. OK.")
    return False


def _timedout(start_time: float, timeout_seconds: int) -> bool:
    if timeout_seconds == 0:
        return True   # fail immediately — don't wait
    return time.time() > start_time + timeout_seconds
