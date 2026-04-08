import os
import sys

from dagster import Definitions, ScheduleDefinition, job, op, DefaultScheduleStatus

_REPO_ROOT = os.environ.get("APP_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _REPO_ROOT)


@op
def run_ags_web(_):
    from runners.web.ags_web.run import run
    run()


@job
def ags_web_job():
    run_ags_web()


ags_web_schedule = ScheduleDefinition(
    job=ags_web_job,
    cron_schedule="0 */6 * * *",
    default_status=DefaultScheduleStatus.RUNNING,
)

defs = Definitions(
    jobs=[ags_web_job],
    schedules=[ags_web_schedule],
)
