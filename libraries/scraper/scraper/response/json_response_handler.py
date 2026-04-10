import json
from requests import Response
import pandas as pd
from scraper.response.response_handler import ResponseHandler


class JsonResponseHandler(ResponseHandler):
    def handle(self, response: Response) -> pd.DataFrame :
        data = json.loads(response.text)
        if self.data_path:
            for path in self.data_path.split('.'):
                data = data[path]

        return pd.DataFrame.from_dict(data)