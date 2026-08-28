from unittest.mock import Mock, patch

from hip.audit.service import AuditService
from hip.config.database import DatabaseSettings


def make_settings():
    return DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test_password",
    )


def make_connection():
    connection = Mock()
    cursor = Mock()

    connection.__enter__ = Mock(return_value=connection)
    connection.__exit__ = Mock(return_value=None)

    connection.cursor.return_value.__enter__ = Mock(
        return_value=cursor
    )
    connection.cursor.return_value.__exit__ = Mock(
        return_value=None
    )

    return connection, cursor


def test_audit_service_starts_batch():
    connection, cursor = make_connection()

    service = AuditService(make_settings())

    with patch.object(
        service,
        "_connection",
        return_value=connection,
    ):
        batch_id = service.start_batch(
            source_system="DHIS2",
            batch_name="Kenya Demo Import",
            environment="DEV",
            initiated_by="test_user",
        )

    assert batch_id is not None
    cursor.execute.assert_called_once()

    query = cursor.execute.call_args.args[0]

    assert "INSERT INTO audit.etl_batch" in query
    assert "RUNNING" in query


def test_audit_service_completes_batch():
    connection, cursor = make_connection()

    service = AuditService(make_settings())

    with patch.object(
        service,
        "_connection",
        return_value=connection,
    ):
        service.complete_batch(
            batch_id="batch-001",
            total_rows=10,
            successful_rows=8,
            failed_rows=2,
        )

    cursor.execute.assert_called_once()

    query = cursor.execute.call_args.args[0]

    assert "SUCCESS" in query
    assert "successful_rows" in query
    assert "failed_rows" in query
    assert "duration_seconds" in query


def test_audit_service_fails_batch():
    connection, cursor = make_connection()

    service = AuditService(make_settings())

    with patch.object(
        service,
        "_connection",
        return_value=connection,
    ):
        service.fail_batch(
            batch_id="batch-001",
            total_rows=10,
            successful_rows=7,
            failed_rows=3,
            remarks="Three records failed validation",
        )

    cursor.execute.assert_called_once()

    query = cursor.execute.call_args.args[0]

    assert "FAILED" in query
    assert "successful_rows" in query
    assert "failed_rows" in query
    assert "remarks" in query
    assert "duration_seconds" in query