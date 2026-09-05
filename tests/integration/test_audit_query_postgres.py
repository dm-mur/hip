from hip.audit.query import AuditQueryService
from hip.audit.service import AuditService
from hip.config.database import DatabaseSettings


def test_audit_query_returns_real_batch_summary():
    settings = DatabaseSettings.from_environment()

    audit_service = AuditService(settings)
    query_service = AuditQueryService(settings)

    batch_id = audit_service.start_batch(
        source_system="DHIS2",
        batch_name="Audit Query Integration Test",
        environment="TEST",
        initiated_by="pytest",
    )

    audit_service.complete_batch(
        batch_id=batch_id,
        total_rows=10,
        successful_rows=9,
        failed_rows=1,
        duplicate_rows=2,
    )

    summary = query_service.get_batch_summary(batch_id)

    assert summary is not None
    assert summary.batch_id == batch_id
    assert summary.source_system == "DHIS2"
    assert summary.batch_name == "Audit Query Integration Test"
    assert summary.environment == "TEST"
    assert summary.status == "SUCCESS"
    assert summary.total_rows == 10
    assert summary.successful_rows == 9
    assert summary.failed_rows == 1
    assert summary.duplicate_rows == 2
    assert summary.inserted_rows == 7
