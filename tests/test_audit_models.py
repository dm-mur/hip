from hip.audit.models import BatchSummary


def test_batch_summary_derives_inserted_rows():
    summary = BatchSummary(
        batch_id="batch-001",
        source_system="DHIS2",
        batch_name="Monthly Import",
        environment="PROD",
        status="SUCCESS",
        total_rows=2579,
        successful_rows=2579,
        failed_rows=0,
        duplicate_rows=149,
    )

    assert summary.inserted_rows == 2430
