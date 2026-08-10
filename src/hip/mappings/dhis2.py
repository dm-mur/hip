"""
DHIS2 source-to-canonical field mappings.

Mappings allow different DHIS2 implementations to use their
own field naming conventions while HIP maintains one canonical
internal representation.
"""

DEFAULT_DHIS2_MAPPING = {
    "dataset_id": "dataset_id",
    "data_element": "data_element",
    "data_element_name": "data_element_name",
    "org_unit": "org_unit",
    "org_unit_name": "org_unit_name",
    "period": "period",
    "category_option_combo": "category_option_combo",
    "category_option_combo_name": "category_option_combo_name",
    "attribute_option_combo": "attribute_option_combo",
    "attribute_option_combo_name": "attribute_option_combo_name",
    "value": "value",
    "comment": "comment",
    "followup": "followup",
    "stored_by": "stored_by",
    "created_at_source": "created_at_source",
    "last_updated_at_source": "last_updated_at_source",
}
