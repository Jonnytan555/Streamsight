import unittest
from unittest import mock
import pandas as pd
from scraper.persistence.db_persistence_handler import DbPersistenceHandler

# Fake existing data available in db
fake_existing_data = {
    "fname": ["Leo", "Kate"],
    "lname": ["Messi", "May"],
    "addr": ["London", "Paris"],
    "phone_number": ["111", "222"],
    "version": [1, 1],
    "latest": [True, True],
}

# Fake new data received from API/web
fake_new_data = {
    "fname": ["Leo", "Kate", "Joe"],
    "lname": ["Andres", "May", "Green"],
    "addr": ["Miami", "Paris", "Jakarta"],
    "phone_number": ["111", "222", "333"],
}

# the expected new records should be returned, previuosly not exist in existing_data
expected_new_records = {
    "fname": ["Joe"],
    "lname": ["Green"],
    "addr": ["Jakarta"],
    "phone_number": ["333"],
    "version": [1],
    "latest": [True],
}

expected_changed_records = {
    "fname": ["Leo"],
    "lname": ["Andres"],
    "addr": ["Miami"],
    "phone_number": ["111"],
    "version": [2],  # version increased to 2
    "latest": [True],
}


class TestDbPersistenceHandler(unittest.TestCase):

    @mock.patch("sqlalchemy.create_engine")
    def test_get_connection(self, mock_engine):
        # Setup
        db_persistence_handler = self._get_mock_persistence_handler()

        # Act
        db_persistence_handler._get_sqlengine()

        # Assert
        mock_engine.assert_called_with(
            f"mssql+pyodbc://{db_persistence_handler.db_host}/{db_persistence_handler.db_name}?driver=ODBC+Driver+17+for+SQL+Server"
        )

    def test_get_new_records_df(self):
        # Setup
        exising_df = pd.DataFrame(fake_existing_data)
        new_df = pd.DataFrame(fake_new_data)

        db_persistence_handler = self._get_mock_persistence_handler()

        # Act
        actual_df = (
            db_persistence_handler._get_new_records_df(exising_df, new_df)
            .sort_index(axis=1)
            .reset_index(drop=True)
        )
        expected_df = (
            pd.DataFrame(expected_new_records).sort_index(axis=1).reset_index(drop=True)
        )

        # Assert the new df is as expected
        self.assertEqual(True, actual_df.equals(expected_df))

    def test_get_changed_records_df(self):
        # Setup
        exising_df = pd.DataFrame(fake_existing_data)
        new_df = pd.DataFrame(fake_new_data)

        db_persistence_handler = self._get_mock_persistence_handler()

        new_df[db_persistence_handler.version_column] = 1
        new_df[db_persistence_handler.latest_column] = True

        # Act
        actual_df = (
            db_persistence_handler._get_changed_records_df(exising_df, new_df)
            .sort_index(axis=1)
            .reset_index(drop=True)
        )
        expected_df = (
            pd.DataFrame(expected_changed_records)
            .sort_index(axis=1)
            .reset_index(drop=True)
        )

        # Assert the new df is as expected
        self.assertEqual(True, actual_df.equals(expected_df))

    @mock.patch("sqlalchemy.create_engine")
    @mock.patch("sqlalchemy.text")
    @mock.patch("pandas.read_sql")
    def test_get_existing_records(
        self, mock_read_sql, mock_sql_text, mock_create_engine
    ):

        # Setup
        sql = """
            SELECT fname,lname,addr,phone_number,version,latest
            FROM
            (
                SELECT 
                    fname,lname,addr,phone_number,version,latest,
                    ROW_NUMBER() OVER (PARTITION BY fname ORDER BY version DESC) [Rank]
                FROM dbo.customer
            ) t WHERE t.[Rank] = 1
            """
        mock_create_engine.return_value = mock.MagicMock()
        mock_create_engine.connect = mock.MagicMock(method="connect")
        mock_read_sql.return_value = pd.DataFrame(fake_existing_data)
        mock_sql_text.return_value = sql

        db_handler = self._get_mock_persistence_handler()
        actual_df = db_handler._get_existing_records()

        expected_df = pd.DataFrame(fake_existing_data)

        mock_read_sql.assert_called_with(
            sql=sql,
            con=mock_create_engine.return_value.connect(),
        )

        self.assertEqual(True, actual_df.equals(expected_df))

    @mock.patch(
        "scraper.persistence.db_persistence_handler.DbPersistenceHandler._get_existing_records"
    )
    @mock.patch("sqlalchemy.create_engine")
    def test_prepare_data(
        self, mock_create_engine, mock_get_existing_records
    ):
        # Setup
        mock_create_engine.return_value = mock.MagicMock()
        mock_create_engine.return_value.begin = mock.MagicMock(method="begin")
        mock_get_existing_records.return_value = pd.DataFrame(fake_existing_data)

        db_handler = self._get_mock_persistence_handler()

        # Setup
        new_df = pd.DataFrame(fake_new_data)
        new_df[db_handler.version_column] = 1
        new_df[db_handler.latest_column] = True
        actual_df = db_handler._prepare_data(new_df, dropNa=True)

        # We expect to get the new records and changed records
        expected_df = pd.concat(
            [pd.DataFrame(expected_new_records), pd.DataFrame(expected_changed_records)]
        )

        # Assert
        mock_create_engine.return_value.begin.assert_called()
        self.assertTrue(True, actual_df.equals(expected_df))

    def _get_mock_persistence_handler(self):
        return DbPersistenceHandler(
            db_host="db-host",
            db_name="my-db",
            table_name="customer",
            schema="dbo",
            keys=["fname"],
            columns_to_compare=[
                "lname",
                "addr",
                "phone_number",
            ],
            version_column="version",
            latest_column="latest",
        )