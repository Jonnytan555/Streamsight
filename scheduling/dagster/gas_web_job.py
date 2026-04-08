import os
import sys

from dagster import Definitions, ScheduleDefinition, job, op, DefaultScheduleStatus

_REPO_ROOT = os.environ.get("APP_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _REPO_ROOT)


@op
def run_gas_web(_):
    from runners.web.gas_web.run import run
    run()


@job
def gas_web_job():
    run_gas_web()


gas_web_schedule = ScheduleDefinition(
    job=gas_web_job,
    cron_schedule="0 */6 * * *",
    default_status=DefaultScheduleStatus.RUNNING,
)

defs = Definitions(
    jobs=[gas_web_job],
    schedules=[gas_web_schedule],
)
