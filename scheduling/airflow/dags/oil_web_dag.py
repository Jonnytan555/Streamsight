import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Docker: set APP_ROOT=/app in docker-compose.yml
# Server: set APP_ROOT=/home/ubuntu/streamsight (or wherever the repo lives)
COMMODITY_NEWS_TRACKER_PATH = os.environ.get("APP_ROOT", "/app")

default_args = {
    "owner": "commodity-news-tracker",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def _run():
    sys.path.insert(0, COMMODITY_NEWS_TRACKER_PATH)
    from runners.web.oil_web.run import run
    run()


with DAG(
    dag_id="oil_web_search",
    description="Fetch oil market news via Perplexity and summarise with Claude",
    start_date=datetime(2026, 3, 27),
    schedule_interval="0 * * * *",  # every hour
    catchup=False,
    default_args=default_args,
    tags=["commodity-news-tracker", "oil", "web"],
) as dag:

    PythonOperator(
        task_id="run",
        python_callable=_run,
        execution_timeout=timedelta(minutes=30),
    )
