import psycopg

from hip.config.database import DatabaseSettings


def test_gold_pipeline_health_exposes_audit_batches():
    settings = DatabaseSettings.from_environment()

    with psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.username,
        password=settings.password,
    ) as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                batch_id,
                source_system,
                batch_name,
                environment,
                status,
                started_at,
                completed_at,
                duration_seconds,
                total_rows,
                successful_rows,
                failed_rows,
                duplicate_rows,
                initiated_by,
                platform_version
            FROM gold.pipeline_health
            ORDER BY started_at DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

    assert row is not None
    assert row[0] is not None
    assert row[1] is not None
    assert row[3] in {"DEV", "TEST", "UAT", "PROD"}
    assert row[4] in {
        "PENDING",
        "RUNNING",
        "SUCCESS",
        "FAILED",
        "CANCELLED",
    }
    assert row[5] is not None
    assert row[11] >= 0
    assert row[12] is not None
