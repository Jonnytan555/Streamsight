import pandas as pd
from io import StringIO
from requests import Response
from scraper.response.response_handler import ResponseHandler

class CsvResponseHandler(ResponseHandler):
    def __init__(
        self,
        delimiter: str = ",",
        skip_rows: int = 0,
        encoding: str = "utf-8"
    ):
        self.delimiter = delimiter
        self.skip_rows = skip_rows
        self.encoding = encoding

    def handle(self, response: Response) -> pd.DataFrame:
        csv_data = StringIO(response.text)

        df = pd.read_csv(
            csv_data,
            delimiter=self.delimiter,
            skiprows=self.skip_rows,
            encoding=self.encoding
        )

        return df