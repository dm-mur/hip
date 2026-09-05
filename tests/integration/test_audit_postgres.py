import psycopg

from hip.audit.service import AuditService
from hip.config.database import DatabaseSettings


def test_audit_service_writes_real_postgres_batch():
    settings = DatabaseSettings.from_environment()
    service = AuditService(settings)

    batch_id = service.start_batch(
        source_system="DHIS2",
        batch_name="Integration Test",
        environment="TEST",
        initiated_by="pytest",
    )

    assert batch_id is not None

    # Verify the batch starts as RUNNING.
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
                    status,
                    source_system,
                    batch_name,
                    environment,
                    initiated_by
                FROM audit.etl_batch
                WHERE batch_id = %s
                """,
            (batch_id,),
        )

        row = cursor.fetchone()

    assert row is not None

    status, source_system, batch_name, environment, initiated_by = row

    assert status == "RUNNING"
    assert source_system == "DHIS2"
    assert batch_name == "Integration Test"
    assert environment == "TEST"
    assert initiated_by == "pytest"

    # Complete the batch.
    service.complete_batch(
        batch_id=batch_id,
        total_rows=10,
        successful_rows=8,
        failed_rows=2,
        duplicate_rows=0,
    )

    # Verify the final database state.
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
                    status,
                    total_rows,
                    successful_rows,
                    failed_rows,
                    duplicate_rows,
                    completed_at,
                    duration_seconds
                FROM audit.etl_batch
                WHERE batch_id = %s
                """,
            (batch_id,),
        )

        row = cursor.fetchone()

    assert row is not None

    (
        status,
        total_rows,
        successful_rows,
        failed_rows,
        duplicate_rows,
        completed_at,
        duration_seconds,
    ) = row

    assert status == "SUCCESS"
    assert total_rows == 10
    assert successful_rows == 8
    assert failed_rows == 2
    assert duplicate_rows == 0
    assert completed_at is not None
    assert duration_seconds is not None
    assert duration_seconds >= 0
    
def test_audit_service_marks_real_postgres_batch_failed():
    settings = DatabaseSettings.from_environment()
    service = AuditService(settings)

    batch_id = service.start_batch(
        source_system="DHIS2",
        batch_name="Integration Failure Test",
        environment="TEST",
        initiated_by="pytest",
    )

    service.fail_batch(
        batch_id=batch_id,
        total_rows=10,
        successful_rows=7,
        failed_rows=3,
        duplicate_rows=0,
        remarks="Three records failed validation",
    )

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
                    status,
                    total_rows,
                    successful_rows,
                    failed_rows,
                    duplicate_rows,
                    remarks,
                    completed_at,
                    duration_seconds
                FROM audit.etl_batch
                WHERE batch_id = %s
                """,
            (batch_id,),
        )

        row = cursor.fetchone()

    assert row is not None

    (
        status,
        total_rows,
        successful_rows,
        failed_rows,
        duplicate_rows,
        remarks,
        completed_at,
        duration_seconds,
    ) = row

    assert status == "FAILED"
    assert total_rows == 10
    assert successful_rows == 7
    assert failed_rows == 3
    assert duplicate_rows == 0
    assert remarks == "Three records failed validation"
    assert completed_at is not None
    assert duration_seconds is not None
    assert duration_seconds >= 0