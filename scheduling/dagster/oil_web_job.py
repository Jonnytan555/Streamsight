import os
import sys

from dagster import Definitions, ScheduleDefinition, job, op, DefaultScheduleStatus

_REPO_ROOT = os.environ.get("APP_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _REPO_ROOT)


@op
def run_oil_web(_):
    from runners.web.oil_web.run import run
    run()


@job
def oil_web_job():
    run_oil_web()


oil_web_schedule = ScheduleDefinition(
    job=oil_web_job,
    cron_schedule="0 */6 * * *",
    default_status=DefaultScheduleStatus.RUNNING,
)

defs = Definitions(
    jobs=[oil_web_job],
    schedules=[oil_web_schedule],
)
