from hip.metadata.dhis2 import DHIS2Metadata


def test_dhis2_metadata_allows_complete_metadata():
    metadata = DHIS2Metadata(
        data_element_name="TX_CURR",
        org_unit_name="Example Health Centre",
        category_option_combo_name="Male, 20-24",
        attribute_option_combo_name="Default",
    )

    assert metadata.data_element_name == "TX_CURR"
    assert metadata.org_unit_name == "Example Health Centre"
    assert metadata.category_option_combo_name == "Male, 20-24"
    assert metadata.attribute_option_combo_name == "Default"


def test_dhis2_metadata_allows_partial_metadata():
    metadata = DHIS2Metadata(
        data_element_name="TX_CURR",
    )

    assert metadata.data_element_name == "TX_CURR"
    assert metadata.org_unit_name is None
    assert metadata.category_option_combo_name is None
    assert metadata.attribute_option_combo_name is None
