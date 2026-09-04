"""
DHIS2 source-to-canonical field mappings.

Mappings allow different DHIS2 implementations to use their
own field naming conventions while HIP maintains one canonical
internal representation.
"""

DEFAULT_DHIS2_MAPPING = {
    "dataset_id": "dataSet",
    "data_element": "dataElement",
    "data_element_name": "dataElementName",
    "org_unit": "orgUnit",
    "org_unit_name": "orgUnitName",
    "period": "period",
    "category_option_combo": "categoryOptionCombo",
    "category_option_combo_name": "categoryOptionComboName",
    "attribute_option_combo": "attributeOptionCombo",
    "attribute_option_combo_name": "attributeOptionComboName",
    "value": "value",
    "comment": "comment",
    "followup": "followup",
    "stored_by": "storedBy",
    "created_at_source": "created",
    "last_updated_at_source": "lastUpdated",
}
