import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

COMMODITY_NEWS_TRACKER_PATH = os.environ.get("APP_ROOT", "/app")

default_args = {
    "owner": "commodity-news-tracker",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def _run():
    sys.path.insert(0, COMMODITY_NEWS_TRACKER_PATH)
    from runners.db.ensog.run import run
    run()


with DAG(
    dag_id="ensog_umm",
    description="Fetch ENTSOG Urgent Market Messages and summarise with Claude",
    start_date=datetime(2026, 4, 6),
    schedule_interval="0 */6 * * *",
    catchup=False,
    default_args=default_args,
    tags=["commodity-news-tracker", "ensog", "gas", "europe"],
) as dag:

    PythonOperator(
        task_id="run",
        python_callable=_run,
        execution_timeout=timedelta(minutes=30),
    )
