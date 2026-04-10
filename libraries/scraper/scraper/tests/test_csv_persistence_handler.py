import os
import unittest
from unittest import mock
import pandas as pd

from scraper.persistence.csv_persistence_handler import CsvPersistenceHandler

class TestCsvPersistanceHandler(unittest.TestCase):
    
    
    @mock.patch('os.makedirs')
    @mock.patch('pandas.DataFrame.to_csv')
    def test_handle_csv_persistence(self, mock_to_csv, mock_makedirs):
        # Setup
        data = {
            'x': [1, 2, 3],
            'y': [2, 3, 4]
        }
        fake_df = pd.DataFrame(data)
        
        # Act
        csv_handler = CsvPersistenceHandler(filename='C\\path\\to\\myfile.csv', encoding='utf-8')
        csv_handler.handle(fake_df)
        
        # Assert
        mock_makedirs.assert_called_with('C\\path\\to', exist_ok=True)
        mock_to_csv.assert_called_with(path_or_buf='C\\path\\to\\myfile.csv', encoding=csv_handler.encoding, index=False)