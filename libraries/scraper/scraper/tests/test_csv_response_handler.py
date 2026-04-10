import unittest
import pandas as pd
from scraper.response.csv_response_handler import CsvResponseHandler


class MockCsvResponse:
    
    @property
    def text(self):
        return """name,age
                Jon,30
                Alice,25
                """


class MockCsvWithHeaderResponse:
    
    @property
    def text(self):
        return """Metadata line
                name,age
                Jon,30
                Alice,25
                """


class TestCsvResponseHandler(unittest.TestCase):

    def test_handle_basic_csv(self):
        handler = CsvResponseHandler()
        
        actual_df = handler.handle(MockCsvResponse())
        
        expected_df = pd.DataFrame({
            "name": ["Jon", "Alice"],
            "age": [30, 25]
        })
        
        self.assertTrue(actual_df.equals(expected_df))


    def test_handle_csv_with_skip_rows(self):
        handler = CsvResponseHandler(skip_rows=1)
        
        actual_df = handler.handle(MockCsvWithHeaderResponse())
        
        expected_df = pd.DataFrame({
            "name": ["Jon", "Alice"],
            "age": [30, 25]
        })
        
        self.assertTrue(actual_df.equals(expected_df))


    def test_handle_csv_column_cleaning(self):
        class MockMessyCsvResponse:
            @property
            def text(self):
                return """ Name , Age 
                Jon,30
                Alice,25
                """
        
        handler = CsvResponseHandler(clean_columns=True)
        
        actual_df = handler.handle(MockMessyCsvResponse())
        
        expected_df = pd.DataFrame({
            "name": ["Jon", "Alice"],
            "age": [30, 25]
        })
        
        self.assertTrue(actual_df.equals(expected_df))