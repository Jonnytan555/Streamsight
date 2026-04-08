"""
Demo script: scrape ENTSOG UMMs into the Scrape DB, then run the Streamsight ENSOG pipeline.

Usage:
    python -m runners.db.ensog.scrape_and_run

Requirements:
    - The Scrape DB must be accessible (Windows auth on localhost by default)
    - ANTHROPIC_API_KEY set in .env (or DEMO_MODE=true to skip Claude)
"""

import logging
import os
import sys
import traceback
from time import time

_HERE      = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, _REPO_ROOT)

from dotenv import load_dotenv
load_dotenv()

import runners.db.ensog.appsettings as settings
import utils.logger as logger

logger.setup_log(
    app=settings.APP_NAME,
    filename=os.path.join(settings.LOG_PATH, settings.APP_NAME + "_ensog_demo.log"),
    use_stream=True,
)


def scrape():
    """Step 1 — pull latest UMMs from ENTSOG API into the Scrape DB."""
    logging.info("── Step 1: Scraping ENTSOG API ──────────────────────────")
    from runners.db.ensog.scraper.ensog import scrape as _scrape
    inserted = _scrape(scrape_db_server=settings.SCRAPE_DB_SERVER)
    logging.info("Scrape complete — %d new records inserted.", inserted)


def run_pipeline():
    """Step 2 — queue and enrich from the freshly populated Scrape DB."""
    logging.info("── Step 2: Running Streamsight ENSOG pipeline ───────────")
    from runners.db.ensog.run import run
    run()


if __name__ == "__main__":
    try:
        start = time()
        scrape()
        run_pipeline()
        logging.info("Demo complete. Duration: %.1fs", time() - start)
    except Exception as e:
        logging.error([e, traceback.format_exc()])
        raise
