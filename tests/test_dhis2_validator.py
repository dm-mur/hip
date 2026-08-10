from hip.models.dhis2 import DHIS2Record
from hip.validators.dhis2 import DHIS2Validator


def make_record(**overrides):
    data = {
        "batch_id": "batch-001",
        "source_instance": "kenya_demo",
        "dataset_id": "DEMO_DATASET",
        "data_element": "DEMO_ELEMENT",
        "data_element_name": "Demo Element",
        "org_unit": "DEMO_ORG_UNIT",
        "org_unit_name": "Demo Organisation Unit",
        "period": "202608",
        "category_option_combo": None,
        "category_option_combo_name": None,
        "attribute_option_combo": None,
        "attribute_option_combo_name": None,
        "value": "100",
        "comment": None,
        "followup": None,
        "stored_by": None,
        "created_at_source": None,
        "last_updated_at_source": None,
        "raw_payload": {
            "dataElement": "DEMO_ELEMENT",
            "orgUnit": "DEMO_ORG_UNIT",
            "period": "202608",
            "value": "100",
        },
        "record_hash": "abc123",
    }

    data.update(overrides)

    return DHIS2Record(**data)


def test_valid_dhis2_record_passes_validation():
    validator = DHIS2Validator()

    result = validator.validate(make_record())

    assert result is True


def test_invalid_dhis2_record_fails_validation():
    validator = DHIS2Validator()

    record = make_record(org_unit=None)

    result = validator.validate_with_result(record)

    assert result.is_valid is False
    assert "org_unit is required" in result.errors
