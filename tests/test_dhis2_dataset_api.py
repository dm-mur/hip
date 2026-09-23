"""Tests for DHIS2 dataset metadata API retrieval."""

from unittest.mock import MagicMock, patch

from hip.config.settings import DHIS2Settings
from hip.metadata.dataset_api import DHIS2DatasetMetadataService


def make_settings() -> DHIS2Settings:
    """Return DHIS2 settings for testing."""

    return DHIS2Settings(
        base_url="https://example.org",
        username="test-user",
        password="test-password",
    )


@patch("hip.metadata.dataset_api.requests.get")
def test_dataset_metadata_service_fetches_dataset(mock_get):
    """Service should retrieve dataset name and period type from DHIS2."""

    response = MagicMock()
    response.json.return_value = {
        "id": "wRQAtvYToKU",
        "name": "Care & Tx Reporting Tool",
        "periodType": "Monthly",
    }
    mock_get.return_value = response

    service = DHIS2DatasetMetadataService(
        source_instance="live_test",
        settings=make_settings(),
    )

    metadata = service.fetch("wRQAtvYToKU")

    assert metadata == {
        "dataset_id": "wRQAtvYToKU",
        "dataset_name": "Care & Tx Reporting Tool",
        "period_type": "Monthly",
    }

    mock_get.assert_called_once_with(
        "https://example.org/api/dataSets/wRQAtvYToKU",
        params={
            "fields": "id,name,periodType",
        },
        auth=(
            "test-user",
            "test-password",
        ),
        timeout=60,
    )

    response.raise_for_status.assert_called_once_with()


def test_dataset_metadata_service_requires_source_instance():
    """Dataset metadata resolution must be bound to one DHIS2 instance."""

    try:
        DHIS2DatasetMetadataService(
            source_instance="",
            settings=make_settings(),
        )
    except ValueError as exc:
        assert str(exc) == "source_instance is required"
    else:
        raise AssertionError("Expected ValueError")
