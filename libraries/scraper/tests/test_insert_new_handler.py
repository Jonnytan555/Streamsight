import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from scraper.persistence.db_insert_new_handler import DbInsertNewHandler

class TestDbInsertNewHandler(unittest.TestCase):

    def setUp(self):
        self.db_handler = DbInsertNewHandler(
            db_host="localhost",
            db_name="test_db",
            table_name="test_table",
            schema="dbo"
        )

    def test_handle_inserts_new_data(self):
        df = pd.DataFrame({
            "id": [1, 2],
            "name": ["Alice", "Bob"]
        })

        with patch.object(self.db_handler, '_db_engine') as mock_engine, \
             patch.object(self.db_handler, '_drop_temp_table') as mock_drop_temp_table, \
             patch.object(self.db_handler, '_check_table_exists') as mock_check_table_exists:
            mock_conn = MagicMock()
            mock_engine.return_value.begin.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.return_value.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
            mock_check_table_exists.return_value = False
            
            inserted_rows = self.db_handler.handle(df)

            self.assertEqual(len(inserted_rows), 2)
            self.assertEqual(inserted_rows[0], (1, "Alice"))
            self.assertEqual(inserted_rows[1], (2, "Bob"))
            mock_drop_temp_table.assert_called_once()

    def test_handle_no_new_data(self):
        df = pd.DataFrame({
            "id": [1, 2],
            "name": ["Alice", "Bob"]
        })

        with patch.object(self.db_handler, '_db_engine') as mock_engine, \
             patch.object(self.db_handler, '_drop_temp_table') as mock_drop_temp_table, \
             patch.object(self.db_handler, '_check_table_exists') as mock_check_table_exists:
            mock_conn = MagicMock()
            mock_engine.return_value.begin.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.return_value.fetchall.return_value = []
            mock_check_table_exists.return_value = False

            inserted_rows = self.db_handler.handle(df)

            self.assertEqual(len(inserted_rows), 0)
            mock_drop_temp_table.assert_called_once()

    def test_handle_exception_during_insert(self):
        df = pd.DataFrame({
            "id": [1, 2],
            "name": ["Alice", "Bob"]
        })

        with patch.object(self.db_handler, '_db_engine') as mock_engine, \
             patch.object(self.db_handler, '_drop_temp_table') as mock_drop_temp_table:
            mock_conn = MagicMock()
            mock_engine.return_value.begin.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.side_effect = Exception("Insert failed")

            with self.assertRaises(Exception) as context:
                self.db_handler.handle(df)

            self.assertTrue("Insert failed" in str(context.exception))
            mock_drop_temp_table.assert_called_once()

if __name__ == '__main__':
    unittest.main()