from articles.enrich.db.db_enrichment import DbEnrichment
from articles.enrich.tree_slicer import TreeSlicer
from articles.enrich.web.web_enrichment import WebEnrichment


def enrich(tree_slicer: TreeSlicer | None = None) -> None:
    DbEnrichment().run()
    WebEnrichment(tree_slicer=tree_slicer).run()
