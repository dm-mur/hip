"""Tests for DHIS2 dataset metadata synchronization."""

from unittest.mock import MagicMock

from hip.metadata.dataset_sync import DHIS2DatasetMetadataSync


def test_dataset_metadata_sync_fetches_and_persists_metadata():
    """Sync should fetch authoritative dataset metadata and cache it."""

    api_service = MagicMock()
    repository = MagicMock()

    api_service.fetch.return_value = {
        "dataset_id": "wRQAtvYToKU",
        "dataset_name": "Care & Tx Reporting Tool",
        "period_type": "Monthly",
    }

    service = DHIS2DatasetMetadataSync(
        api_service=api_service,
        repository=repository,
    )

    result = service.sync(
        source_instance="live_test",
        dataset_id="wRQAtvYToKU",
    )

    api_service.fetch.assert_called_once_with("wRQAtvYToKU")

    repository.upsert.assert_called_once_with(
        source_instance="live_test",
        dataset_id="wRQAtvYToKU",
        dataset_name="Care & Tx Reporting Tool",
        period_type="Monthly",
    )

    assert result == {
        "dataset_id": "wRQAtvYToKU",
        "dataset_name": "Care & Tx Reporting Tool",
        "period_type": "Monthly",
    }


def test_dataset_metadata_sync_uses_returned_dataset_id():
    """Persist the dataset identity returned by DHIS2."""

    api_service = MagicMock()
    repository = MagicMock()

    api_service.fetch.return_value = {
        "dataset_id": "DATASET_002",
        "dataset_name": "Quarterly Dataset",
        "period_type": "Quarterly",
    }

    service = DHIS2DatasetMetadataSync(
        api_service=api_service,
        repository=repository,
    )

    service.sync(
        source_instance="source_a",
        dataset_id="DATASET_002",
    )

    repository.upsert.assert_called_once_with(
        source_instance="source_a",
        dataset_id="DATASET_002",
        dataset_name="Quarterly Dataset",
        period_type="Quarterly",
    )
