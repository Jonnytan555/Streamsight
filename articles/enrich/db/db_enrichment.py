from articles.article_pipeline import ArticlePipeline
from articles.enrich.enrichment import Enrichment
from articles.enrich.queue_reader import QueueReader
from articles.enrich.article_summariser import ArticleSummariser
from articles.enrich.article_writer import ArticleWriter
from articles.enrich.db.concat_summariser import ConcatSummariser


class DbEnrichment(Enrichment):
    """
    Enrichment for all non-web sources.
    Always uses ConcatSummariser — no LLM, passes body text through as-is.
    """

    def run(self) -> None:
        ArticlePipeline(
            reader=QueueReader(source_type="database"),
            enricher=ArticleSummariser(summariser=ConcatSummariser()),
            writer=ArticleWriter(),
        ).run()
