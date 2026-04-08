"""
DomainTracker
-------------
Tracks which search domains return results and auto-blocks those that
consistently return nothing (likely paywalled or blocking scrapers).

A domain is auto-blocked after `block_after_zeros` consecutive zero-result runs.
Blocked domains are excluded from future searches.
"""
import logging
from datetime import datetime, timezone

import sqlalchemy as sa
from appsettings import engine


class DomainTracker:
    def __init__(self, block_after_zeros: int = 3) -> None:
        self.block_after_zeros = block_after_zeros

    def get_active_domains(self, domains: list[str]) -> list[str]:
        """Return domains that are not blocked."""
        if not domains:
            return []
        placeholders = ", ".join(f":d{i}" for i in range(len(domains)))
        params = {f"d{i}": d for i, d in enumerate(domains)}
        with engine.connect() as conn:
            blocked = {
                row[0] for row in conn.execute(
                    sa.text(f"""
                        SELECT domain FROM blocked_domains
                        WHERE blocked_at IS NOT NULL
                          AND domain IN ({placeholders})
                    """),
                    params,
                ).fetchall()
            }
        active = [d for d in domains if d not in blocked]
        if blocked:
            logging.info(f"[domain_tracker] Skipping {len(blocked)} blocked domain(s): {blocked}")
        return active

    def record_results(self, domain: str, article_count: int) -> None:
        """Record how many articles a domain returned. Auto-blocks on consecutive zeros."""
        with engine.begin() as conn:
            existing = conn.execute(
                sa.text("SELECT id, consecutive_zero_runs FROM blocked_domains WHERE domain = :domain"),
                {"domain": domain},
            ).fetchone()

            now = datetime.now(timezone.utc).replace(tzinfo=None)

            if not existing:
                conn.execute(
                    sa.text("""
                        INSERT INTO blocked_domains (domain, consecutive_zero_runs, last_checked_at)
                        VALUES (:domain, :zeros, :now)
                    """),
                    {"domain": domain, "zeros": 0 if article_count > 0 else 1, "now": now},
                )
                return

            if article_count > 0:
                conn.execute(
                    sa.text("""
                        UPDATE blocked_domains
                        SET consecutive_zero_runs = 0, last_checked_at = :now
                        WHERE domain = :domain
                    """),
                    {"domain": domain, "now": now},
                )
            else:
                new_zeros = existing.consecutive_zero_runs + 1
                blocked_at = now if new_zeros >= self.block_after_zeros else None

                conn.execute(
                    sa.text("""
                        UPDATE blocked_domains
                        SET consecutive_zero_runs = :zeros,
                            last_checked_at = :now,
                            blocked_at = COALESCE(blocked_at, :blocked_at),
                            reason = CASE WHEN :blocked_at IS NOT NULL
                                         THEN :reason ELSE reason END
                        WHERE domain = :domain
                    """),
                    {
                        "domain":     domain,
                        "zeros":      new_zeros,
                        "now":        now,
                        "blocked_at": blocked_at,
                        "reason":     f"Auto-blocked after {new_zeros} consecutive zero-result runs",
                    },
                )
                if blocked_at:
                    logging.warning(f"[domain_tracker] Auto-blocked {domain} after {new_zeros} zero-result runs")
