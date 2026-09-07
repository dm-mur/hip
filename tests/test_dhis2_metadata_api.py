from unittest.mock import Mock, patch

from hip.config.settings import DHIS2Settings
from hip.metadata.api import DHIS2APIMetadataService


def make_settings(
    base_url: str,
) -> DHIS2Settings:
    return DHIS2Settings(
        base_url=base_url,
        username="test_user",
        password="test_password",
    )


def test_api_metadata_service_is_scoped_to_source_instance():
    first = DHIS2APIMetadataService(
        source_instance="instance_a",
        settings=make_settings("https://instance-a.example.org"),
    )

    second = DHIS2APIMetadataService(
        source_instance="instance_b",
        settings=make_settings("https://instance-b.example.org"),
    )

    first.data_elements["DE123"] = "TX_CURR"

    second.data_elements["DE123"] = "ANC First Visit"

    first_metadata = first.resolve(
        data_element="DE123",
        org_unit="OU001",
        category_option_combo=None,
        attribute_option_combo=None,
    )

    second_metadata = second.resolve(
        data_element="DE123",
        org_unit="OU001",
        category_option_combo=None,
        attribute_option_combo=None,
    )

    assert first.source_instance == "instance_a"
    assert second.source_instance == "instance_b"

    assert first_metadata.data_element_name == "TX_CURR"
    assert second_metadata.data_element_name == "ANC First Visit"


def test_api_metadata_service_rejects_empty_source_instance():
    settings = make_settings(
        "https://example.org",
    )

    try:
        DHIS2APIMetadataService(
            source_instance="   ",
            settings=settings,
        )
    except ValueError as exc:
        assert str(exc) == "source_instance is required"
    else:
        raise AssertionError("Expected ValueError")


def test_api_metadata_service_preloads_requested_metadata():
    service = DHIS2APIMetadataService(
        source_instance="instance_a",
        settings=make_settings("https://instance-a.example.org"),
    )

    data_elements_response = Mock()
    data_elements_response.json.return_value = {
        "dataElements": [
            {
                "id": "DE123",
                "name": "TX_CURR",
            },
            {
                "id": "DE456",
                "name": "TX_NEW",
            },
        ]
    }

    org_units_response = Mock()
    org_units_response.json.return_value = {
        "organisationUnits": [
            {
                "id": "OU123",
                "name": "Example Health Centre",
            }
        ]
    }

    category_option_combos_response = Mock()
    category_option_combos_response.json.return_value = {
        "categoryOptionCombos": [
            {
                "id": "COC123",
                "name": "Male, 20-24",
            },
            {
                "id": "AOC123",
                "name": "Default",
            },
        ]
    }

    with patch(
        "hip.metadata.api.requests.get",
        side_effect=[
            data_elements_response,
            org_units_response,
            category_option_combos_response,
        ],
    ) as get:
        service.preload(
            data_elements={
                "DE123",
                "DE456",
            },
            org_units={
                "OU123",
            },
            category_option_combos={
                "COC123",
                "AOC123",
            },
        )

    assert service.data_elements == {
        "DE123": "TX_CURR",
        "DE456": "TX_NEW",
    }

    assert service.org_units == {
        "OU123": "Example Health Centre",
    }

    assert service.category_option_combos == {
        "COC123": "Male, 20-24",
        "AOC123": "Default",
    }

    assert get.call_count == 3

    data_elements_response.raise_for_status.assert_called_once()
    org_units_response.raise_for_status.assert_called_once()
    category_option_combos_response.raise_for_status.assert_called_once()


def test_api_metadata_service_resolves_loaded_metadata():
    service = DHIS2APIMetadataService(
        source_instance="instance_a",
        settings=make_settings("https://instance-a.example.org"),
    )

    service.data_elements = {
        "DE123": "TX_CURR",
    }

    service.org_units = {
        "OU123": "Example Health Centre",
    }

    service.category_option_combos = {
        "COC123": "Male, 20-24",
        "AOC123": "Default",
    }

    metadata = service.resolve(
        data_element="DE123",
        org_unit="OU123",
        category_option_combo="COC123",
        attribute_option_combo="AOC123",
    )

    assert metadata.data_element_name == "TX_CURR"
    assert metadata.org_unit_name == "Example Health Centre"
    assert metadata.category_option_combo_name == "Male, 20-24"
    assert metadata.attribute_option_combo_name == "Default"

def test_api_metadata_service_skips_http_for_empty_preload():
    service = DHIS2APIMetadataService(
        source_instance="instance_a",
        settings=make_settings("https://instance-a.example.org"),
    )

    with patch(
        "hip.metadata.api.requests.get",
    ) as get:
        service.preload(
            data_elements=set(),
            org_units=set(),
            category_option_combos=set(),
        )

    get.assert_not_called()

def test_api_metadata_service_filters_by_requested_ids():
    service = DHIS2APIMetadataService(
        source_instance="instance_a",
        settings=make_settings("https://instance-a.example.org"),
    )

    response = Mock()
    response.json.return_value = {
        "dataElements": [],
    }

    with patch(
        "hip.metadata.api.requests.get",
        return_value=response,
    ) as get:
        service.preload(
            data_elements={
                "DE456",
                "DE123",
            },
            org_units=set(),
            category_option_combos=set(),
        )

    get.assert_called_once_with(
        "https://instance-a.example.org/api/dataElements",
        params={
            "fields": "id,name",
            "filter": "id:in:[DE123,DE456]",
            "paging": "false",
        },
        auth=(
            "test_user",
            "test_password",
        ),
        timeout=60,
    )
