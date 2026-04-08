from articles.article_pipeline import ArticlePipeline
from articles.enrich.enrichment import Enrichment
from articles.enrich.queue_reader import QueueReader
from articles.enrich.article_summariser import ArticleSummariser
from articles.enrich.article_writer import ArticleWriter
from articles.enrich.tree_slicer import TreeSlicer
from articles.enrich.web.claude_summariser import ClaudeSummariser
from articles.enrich.db.concat_summariser import ConcatSummariser
from utils.tracking.budget_checker import LlmBudgetChecker


class WebEnrichment(Enrichment):
    """
    Enrichment for web sources.
    Uses ClaudeSummariser by default; falls back to ConcatSummariser in demo mode.
    Set DEMO_MODE=true in .env to run without an ANTHROPIC_API_KEY.
    """

    def __init__(self, tree_slicer: TreeSlicer | None = None, demo: bool = False) -> None:
        self.tree_slicer = tree_slicer
        self.demo = demo

    def run(self) -> None:
        if self.demo:
            summariser = ConcatSummariser()
            budget_checker = None
        else:
            summariser = ClaudeSummariser(tree_slicer=self.tree_slicer)
            budget_checker = LlmBudgetChecker()

        ArticlePipeline(
            reader=QueueReader(source_type="web"),
            enricher=ArticleSummariser(
                summariser=summariser,
                budget_checker=budget_checker,
            ),
            writer=ArticleWriter(),
        ).run()
