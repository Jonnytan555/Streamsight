import logging
import os
import pandas as pd
from scraper.persistence.persistence_handler import PersistenceHandler


class CsvPersistenceHandler(PersistenceHandler):

    def __init__(self, filename: str, encoding="utf-8") -> None:
        super().__init__()
        self.filename = filename
        self.encoding = encoding

    def handle(self, new_df: pd.DataFrame, dropNa: bool = True):
        logging.info(f"Writing to csv {self.filename}...")

        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        new_df.to_csv(path_or_buf=self.filename, encoding=self.encoding, index=False)
        
        logging.info(f"Saved to {self.filename}.")
        return new_df