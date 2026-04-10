import json
import unittest
from unittest.mock import MagicMock
import pandas as pd
from scraper.scraper import Scraper


class MockHandler:
    def handle(self):
        pass


class TestScraper(unittest.TestCase):

    def test_scrape_should_request_then_handle_response_and_persist(self):

        fake_json_response = '{"fname": "Kate"}'
        fake_df = pd.json_normalize(json.loads(fake_json_response))
        
        request_handler = MockHandler()
        request_handler.handle = MagicMock(
            method="handle", return_value=fake_json_response)

        response_handler = MockHandler()
        response_handler.handle = MagicMock(
            method="handle", return_value=fake_df
        )

        persistence_handler = MockHandler()
        persistence_handler.handle = MagicMock(method="handle")

        scraper = Scraper(request_handler, response_handler, persistence_handler)
        scraper.scrape()

        request_handler.handle.assert_called_once()
        response_handler.handle.assert_called_once_with(fake_json_response)
        persistence_handler.handle.assert_called_once_with(fake_df, True, None, 'CreatedDate')