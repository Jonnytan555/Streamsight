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
    
    def _prepare_data(
        self, new_df: pd.DataFrame, dropNa: bool, dtype=None, where: str = ""
    ) -> pd.DataFrame:
        """
            This will prepare the data to be saved in the database.
            1. Find new records that is not exists in existing data
            2. Find existing records that has changed (increase the version by 1 and set latest=True)
            3. Update existing record that has changed to latest=False
        Returns: Dataframe to be saved
        """
        existing_df = self._get_existing_records(where)

        try:
            logging.info("Trying to match new_df dtypes based on existing_df")
            new_df = new_df.astype(existing_df.dtypes.to_dict())
        except Exception as e:
            logging.warning(
                "Unable to match existing_df dtypes to new_def. Reason: %s", repr(e)
            )

        new_df.replace({np.nan: None}, inplace=True)
        existing_df.replace({np.nan: None}, inplace=True)

        # Find new records
        new_records_df = self._get_new_records_df(existing_df, new_df, dropNa)
        logging.info("Found %d new records", len(new_records_df))

        # Find existing records that have changed
        changed_records_df = self._get_changed_records_df(existing_df, new_df)
        logging.info("Found %d changed records", len(changed_records_df))

        unique_timestamp = pd.Timestamp.utcnow().strftime("%Y%m%d%H%M%S%f")
        temp_table_name = f"{self.table_name}_temp_{unique_timestamp}"
        
        if len(changed_records_df) > 0:
            # Set latest=False for existing data that has changed
            changed_records_df.to_sql(
                name=f"{temp_table_name}",
                schema=self.schema,
                con=self._get_sqlengine(),
                if_exists="replace",
                dtype=dtype,
            )
            on_keys = " AND ".join(
                [f"[target].{column} = [temp].{column}" for column in self.keys]
            )
            update_latest_sql = f"""
                UPDATE [target]
                SET [target].{self.latest_column} = 0         
                FROM {self.schema}.{self.table_name} AS [target]
                INNER JOIN {self.schema}.{temp_table_name} AS [temp]
                ON {on_keys}
            """

            with self._get_sqlengine().begin() as conn:
                conn.execute(sa.text(update_latest_sql))

        # Clean up temp table if exist
        try:
            drop_temp_sql = f"""
            IF OBJECT_ID('{self.schema}.{temp_table_name}') IS NOT NULL
            BEGIN
                    DROP TABLE {self.schema}.{temp_table_name}
            END
            """
            with self._get_sqlengine().begin() as conn:
                conn.execute(sa.text(drop_temp_sql))
        except Exception as e:
            # log but should not interrupt the process
            logging.error(
                "Failed to delete temp table %s.%s. Exception: %s",
                self.schema,
                temp_table_name,
                repr(e),
            )

        return pd.concat([new_records_df, changed_records_df])

    def _get_sqlengine(self):
        return sa.create_engine(
            f"mssql+pyodbc://{self.db_host}/{self.db_name}?driver={self.db_driver.replace(' ', '+')}"
        )

    def _get_existing_records(self, where: str = "") -> pd.DataFrame:
        columns_to_select = self.keys + self.columns_to_compare
        columns_to_select.extend([self.version_column, self.latest_column])
        columns_to_select = [
            f"[{col}]" for col in columns_to_select
        ]  # Add [] to the column name

        # Query to get latest version available in existing records
        sql_select = f"""
            SELECT {",".join(columns_to_select)}
            FROM
            (
                SELECT 
                    {",".join(columns_to_select)},
                    ROW_NUMBER() OVER (PARTITION BY {",".join(self.keys)} 
                    ORDER BY {self.version_column} DESC) [Rank]
                FROM {self.schema}.{self.table_name}
                {where}
            ) t WHERE t.[Rank] = 1
            """

        existing_df = pd.read_sql(
            sql=sa.text(sql_select), con=self._get_sqlengine().connect()
        )
        return existing_df

    def _round_decimals(self, merged_df: pd.DataFrame):
        if merged_df.empty:
            return merged_df
        try:
            for col in merged_df.columns:
                if isinstance(merged_df[col].iloc[0], float) or isinstance(
                    merged_df[col].iloc[0], Decimal
                ):
                    merged_df[col] = merged_df[col].apply(
                        lambda x: round(x, 10) if x else x
                    )
                    logging.debug(
                        "Column %s rounded to max 10 decimal places for comparison", col
                    )
            return merged_df
        except Exception as e:
            logging.warning(
                "Unable to round decimal places for comparison. Exception: %s", repr(e)
            )

    def _filter_changed_records(self, merged_df: pd.DataFrame, columns: list[str]):
        # This is to ensure when we compare, it uses the same precision between x and y
        merged_df = self._round_decimals(merged_df)

        # None/NaN behave differently when we want to compare x and y, hence replace with empty string for comparison
        merged_df = merged_df.replace({np.nan: None})
        merged_df = merged_df.replace({None: ""})

        changed_dfs = []
        for column in columns:
            df = merged_df.query(f"(`{column}_y` != `{column}_x`)")
            if df.empty:
                continue
            logging.info("The value of column %s has changed", column)
            changed_dfs.append(df)

        return (
            pd.concat(changed_dfs).drop_duplicates().replace({"": None})
            if len(changed_dfs) > 0
            else pd.DataFrame()
        )

    def _get_changed_records_df(
        self, left_df: pd.DataFrame, right_df: pd.DataFrame
    ) -> pd.DataFrame:
        merged_df = pd.merge(
            left=left_df, right=right_df, how="inner", on=self.keys, indicator=True
        )
        # Must exist in both existing and incoming data
        merged_df = merged_df.query('_merge=="both"')

        if merged_df.empty:
            return pd.DataFrame()

        changed_records_df = self._filter_changed_records(
            merged_df, self.columns_to_compare
        )

        if changed_records_df.empty:
            return pd.DataFrame()

        # Rename back the columns
        changed_records_df.rename(
            columns={f"{column}_y": f"{column}" for column in self.columns_to_compare},
            inplace=True,
        )

        # Set latest=True and increase version
        changed_records_df[self.latest_column] = True
        changed_records_df[self.version_column] = (
            changed_records_df[f"{self.version_column}_x"] + 1
        )

        # Drop other columns
        changed_records_df.drop(
            columns=[f"{column}_x" for column in self.columns_to_compare], inplace=True
        )
        changed_records_df.drop(
            columns=[
                "_merge",
                f"{self.version_column}_y",
                f"{self.latest_column}_y",
                f"{self.version_column}_x",
                f"{self.latest_column}_x",
            ],
            inplace=True,
            errors="ignore",
        )

        changed_records_df.replace({"": None}, inplace=True)

        return changed_records_df

    def _get_new_records_df(
        self, left_df: pd.DataFrame, right_df: pd.DataFrame, dropNa: bool = True
    ) -> pd.DataFrame:

        new_records_df = pd.merge(
            left=left_df, right=right_df, how="right", on=self.keys, indicator=True
        )
        new_records_df.query('_merge=="right_only"', inplace=True)
        new_records_df[self.version_column] = 1
        new_records_df[self.latest_column] = True
        new_records_df.rename(
            columns={f"{col}_y": f"{col}" for col in self.columns_to_compare},
            inplace=True,
        )
        new_records_df.drop(columns=["_merge"], inplace=True)
        new_records_df.drop(
            columns=[f"{col}_x" for col in self.columns_to_compare], inplace=True
        )
        new_records_df.drop(
            columns=[
                f"{self.latest_column}_x",
                f"{self.latest_column}_y",
                f"{self.version_column}_x",
                f"{self.version_column}_y",
            ],
            inplace=True,
            errors="ignore",
        )

        if dropNa:
            new_records_df.dropna(axis=0, inplace=True)

        return new_records_df