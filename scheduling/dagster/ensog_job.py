import os
import sys

from dagster import Definitions, ScheduleDefinition, job, op, DefaultScheduleStatus

_REPO_ROOT = os.environ.get("APP_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _REPO_ROOT)


@op
def run_ensog(_):
    from runners.db.ensog.run import run
    run()


@job
def ensog_job():
    run_ensog()


ensog_schedule = ScheduleDefinition(
    job=ensog_job,
    cron_schedule="0 */6 * * *",
    default_status=DefaultScheduleStatus.RUNNING,
)

defs = Definitions(
    jobs=[ensog_job],
    schedules=[ensog_schedule],
)
