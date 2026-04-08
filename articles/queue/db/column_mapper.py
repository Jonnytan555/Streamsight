import pandas as pd

_REQUIRED_COLS = [
    "source_type", "source_name", "source_record_id", "source_url",
    "title", "body_text", "published_at", "sector",
    "market_region", "commodity_group", "commodity_classification",
]

_OPTIONAL_COLS = ["commodity_name"]


class ColumnMapper:
    """
    Maps a list of raw DB rows to the article_queue column shape
    using a caller-supplied column_map.

    column_map keys are article_queue column names (snake_case).
    Values are either a string literal or a callable that receives
    the row dict and returns the value.
    """

    def __init__(self, column_map: dict) -> None:
        missing = [col for col in _REQUIRED_COLS if col not in column_map]
        if missing:
            raise ValueError(f"[ColumnMapper] missing required keys: {missing}")
        self.column_map = column_map

    def enrich(self, rows: list[dict]) -> pd.DataFrame:
        all_cols = _REQUIRED_COLS + [c for c in _OPTIONAL_COLS if c in self.column_map]
        result = []
        for raw in rows:
            row = {}
            for col in all_cols:
                mapping = self.column_map.get(col)
                row[col] = mapping(raw) if callable(mapping) else mapping
            result.append(row)
        return pd.DataFrame(result)
