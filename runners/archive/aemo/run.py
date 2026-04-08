import logging
import os
import sys
import traceback
from time import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from dotenv import load_dotenv

load_dotenv()

import runners.db.archive.aemo.appsettings as settings
import runners.db.archive.aemo.mapper as mapper

import utils.logger as logger
logger.setup_log(
    app=settings.APP_NAME,
    filename=os.path.join(settings.LOG_PATH, settings.APP_NAME + "_aemo.log"),
    use_stream=True,
)

from articles.queue.source_queuer import SourceQueuer
from articles.enrich import enrich


def run():
    try:
        start = time()

        SourceQueuer(
            source_engine=settings.DB_ENGINE,
            source_table=settings.SOURCE_TABLE,
            column_map={
                "source_type":              settings.SOURCE_TYPE,
                "source_name":              settings.SOURCE_NAME,
                "source_record_id":         mapper.record_id,
                "source_url":               settings.SOURCE_URL,
                "title":                    mapper.title,
                "body_text":                mapper.body,
                "published_at":             mapper.published_at,
                "sector":                   settings.SECTOR,
                "market_region":            settings.MARKET_REGION,
                "commodity_group":          settings.COMMODITY_GROUP,
                "commodity_classification": settings.COMMODITY_CLASSIFICATION,
                "commodity_name":           settings.COMMODITY_NAME,
            },
        ).run()

        enrich()

        logging.info(f"Finished {settings.APP_NAME} aemo. Duration: {time() - start:.1f}s")

    except Exception as e:
        logging.error([e, traceback.format_exc()])
        raise


if __name__ == "__main__":
    run()
