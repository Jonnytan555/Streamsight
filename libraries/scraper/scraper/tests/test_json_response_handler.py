import unittest
import pandas as pd
from scraper.response.json_response_handler import JsonResponseHandler



fake_data = {
    "data": [
        {"fname": "Joe", "name": "Doe"},
        {"fname": "Wendy", "name": "Byrde"}
    ]
}

class MockResponse:
    
    @property
    def text(self):
        return """{
            "data": [
                {"fname": "Joe", "name": "Doe"},
                {"fname": "Wendy", "name": "Byrde"}
            ]
        }
        """

class TestJsonResponseHandler(unittest.TestCase):
       
    def test_handle_json_response(self):
        
        handler = JsonResponseHandler()
        
        actual_df = handler.handle(MockResponse())
        
        expected_df = pd.DataFrame(fake_data)
        
        self.assertTrue(actual_df.equals(expected_df))
        
    
    def test_handle_json_with_data_path(self):
        # Look at data path
        handler = JsonResponseHandler('data')
        
        actual_df = handler.handle(MockResponse())
        
        expected_df = pd.DataFrame(fake_data["data"]) # look at the data path
        
        self.assertTrue(actual_df.equals(expected_df))