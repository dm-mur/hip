FROM apache/airflow:3.1.7

USER airflow

COPY --chown=airflow:0 pyproject.toml README.md /opt/hip/
COPY --chown=airflow:0 src /opt/hip/src

RUN pip install --no-cache-dir \
    /opt/hip \
    "dbt-core==1.12.5" \
    "dbt-postgres==1.11.0"

WORKDIR /opt/airflow
