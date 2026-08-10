from hip.mappings.dhis2 import DEFAULT_DHIS2_MAPPING


def test_default_dhis2_mapping_contains_core_fields():
    assert DEFAULT_DHIS2_MAPPING["data_element"] == "data_element"
    assert DEFAULT_DHIS2_MAPPING["org_unit"] == "org_unit"
    assert DEFAULT_DHIS2_MAPPING["period"] == "period"
    assert DEFAULT_DHIS2_MAPPING["value"] == "value"
