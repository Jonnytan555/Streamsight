import logging
import pandas as pd
from scraper.persistence.persistence_handler import PersistenceHandler
import sqlalchemy as sa
import random


class DbInsertNewHandler(PersistenceHandler):
    """
    Handler for inserting new data into a database table if it does not already exist.
    Attributes:
        db_host (str): The database host.
        db_name (str): The name of the database.
        table_name (str): The name of the table to insert data into.
        schema (str): The schema of the table.
        db_driver (str): The database driver to use. Defaults to "ODBC Driver 17 for SQL Server".
    Methods:
        __init__(db_host: str, db_name: str, table_name: str, schema: str, db_driver: str = "ODBC Driver 17 for SQL Server"):
            Initializes the DbInsertNewHandler with the given database connection details.
        handle(df: pd.DataFrame, dtype=None) -> None:
            Inserts data from a DataFrame into the database table if it does not already exist.
        _get_sqlengine():
            Creates and returns a SQLAlchemy engine for the database connection.
        _drop_temp_table():
            Drops the temporary table used during the insert operation.
    """

    def __init__(
        self,
        db_host: str,
        db_name: str,
        table_name: str,
        schema: str,
        db_driver: str = "ODBC Driver 17 for SQL Server",
    ) -> None:
        self.db_host = db_host
        self.db_name = db_name
        self.table_name = table_name
        self.schema = schema
        self.db_driver = db_driver

    def handle(
        self,
        new_df: pd.DataFrame,
        dropNa: bool = True,
        dtype=None,
        created_date_column: str = "CreatedDate",
    ) -> None:
        logging.info("Inserting new data into %s.%s...", self.schema, self.table_name)

        if dropNa:
            new_df.dropna(axis=0, inplace=True)

        # Insert to temp table
        temp_table_name = f"{self.table_name}_temp_{int(random.random() * 1e6)}"
        while self._check_table_exists(temp_table_name):
            temp_table_name = f"{self.table_name}_temp_{int(random.random() * 1e6)}"

        new_df.to_sql(
            temp_table_name,
            con=self._db_engine(),
            schema=self.schema,
            if_exists="replace",
            index=False,
            dtype=dtype,
        )

        columns = new_df.columns.tolist()
        columns_str = ", ".join([f"source.[{col}]" for col in columns])

        equality_conditions = [
            (
                f"ISNULL(CAST(target.[{col}] AS NVARCHAR), '') = ISNULL(CAST(source.[{col}] AS NVARCHAR), '')"
                if pd.api.types.is_numeric_dtype(new_df[col])
                else f"ISNULL(target.[{col}], '') = ISNULL(source.[{col}], '')"
            )
            for col in columns
        ]

        # Construct the INSERT query
        insert_query = f"""
        INSERT INTO {self.schema}.{self.table_name} ({columns_str})
        OUTPUT inserted.*
        SELECT {', '.join([f'source.[{col}]' for col in columns])}
        FROM {self.schema}.{temp_table_name} AS source
        WHERE NOT EXISTS (
            SELECT 1
            FROM {self.schema}.{self.table_name} AS target
            WHERE {" AND ".join(equality_conditions)}
        )
        """
        try:
            with self._db_engine().begin() as conn:
                result = conn.execute(sa.text(insert_query))
                inserted_rows = result.fetchall()
                logging.info("Inserted %d new rows", len(inserted_rows))
        except Exception as e:
            logging.error("Failed to insert new data. Exception: %s", repr(e))
            raise
        finally:
            self._drop_temp_table(temp_table_name)

        return inserted_rows

    def _db_engine(self):
        return sa.create_engine(
            f"mssql+pyodbc://{self.db_host}/{self.db_name}?driver={self.db_driver.replace(' ', '+')}"
        )

    def _drop_temp_table(self, temp_table_name: str) -> None:
        temp_table = temp_table_name or f"{self.table_name}_temp"

        try:
            drop_temp_sql = f"""
            IF OBJECT_ID('{self.schema}.{temp_table}') IS NOT NULL
            BEGIN
                    DROP TABLE {self.schema}.{temp_table}
            END
            """
            with self._db_engine().begin() as conn:
                conn.execute(sa.text(drop_temp_sql))

        except Exception as e:
            # log but should not interrupt the process
            logging.error(
                "Failed to delete temp table %s.%s_temp. Exception: %s",
                self.schema,
                temp_table,
                repr(e),
            )

    def _check_table_exists(self, temp_table_name: str) -> bool:
        try:
            check_table_sql = f"""
                    SELECT 1
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = '{self.schema}'
                    AND TABLE_NAME = '{temp_table_name}'
                    """
            with self._db_engine().begin() as conn:
                result = conn.execute(sa.text(check_table_sql))
                return result.fetchone() is not None
        except Exception as e:
            logging.warning(
                "Failed to check if table exists. Assuming it does not. Exception: %s",
                repr(e),
            )
            return False