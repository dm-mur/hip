from hip.mappings.dhis2 import DEFAULT_DHIS2_MAPPING


def test_default_dhis2_mapping_contains_core_fields():
    assert DEFAULT_DHIS2_MAPPING["dataset_id"] == "dataSet"
    assert DEFAULT_DHIS2_MAPPING["data_element"] == "dataElement"
    assert DEFAULT_DHIS2_MAPPING["org_unit"] == "orgUnit"
    assert DEFAULT_DHIS2_MAPPING["period"] == "period"
    assert (
        DEFAULT_DHIS2_MAPPING["category_option_combo"]
        == "categoryOptionCombo"
    )
    assert (
        DEFAULT_DHIS2_MAPPING["attribute_option_combo"]
        == "attributeOptionCombo"
    )
    assert DEFAULT_DHIS2_MAPPING["value"] == "value"
    assert DEFAULT_DHIS2_MAPPING["stored_by"] == "storedBy"
    assert DEFAULT_DHIS2_MAPPING["created_at_source"] == "created"
    assert DEFAULT_DHIS2_MAPPING["last_updated_at_source"] == "lastUpdated"
