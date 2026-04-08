import os
import sqlalchemy as sa

APP_NAME = "commodity-news-tracker"
LOG_PATH = os.getenv("LOG_PATH", "/var/log/commodity-news-tracker")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")

# Database
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME   = os.getenv("DB_NAME", "COMMODITY_NEWS_TRACKER")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
engine    = sa.create_engine(f"mssql+pyodbc://{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER.replace(' ', '+')}")

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
MAX_AGE_DAYS = int(os.getenv("MAX_AGE_DAYS", "2"))
MAX_RESULTS_PER_TOPIC   = int(os.getenv("MAX_RESULTS_PER_TOPIC", "5"))
MAX_DAILY_LLM_SPEND_USD = float(os.getenv("MAX_DAILY_LLM_SPEND_USD", "10.0"))
COST_TRACKING_ENABLED   = os.getenv("COST_TRACKING_ENABLED", "true").lower() != "false"

#Rename the SQL Server database — run ALTER DATABASE STREAMSIGHT MODIFY NAME = COMMODITY_NEWS_TRACKER in SSMS
#Rename the folder — C:\Python\Streamsight → C:\Python\CommodityNewsTracker (optional, but keeps things tidy — update the Airflow DAG path constants after)