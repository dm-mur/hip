from hip.metadata.in_memory import InMemoryDHIS2MetadataService


def test_resolve_returns_matching_metadata():
    service = InMemoryDHIS2MetadataService(
        data_elements={
            "DE123": "TX_CURR",
        },
        org_units={
            "OU456": "Example Health Centre",
        },
        category_option_combos={
            "COC789": "Male, 20-24",
        },
        attribute_option_combos={
            "AOC000": "Default",
        },
    )

    metadata = service.resolve(
        data_element="DE123",
        org_unit="OU456",
        category_option_combo="COC789",
        attribute_option_combo="AOC000",
    )

    assert metadata.data_element_name == "TX_CURR"
    assert metadata.org_unit_name == "Example Health Centre"
    assert metadata.category_option_combo_name == "Male, 20-24"
    assert metadata.attribute_option_combo_name == "Default"


def test_resolve_returns_none_for_unknown_metadata():
    service = InMemoryDHIS2MetadataService()

    metadata = service.resolve(
        data_element="UNKNOWN_DE",
        org_unit="UNKNOWN_OU",
        category_option_combo="UNKNOWN_COC",
        attribute_option_combo="UNKNOWN_AOC",
    )

    assert metadata.data_element_name is None
    assert metadata.org_unit_name is None
    assert metadata.category_option_combo_name is None
    assert metadata.attribute_option_combo_name is None


def test_resolve_handles_optional_combo_ids():
    service = InMemoryDHIS2MetadataService(
        data_elements={
            "DE123": "TX_CURR",
        },
        org_units={
            "OU456": "Example Health Centre",
        },
    )

    metadata = service.resolve(
        data_element="DE123",
        org_unit="OU456",
        category_option_combo=None,
        attribute_option_combo=None,
    )

    assert metadata.data_element_name == "TX_CURR"
    assert metadata.org_unit_name == "Example Health Centre"
    assert metadata.category_option_combo_name is None
    assert metadata.attribute_option_combo_name is None
