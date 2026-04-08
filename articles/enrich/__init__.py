import os

from articles.enrich.db.db_enrichment import DbEnrichment
from articles.enrich.tree_slicer import TreeSlicer
from articles.enrich.web.web_enrichment import WebEnrichment


def enrich(tree_slicer: TreeSlicer | None = None) -> None:
    """
    Enrich all pending articles in the queue.

    Set DEMO_MODE=true in .env to skip Claude and use ConcatSummariser instead.
    Useful for testing without an ANTHROPIC_API_KEY.
    """
    demo = os.getenv("DEMO_MODE", "false").lower() == "true"

    DbEnrichment().run()
    WebEnrichment(tree_slicer=tree_slicer, demo=demo).run()
