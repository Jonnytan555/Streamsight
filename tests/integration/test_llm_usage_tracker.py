import sqlalchemy as sa
from utils.tracking.llm_usage_tracker import LlmUsageTracker, estimate_cost


def test_estimate_cost_known_model():
    # Arrange / Act
    cost = estimate_cost("anthropic", "claude-haiku-4-5-20251001", 1000, 500)

    # Assert
    assert cost > 0


def test_estimate_cost_unknown_model_returns_zero():
    # Arrange / Act
    cost = estimate_cost("unknown", "unknown-model", 1000, 500)

    # Assert
    assert cost == 0.0


def test_record_writes_to_db(sqlite_engine):
    # Arrange
    tracker = LlmUsageTracker(caller="test", engine=sqlite_engine)

    # Act
    tracker.record("anthropic", "claude-haiku-4-5-20251001", 100, 50)

    # Assert
    with sqlite_engine.connect() as conn:
        row = conn.execute(sa.text("SELECT * FROM llm_usage")).fetchone()
    assert row is not None
    assert row.provider == "anthropic"
    assert row.input_tokens == 100


def test_get_spend_sums_costs(sqlite_engine):
    # Arrange
    tracker = LlmUsageTracker(caller="test", engine=sqlite_engine)
    tracker.record("anthropic", "claude-haiku-4-5-20251001", 1000, 500)
    tracker.record("anthropic", "claude-haiku-4-5-20251001", 1000, 500)

    # Act
    spend = tracker.get_spend(hours=24)

    # Assert
    assert spend > 0


def test_get_spend_returns_zero_when_empty(sqlite_engine):
    # Arrange
    tracker = LlmUsageTracker(caller="test", engine=sqlite_engine)

    # Act
    spend = tracker.get_spend(hours=24)

    # Assert
    assert spend == 0.0
