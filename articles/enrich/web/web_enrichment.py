from articles.article_pipeline import ArticlePipeline
from articles.enrich.enrichment import Enrichment
from articles.enrich.queue_reader import QueueReader
from articles.enrich.article_summariser import ArticleSummariser
from articles.enrich.article_writer import ArticleWriter
from articles.enrich.tree_slicer import TreeSlicer
from articles.enrich.web.claude_summariser import ClaudeSummariser
from utils.tracking.budget_checker import LlmBudgetChecker


class WebEnrichment(Enrichment):
    """
    Enrichment for web sources.
    Always uses ClaudeSummariser — LLM classifies and summarises article content.
    Budget is enforced before any LLM calls are made.
    tree_slicer scopes LLM classification to the runner's commodity domain.
    """

    def __init__(self, tree_slicer: TreeSlicer | None = None) -> None:
        self.tree_slicer = tree_slicer

    def run(self) -> None:
        ArticlePipeline(
            reader=QueueReader(source_type="web"),
            enricher=ArticleSummariser(
                summariser=ClaudeSummariser(tree_slicer=self.tree_slicer),
                budget_checker=LlmBudgetChecker(),
            ),
            writer=ArticleWriter(),
        ).run()
