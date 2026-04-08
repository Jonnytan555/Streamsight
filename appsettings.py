import os
import sqlalchemy as sa

APP_NAME = "commodity-news-tracker"
LOG_PATH = os.path.join(os.path.dirname(__file__), "logs")
EMAIL_RECIPIENTS = ""
SMTP_HOST        = ""

# Database — all values from env so local runners and server API point to the same instance
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME   = os.getenv("DB_NAME",   "STREAMSIGHT")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_USER   = os.getenv("DB_USER",   "")
DB_PASS   = os.getenv("DB_PASS",   "")

from utils.db import build_engine
engine = build_engine(server=DB_SERVER, database=DB_NAME, driver=DB_DRIVER, user=DB_USER, password=DB_PASS)

# API keys — set in .env only
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")

# Article deduplication key — shared by QueueWriter and ArticleWriter
QUEUE_KEY_COLS   = ["source_type", "source_name", "source_record_id"]
ARTICLE_KEY_COLS = ["source_type", "source_name", "record_id"]

# Perplexity tuning
MAX_AGE_DAYS            = 2
MAX_RESULTS_PER_TOPIC   = 5
MAX_DAILY_LLM_SPEND_USD = 1.0
COST_TRACKING_ENABLED   = True

