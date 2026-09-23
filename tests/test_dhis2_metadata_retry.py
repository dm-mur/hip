from unittest.mock import MagicMock, call

from hip.metadata.dhis2 import DHIS2Metadata
from hip.metadata.retry import DHIS2MetadataRetryService


def test_retry_service_resolves_unresolved_data_element():
    repository = MagicMock()
    api_service = MagicMock()
    silver_loader = MagicMock()

    repository.fetch_unresolved.return_value = [
        {
            "metadata_type": "DATA_ELEMENT",
            "uid": "DE_RETRY_001",
            "attempt_count": 1,
        }
    ]

    api_service.resolve.return_value = DHIS2Metadata(
        data_element_name="Recovered Data Element",
    )

    service = DHIS2MetadataRetryService(
        repository=repository,
        api_service=api_service,
        silver_loader=silver_loader,
    )

    result = service.retry(
        source_instance="test_instance",
    )

    assert result == {
        "attempted": 1,
        "resolved": 1,
        "unresolved": 0,
    }

    repository.upsert_many.assert_called_once_with(
        source_instance="test_instance",
        metadata_type="DATA_ELEMENT",
        metadata={
            "DE_RETRY_001": "Recovered Data Element",
        },
    )

    repository.mark_resolved.assert_called_once_with(
        source_instance="test_instance",
        metadata_type="DATA_ELEMENT",
        uid="DE_RETRY_001",
    )

    repository.record_unresolved.assert_not_called()

def test_retry_service_keeps_unresolved_data_element_open():
    repository = MagicMock()
    api_service = MagicMock()
    silver_loader = MagicMock()

    repository.fetch_unresolved.return_value = [
        {
            "metadata_type": "DATA_ELEMENT",
            "uid": "DE_STILL_UNKNOWN",
            "attempt_count": 1,
        }
    ]

    api_service.resolve.return_value = DHIS2Metadata()

    service = DHIS2MetadataRetryService(
        repository=repository,
        api_service=api_service,
        silver_loader=silver_loader,
    )

    result = service.retry(
        source_instance="test_instance",
    )

    assert result == {
        "attempted": 1,
        "resolved": 0,
        "unresolved": 1,
    }

    repository.record_unresolved.assert_called_once_with(
        source_instance="test_instance",
        metadata_type="DATA_ELEMENT",
        uid="DE_STILL_UNKNOWN",
    )

    repository.upsert_many.assert_not_called()
    repository.mark_resolved.assert_not_called()
    silver_loader.backfill_metadata_name.assert_not_called()

def test_retry_service_resolves_all_metadata_types():
    repository = MagicMock()
    api_service = MagicMock()
    silver_loader = MagicMock()

    repository.fetch_unresolved.return_value = [
        {
            "metadata_type": "DATA_ELEMENT",
            "uid": "DE_001",
            "attempt_count": 1,
        },
        {
            "metadata_type": "ORG_UNIT",
            "uid": "OU_001",
            "attempt_count": 1,
        },
        {
            "metadata_type": "CATEGORY_OPTION_COMBO",
            "uid": "COC_001",
            "attempt_count": 1,
        },
        {
            "metadata_type": "ATTRIBUTE_OPTION_COMBO",
            "uid": "AOC_001",
            "attempt_count": 1,
        },
    ]

    api_service.resolve.side_effect = [
        DHIS2Metadata(data_element_name="Data Element"),
        DHIS2Metadata(org_unit_name="Organisation Unit"),
        DHIS2Metadata(category_option_combo_name="Category Option Combo"),
        DHIS2Metadata(attribute_option_combo_name="Attribute Option Combo"),
    ]

    service = DHIS2MetadataRetryService(
        repository=repository,
        api_service=api_service,
        silver_loader=silver_loader,
    )

    result = service.retry(
        source_instance="test_instance",
    )

    assert result == {
        "attempted": 4,
        "resolved": 4,
        "unresolved": 0,
    }

    api_service.resolve.assert_has_calls(
        [
            call(
                data_element="DE_001",
                org_unit=None,
                category_option_combo=None,
                attribute_option_combo=None,
            ),
            call(
                data_element=None,
                org_unit="OU_001",
                category_option_combo=None,
                attribute_option_combo=None,
            ),
            call(
                data_element=None,
                org_unit=None,
                category_option_combo="COC_001",
                attribute_option_combo=None,
            ),
            call(
                data_element=None,
                org_unit=None,
                category_option_combo=None,
                attribute_option_combo="AOC_001",
            ),
        ]
    )

    api_service.preload.assert_called_once_with(
        data_elements={"DE_001"},
        org_units={"OU_001"},
        category_option_combos={"COC_001", "AOC_001"},
    )

    assert api_service.resolve.call_count == 4
    assert repository.upsert_many.call_count == 4
    assert repository.mark_resolved.call_count == 4
    assert silver_loader.backfill_metadata_name.call_count == 4
    repository.record_unresolved.assert_not_called()

def test_retry_service_handles_mixed_resolution_results():
    repository = MagicMock()
    api_service = MagicMock()
    silver_loader = MagicMock()

    repository.fetch_unresolved.return_value = [
        {
            "metadata_type": "CATEGORY_OPTION_COMBO",
            "uid": "COC_RECOVERED",
            "attempt_count": 1,
        },
        {
            "metadata_type": "CATEGORY_OPTION_COMBO",
            "uid": "COC_STILL_UNKNOWN",
            "attempt_count": 2,
        },
    ]

    api_service.resolve.side_effect = [
        DHIS2Metadata(
            category_option_combo_name="Recovered Category Option Combo",
        ),
        DHIS2Metadata(),
    ]

    service = DHIS2MetadataRetryService(
        repository=repository,
        api_service=api_service,
        silver_loader=silver_loader,
    )

    result = service.retry(
        source_instance="test_instance",
    )

    assert result == {
        "attempted": 2,
        "resolved": 1,
        "unresolved": 1,
    }

    repository.upsert_many.assert_called_once_with(
        source_instance="test_instance",
        metadata_type="CATEGORY_OPTION_COMBO",
        metadata={
            "COC_RECOVERED": "Recovered Category Option Combo",
        },
    )

    repository.mark_resolved.assert_called_once_with(
        source_instance="test_instance",
        metadata_type="CATEGORY_OPTION_COMBO",
        uid="COC_RECOVERED",
    )

    repository.record_unresolved.assert_called_once_with(
        source_instance="test_instance",
        metadata_type="CATEGORY_OPTION_COMBO",
        uid="COC_STILL_UNKNOWN",
    )

def test_retry_service_handles_empty_retry_queue():
    repository = MagicMock()
    api_service = MagicMock()
    silver_loader = MagicMock()

    repository.fetch_unresolved.return_value = []

    service = DHIS2MetadataRetryService(
        repository=repository,
        api_service=api_service,
        silver_loader=silver_loader,
    )

    result = service.retry(
        source_instance="test_instance",
    )

    assert result == {
        "attempted": 0,
        "resolved": 0,
        "unresolved": 0,
    }

    api_service.resolve.assert_not_called()
    api_service.preload.assert_not_called()
    repository.upsert_many.assert_not_called()
    repository.mark_resolved.assert_not_called()
    repository.record_unresolved.assert_not_called()
