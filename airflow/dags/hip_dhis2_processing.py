from __future__ import annotations

import subprocess
from datetime import UTC, datetime

from airflow.sdk import DAG, Param, task

SOURCE_INSTANCE = "live_test"
DATASET_ID = "wRQAtvYToKU"
ORG_UNIT_ID = "GOxptySBE5j"
DHIS2_ENDPOINT = "/api/dataValueSets"
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
    description="Ingest and process DHIS2 data through HIP analytics",
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    schedule=None,
    catchup=False,
    params={
        "period": Param(
            "202607",
            type="string",
            pattern=r"^\d{6}$",
            description="DHIS2 reporting period in YYYYMM format",
        ),
    },
    tags=["hip", "dhis2"],
) as dag:

    @task
    def ingest_dhis2(**context) -> None:
        period = context["params"]["period"]

        run_command(
            [
                "hip",
                "run",
                "dhis2",
                "--source-instance",
                SOURCE_INSTANCE,
                "--endpoint",
                DHIS2_ENDPOINT,
                "--environment",
                "DEV",
                "--initiated-by",
                "airflow",
                "--batch-name",
                f"DHIS2 Airflow {period}",
                "--period",
                period,
                "--param",
                f"dataSet={DATASET_ID}",
                "--param",
                f"orgUnit={ORG_UNIT_ID}",
            ]
        )

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

    ingest_dhis2() >> process_silver() >> reconcile_metadata() >> build_analytics()
