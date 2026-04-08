import logging
import os
import sys
import traceback
from time import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from dotenv import load_dotenv

load_dotenv()
import runners.web.ags_web.appsettings as settings

import logger
logger.setup_log(
    app=settings.APP_NAME,
    filename=os.path.join(settings.LOG_PATH, settings.APP_NAME + "_ags_web.log"),
    use_stream=True,
)

from runners.web.ags_web.prompts import AGS_MARKET, COMMODITY_TREE
from articles.enrich.web.web_tree_slicer import WebTreeSlicer
from articles.queue.web.perplexity_search import PerplexitySearch
from articles.queue.web.search_result_mapper import SearchResultMapper
from articles.queue.queue_writer import QueueWriter
from articles.article_pipeline import ArticlePipeline
from articles.enrich import enrich


def run():
    try:
        start = time()

        ArticlePipeline(
            reader=PerplexitySearch(
                api_key=settings.PERPLEXITY_API_KEY,
                topics=[{
                    "query":                    AGS_MARKET,
                    "sector":                   settings.SECTOR,
                    "commodity_group":          settings.COMMODITY_GROUP,
                    "commodity_classification": settings.COMMODITY_CLASSIFICATION,
                    "market_region":            settings.MARKET_REGION,
                }],
                source_name=settings.SOURCE_NAME,
                model=settings.SEARCH_MODEL,
                max_age_days=settings.MAX_AGE_DAYS,
                max_results_per_topic=settings.MAX_RESULTS_PER_TOPIC,
                domains=settings.DOMAINS,
            ),
            enricher=SearchResultMapper(
                sector=settings.SECTOR,
                market_region=settings.MARKET_REGION,
                commodity_group=settings.COMMODITY_GROUP,
                commodity_classification=settings.COMMODITY_CLASSIFICATION,
            ),
            writer=QueueWriter(),
        ).run()

        enrich(tree_slicer=WebTreeSlicer(COMMODITY_TREE))

        logging.info(f"Finished {settings.APP_NAME} ags_web. Duration: {time() - start:.1f}s")

    except Exception as e:
        logging.error([e, traceback.format_exc()])
        raise


if __name__ == "__main__":
    run()
