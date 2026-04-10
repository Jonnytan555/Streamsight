from decimal import Decimal

import pandas as pd
import sqlalchemy as sa
import logging
import numpy as np

from scraper.persistence.persistence_handler import PersistenceHandler

class DbPersistenceHandler(PersistenceHandler):

    def __init__(
        self,
        db_host: str,
        db_name: str,
        table_name: str,
        schema: str,
        keys: list[str],
        columns_to_compare: list[str],
        version_column: str,
        latest_column: str,
        db_driver: str = "ODBC Driver 17 for SQL Server",
    ) -> None:
        self.db_host = db_host
        self.db_name = db_name
        self.table_name = table_name
        self.schema = schema
        self.keys = keys
        self.columns_to_compare = columns_to_compare
        self.version_column = version_column
        self.latest_column = latest_column
        self.db_driver = db_driver

    def handle(
        self,
        new_df: pd.DataFrame,
        dropNa: bool = True,
        dtype=None,
        created_date_column: str = "CreatedDate",
        where: str = "",
    ):
        if new_df is None or new_df.empty:
            logging.info("No data to be saved.")
            return

        logging.info("Initialising new data with version and latest flag...")
        new_df[self.version_column] = 1
        new_df[self.latest_column] = True

        logging.info("Preparing data to be saved...")
        result_df = self._prepare_data(new_df, dropNa, dtype, where=where)

        if len(result_df) == 0:
            logging.info("No data to be saved.")
            return

        result_df[created_date_column] = pd.Timestamp.utcnow().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        logging.info(
            "Persist data to database %s %s.%s.%s...",
            self.db_host,
            self.db_name,
            self.schema,
            self.table_name,
        )
        result_df.to_sql(
            name=self.table_name,
            schema=self.schema,
            if_exists="append",
            con=self._get_sqlengine(),
            index=False,
            dtype=dtype,
        )
        logging.info("Completed.")
        return result_df