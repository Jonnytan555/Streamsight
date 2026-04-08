import logging

import sqlalchemy as sa

from articles.article_pipeline import ArticlePipeline
from articles.queue.db.db_table_reader import DbTableReader
from articles.queue.db.column_mapper import ColumnMapper
from articles.queue.queue_writer import QueueWriter


class SourceQueuer:
    """
    Reads rows from an external DB table, maps them to article_queue shape,
    and writes them as status='pending' for enrichment.

    column_map values can be:
      - a string literal:  "api"
      - a callable:        lambda r: f"{r['GasDate']}_{r['FacilityId']}"
    """

    def __init__(
        self,
        source_engine: sa.engine.Engine,
        source_table: str,
        column_map: dict,
        source_schema: str = "dbo",
        where: str | None = None,
    ) -> None:
        self.source_engine = source_engine
        self.source_table = source_table
        self.column_map = column_map
        self.source_schema = source_schema
        self.where = where

    def run(self) -> None:
        logging.info("[SourceQueuer] Queuing from %s.%s", self.source_schema, self.source_table)

        ArticlePipeline(
            reader=DbTableReader(
                engine=self.source_engine,
                table=self.source_table,
                schema=self.source_schema,
                where=self.where,
            ),
            enricher=ColumnMapper(column_map=self.column_map),
            writer=QueueWriter(),
        ).run()
