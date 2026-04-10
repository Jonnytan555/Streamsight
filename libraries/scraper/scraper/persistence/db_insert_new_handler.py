import logging
import uuid

import pandas as pd
import sqlalchemy as sa


class DbInsertNewHandler:
    """
    Inserts rows from a DataFrame into a SQL Server table, skipping rows that
    already exist based on key_cols. Returns the newly inserted rows as a list
    of dicts.

    Usage:
        class MyWriter(DbInsertNewHandler):
            def __init__(self, engine=None):
                super().__init__(
                    engine=engine,
                    table_name="my_table",
                    schema="dbo",
                    key_cols=["source_type", "source_name", "record_id"],
                )
    """

    def __init__(
        self,
        engine: sa.Engine,
        table_name: str,
        schema: str,
        key_cols: list[str],
    ) -> None:
        self.engine = engine
        self.table_name = table_name
        self.schema = schema
        self.key_cols = key_cols

    def _insert_new(self, df: pd.DataFrame) -> list[dict]:
        if df is None or df.empty:
            return []

        temp = f"{self.table_name}_tmp_{uuid.uuid4().hex[:12]}"
        columns = df.columns.tolist()
        col_list = ", ".join(f"[{c}]" for c in columns)
        src_cols = ", ".join(f"source.[{c}]" for c in columns)
        join_clause = " AND ".join(
            f"target.[{c}] = source.[{c}]" for c in self.key_cols
        )

        insert_sql = f"""
            INSERT INTO [{self.schema}].[{self.table_name}] ({col_list})
            OUTPUT inserted.*
            SELECT {src_cols}
            FROM [{self.schema}].[{temp}] AS source
            WHERE NOT EXISTS (
                SELECT 1 FROM [{self.schema}].[{self.table_name}] AS target
                WHERE {join_clause}
            )
        """

        drop_sql = f"""
            IF OBJECT_ID('[{self.schema}].[{temp}]') IS NOT NULL
                DROP TABLE [{self.schema}].[{temp}]
        """

        try:
            df.to_sql(
                temp,
                con=self.engine,
                schema=self.schema,
                if_exists="replace",
                index=False,
            )

            with self.engine.begin() as conn:
                result = conn.execute(sa.text(insert_sql))
                rows = result.fetchall()
                keys = result.keys()

            inserted = [dict(zip(keys, row)) for row in rows]
            logging.info("[DbInsertNewHandler] Inserted %d new rows into %s.%s",
                         len(inserted), self.schema, self.table_name)
            return inserted

        except Exception:
            logging.exception("[DbInsertNewHandler] Failed to insert into %s.%s",
                              self.schema, self.table_name)
            raise

        finally:
            try:
                with self.engine.begin() as conn:
                    conn.execute(sa.text(drop_sql))
            except Exception:
                logging.warning("[DbInsertNewHandler] Failed to drop temp table %s", temp)
