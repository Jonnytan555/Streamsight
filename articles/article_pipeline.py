class ArticlePipeline:
    """
    Orchestrates a three-step data pipeline for this app:
      reader   — fetches data from a source
      enricher — transforms / summarises the data
      writer   — persists the result
    """

    def __init__(self, reader, enricher, writer) -> None:
        self.reader  = reader
        self.enricher = enricher
        self.writer  = writer

    def run(self) -> None:
        data   = self.reader.read()
        result = self.enricher.enrich(data)
        self.writer.write(result)
