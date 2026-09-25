from datetime import datetime

from airflow.sdk import DAG, task


with DAG(
    dag_id="hip_smoke_test",
    description="Verify HIP Airflow orchestration is working",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["hip", "test"],
) as dag:

    @task
    def verify_airflow() -> str:
        message = "HIP Airflow orchestration is working"
        print(message)
        return message

    verify_airflow()
