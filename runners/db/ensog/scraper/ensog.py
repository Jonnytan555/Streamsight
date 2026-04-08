"""
Standalone ENTSOG UMM scraper — no dependency on the WebScrapes scraper library.
Fetches from the ENTSOG Transparency Platform API and upserts into ENTSOGUrgentMarketMessages.
"""

import logging
import os
from datetime import datetime, timedelta

import httpx
import pandas as pd
import sqlalchemy as sa


_UMM_URL = "https://transparency.entsog.eu/api/v1/urgentMarketMessages"
_TABLE   = "ENTSOGUrgentMarketMessages"
_KEY_COL = "id"


def fetch(forward_days: int = 30) -> pd.DataFrame:
    """Pull raw UMM records from the ENTSOG Transparency Platform API."""
    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    to_date   = (datetime.now() + timedelta(days=forward_days)).strftime("%Y-%m-%d")

    params = {
        "messageType": "all",
        "from":        from_date,
        "to":          to_date,
        "timeZone":    "CET",
        "eventStatus": "All",
        "limit":       "-1",
        "indicator":   "UMM Data",
    }

    logging.info("Fetching ENTSOG UMMs from %s to %s", from_date, to_date)
    with httpx.Client(timeout=60) as client:
        r = client.get(_UMM_URL, params=params)
        r.raise_for_status()

    df = pd.DataFrame(r.json()["urgentMarketMessages"])
    logging.info("Fetched %d raw UMM records", len(df))
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to active, non-archived UMMs with a meaningful capacity impact."""
    df = df.copy()
    df["unavailableCapacity"] = pd.to_numeric(df["unavailableCapacity"], errors="coerce")

    df = df[
        (df["eventStatus"] == "Active") &
        (df["isArchived"] != "Yes") &
        (df["unavailableCapacity"].notna()) &
        (df["unavailableCapacity"] > 0)
    ].reset_index(drop=True)

    df["CreatedDate"] = pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M:%S")

    logging.info("%d UMM records after transform", len(df))
    return df


def upsert(df: pd.DataFrame, engine: sa.engine.Engine) -> int:
    """Insert rows that don't already exist (keyed on 'id')."""
    if df.empty:
        logging.info("No records to upsert.")
        return 0

    with engine.connect() as conn:
        existing = pd.read_sql(
            sa.text(f"SELECT [{_KEY_COL}] FROM dbo.[{_TABLE}]"), conn
        )[_KEY_COL].tolist()

    new_rows = df[~df[_KEY_COL].isin(existing)]
    if new_rows.empty:
        logging.info("No new UMM records to insert.")
        return 0

    new_rows.to_sql(_TABLE, engine, schema="dbo", if_exists="append", index=False)
    logging.info("Inserted %d new UMM records.", len(new_rows))
    return len(new_rows)


def scrape(scrape_db_server: str, forward_days: int = 30) -> int:
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server").replace(" ", "+")
    engine = sa.create_engine(
        f"mssql+pyodbc://{scrape_db_server}/Scrape?driver={driver}&trusted_connection=yes"
    )
    df = fetch(forward_days)
    df = transform(df)
    return upsert(df, engine)
