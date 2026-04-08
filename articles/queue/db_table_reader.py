import logging

import sqlalchemy as sa


class DbTableReader:
    """Reads all rows from a SQL table and returns them as a list of dicts."""

    def __init__(self, engine: sa.engine.Engine, table: str, schema: str = "dbo") -> None:
        self.engine = engine
        self.table = table
        self.schema = schema

    def read(self) -> list[dict]:

        sql = f"SELECT * FROM [{self.schema}].[{self.table}]"

        logging.info("[DbTableReader] Reading from %s.%s", self.schema, self.table)
        
        with self.engine.connect() as conn:
            rows = conn.execute(sa.text(sql)).fetchall()
        
        logging.info("[DbTableReader] Read %d rows", len(rows))
        
        return [dict(r._mapping) for r in rows]
