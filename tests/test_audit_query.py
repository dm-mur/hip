from unittest.mock import Mock, patch

from hip.audit.query import AuditQueryService
from hip.config.database import DatabaseSettings


def make_settings():
    return DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test_password",
    )


def make_connection(row):
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

    cursor.fetchone.return_value = row

    return connection, cursor


def test_get_batch_summary_returns_summary():
    row = (
        "batch-001",
        "DHIS2",
        "Monthly Import",
        "PROD",
        "SUCCESS",
        2579,
        2579,
        0,
        149,
    )

    connection, cursor = make_connection(row)
    service = AuditQueryService(make_settings())

    with patch.object(
        service,
        "_connection",
        return_value=connection,
    ):
        summary = service.get_batch_summary("batch-001")

    assert summary is not None
    assert summary.batch_id == "batch-001"
    assert summary.source_system == "DHIS2"
    assert summary.batch_name == "Monthly Import"
    assert summary.environment == "PROD"
    assert summary.status == "SUCCESS"
    assert summary.total_rows == 2579
    assert summary.successful_rows == 2579
    assert summary.failed_rows == 0
    assert summary.duplicate_rows == 149
    assert summary.inserted_rows == 2430

    cursor.execute.assert_called_once()


def test_get_batch_summary_returns_none_when_batch_not_found():
    connection, _ = make_connection(None)
    service = AuditQueryService(make_settings())

    with patch.object(
        service,
        "_connection",
        return_value=connection,
    ):
        summary = service.get_batch_summary("missing-batch")

    assert summary is None
