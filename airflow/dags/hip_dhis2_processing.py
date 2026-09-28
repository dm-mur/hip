from __future__ import annotations

import subprocess
from datetime import UTC, datetime

from airflow.sdk import DAG, task

SOURCE_INSTANCE = "live_test"
DBT_PROJECT_DIR = "/opt/hip/dbt"


def run_command(command: list[str], *, cwd: str | None = None) -> None:
    """Run an external HIP command and fail the Airflow task on error."""

    subprocess.run(
        command,
        cwd=cwd,
        check=True,
    )


with DAG(
    dag_id="hip_dhis2_processing",
    description="Process DHIS2 Bronze data through Silver, metadata reconciliation, and dbt",
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    schedule=None,
    catchup=False,
    tags=["hip", "dhis2"],
) as dag:

    @task
    def process_silver() -> None:
        run_command(
            [
                "hip",
                "process",
                "silver",
                "dhis2",
                "--source-instance",
                SOURCE_INSTANCE,
            ]
        )

    @task
    def reconcile_metadata() -> None:
        run_command(
            [
                "hip",
                "process",
                "metadata",
                "dhis2",
                "--source-instance",
                SOURCE_INSTANCE,
            ]
        )

    @task
    def build_analytics() -> None:
        run_command(
            ["dbt", "build"],
            cwd=DBT_PROJECT_DIR,
        )

    process_silver() >> reconcile_metadata() >> build_analytics()
