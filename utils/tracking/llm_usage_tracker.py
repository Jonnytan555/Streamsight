"""
LlmUsageTracker
---------------
Injectable tracker that records token usage and estimated cost to the
llm_usage table after every LLM API call.

Inject into any LLM client (PerplexitySearchListener, summarisers, etc.)
as a kwarg. If not injected, tracking is silently skipped.

Pricing (USD per token) — update when provider prices change:
  https://docs.perplexity.ai/docs/pricing
  https://www.anthropic.com/pricing
"""
import logging
from datetime import datetime, timedelta, timezone

import sqlalchemy as sa


# (provider, model) -> (input_usd_per_token, output_usd_per_token)
_PRICING: dict[tuple[str, str], tuple[float, float]] = {
    ("perplexity", "sonar"):                        (1.0 / 1_000_000,   1.0 / 1_000_000),
    ("perplexity", "sonar-pro"):                    (3.0 / 1_000_000,  15.0 / 1_000_000),
    ("perplexity", "sonar-reasoning"):              (5.0 / 1_000_000,  25.0 / 1_000_000),
    ("anthropic",  "claude-haiku-4-5-20251001"):    (0.25 / 1_000_000,  1.25 / 1_000_000),
    ("anthropic",  "claude-sonnet-4-6"):            (3.0 / 1_000_000,  15.0 / 1_000_000),
    ("anthropic",  "claude-opus-4-6"):              (15.0 / 1_000_000, 75.0 / 1_000_000),
}


def estimate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = _PRICING.get((provider, model))
    if pricing is None:
        logging.warning(f"[llm_tracker] No pricing found for {provider}/{model} — cost recorded as 0.0")
        return 0.0
    input_rate, output_rate = pricing
    return (input_tokens * input_rate) + (output_tokens * output_rate)


class LlmUsageTracker:
    def __init__(self, caller: str | None = None, engine=None) -> None:
        self.caller = caller
        if engine is None:
            from appsettings import engine as _default_engine
            engine = _default_engine
        self.engine = engine

    def record(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        caller: str | None = None,
    ) -> None:
        cost = estimate_cost(provider, model, input_tokens, output_tokens)
        try:
            with self.engine.begin() as conn:
                conn.execute(
                    sa.text("""
                        INSERT INTO llm_usage
                            (provider, model, caller, input_tokens, output_tokens, estimated_cost_usd)
                        VALUES
                            (:provider, :model, :caller, :input_tokens, :output_tokens, :estimated_cost_usd)
                    """),
                    {
                        "provider":           provider,
                        "model":              model,
                        "caller":             caller or self.caller,
                        "input_tokens":       input_tokens,
                        "output_tokens":      output_tokens,
                        "estimated_cost_usd": cost,
                    },
                )
            logging.info(
                f"[llm_tracker] {provider}/{model} — "
                f"in={input_tokens} out={output_tokens} cost=${cost:.6f}"
            )
        except Exception:
            logging.warning("[llm_tracker] Failed to record usage", exc_info=True)

    def get_spend(self, hours: int = 24) -> float:
        """Return total estimated cost in USD over the last N hours."""
        since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours)
        with self.engine.connect() as conn:
            result = conn.execute(
                sa.text("""
                    SELECT SUM(estimated_cost_usd)
                    FROM llm_usage
                    WHERE called_at >= :since
                """),
                {"since": since},
            ).scalar()
        return float(result or 0.0)

    def get_summary(self, hours: int = 24) -> list[dict]:
        """Return spend broken down by provider/model over the last N hours."""
        since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours)
        with self.engine.connect() as conn:
            rows = conn.execute(
                sa.text("""
                    SELECT provider, model,
                           SUM(input_tokens)       AS total_input,
                           SUM(output_tokens)      AS total_output,
                           SUM(estimated_cost_usd) AS total_cost,
                           COUNT(id)               AS calls
                    FROM llm_usage
                    WHERE called_at >= :since
                    GROUP BY provider, model
                """),
                {"since": since},
            ).fetchall()
        return [
            {
                "provider":      r.provider,
                "model":         r.model,
                "calls":         r.calls,
                "input_tokens":  r.total_input,
                "output_tokens": r.total_output,
                "cost_usd":      round(r.total_cost, 6),
            }
            for r in rows
        ]
