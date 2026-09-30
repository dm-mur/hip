from __future__ import annotations

import subprocess
from datetime import UTC, datetime, timedelta

from airflow.sdk import DAG, Param, task

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
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    params={
        "source_instance": Param(
            "live_test",
            type="string",
            minLength=1,
            description="Logical name identifying the DHIS2 source instance",
        ),
        "dataset_id": Param(
            "wRQAtvYToKU",
            type="string",
            minLength=1,
            description="DHIS2 dataset UID",
        ),
        "org_unit_id": Param(
            "GOxptySBE5j",
            type="string",
            minLength=1,
            description="DHIS2 organisation unit UID",
        ),
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
        params = context["params"]

        source_instance = params["source_instance"]
        dataset_id = params["dataset_id"]
        org_unit_id = params["org_unit_id"]
        period = params["period"]

        run_command(
            [
                "hip",
                "run",
                "dhis2",
                "--source-instance",
                source_instance,
                "--endpoint",
                DHIS2_ENDPOINT,
                "--environment",
                "DEV",
                "--initiated-by",
                "airflow",
                "--batch-name",
                f"DHIS2 Airflow {source_instance} {period}",
                "--period",
                period,
                "--param",
                f"dataSet={dataset_id}",
                "--param",
                f"orgUnit={org_unit_id}",
            ]
        )

    @task
    def process_silver(**context) -> None:
        source_instance = context["params"]["source_instance"]

        run_command(
            [
                "hip",
                "process",
                "silver",
                "dhis2",
                "--source-instance",
                source_instance,
            ]
        )

    @task
    def reconcile_metadata(**context) -> None:
        source_instance = context["params"]["source_instance"]

        run_command(
            [
                "hip",
                "process",
                "metadata",
                "dhis2",
                "--source-instance",
                source_instance,
            ]
        )

    @task
    def build_analytics() -> None:
        run_command(
            ["dbt", "build"],
            cwd=DBT_PROJECT_DIR,
        )

    ingest_dhis2() >> process_silver() >> reconcile_metadata() >> build_analytics()
