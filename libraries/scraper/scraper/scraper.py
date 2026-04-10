from scraper.persistence.persistence_handler import PersistenceHandler
from scraper.request.request_handler import RequestHandler
from scraper.response.response_handler import ResponseHandler


class Scraper:

    def __init__(self, 
                 request_handler: RequestHandler,
                 response_handler: ResponseHandler,
                 persistence_handler: PersistenceHandler) -> None:
        self.request_handler = request_handler
        self.response_handler = response_handler
        self.persistence_handler = persistence_handler

    def scrape(self,
               dropNa: bool = True,
               dtype=None,
               created_date_column: str = 'CreatedDate'):

        response = self.request_handler.handle()

        result = self.response_handler.handle(response)

        return self.persistence_handler.handle(result, dropNa, dtype, created_date_column)