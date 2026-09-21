from decimal import Decimal
from uuid import UUID

import pytest

from hip.transformers.silver_dhis2 import SilverDHIS2Transformer


def test_silver_transformer_converts_numeric_value():
    transformer = SilverDHIS2Transformer()

    bronze_record = {
        "bronze_id": 101,
        "batch_id": UUID("11111111-1111-1111-1111-111111111111"),
        "source_system": "DHIS2",
        "source_instance": "live_test",
        "dataset_id": "DS001",
        "data_element": "DE001",
        "data_element_name": "TX_CURR",
        "org_unit": "OU001",
        "org_unit_name": "Example Health Centre",
        "period": "202605",
        "category_option_combo": "COC001",
        "category_option_combo_name": "Male, 20-24",
        "attribute_option_combo": "AOC001",
        "attribute_option_combo_name": "Default",
        "value": "15",
        "created_at_source": None,
        "last_updated_at_source": None,
    }

    observation = transformer.transform(bronze_record)

    assert observation.bronze_id == 101
    assert observation.value_raw == "15"
    assert observation.value_numeric == Decimal(15)
    assert observation.quality_status == "VALID"
    assert observation.quality_reason is None

def test_silver_transformer_converts_decimal_value():
    transformer = SilverDHIS2Transformer()

    bronze_record = {
        "bronze_id": 102,
        "batch_id": UUID("11111111-1111-1111-1111-111111111111"),
        "source_system": "DHIS2",
        "source_instance": "live_test",
        "dataset_id": "DS001",
        "data_element": "DE001",
        "data_element_name": "TX_CURR",
        "org_unit": "OU001",
        "org_unit_name": "Example Health Centre",
        "period": "202605",
        "category_option_combo": "COC001",
        "category_option_combo_name": "Male, 20-24",
        "attribute_option_combo": "AOC001",
        "attribute_option_combo_name": "Default",
        "value": "3.5",
        "created_at_source": None,
        "last_updated_at_source": None,
    }

    observation = transformer.transform(bronze_record)

    assert observation.value_raw == "3.5"
    assert observation.value_numeric == Decimal("3.5")
    assert observation.quality_status == "VALID"
    assert observation.quality_reason is None

def test_silver_transformer_marks_non_numeric_value():
    transformer = SilverDHIS2Transformer()

    bronze_record = {
        "bronze_id": 103,
        "batch_id": UUID("11111111-1111-1111-1111-111111111111"),
        "source_system": "DHIS2",
        "source_instance": "live_test",
        "dataset_id": "DS001",
        "data_element": "DE001",
        "data_element_name": "TX_CURR",
        "org_unit": "OU001",
        "org_unit_name": "Example Health Centre",
        "period": "202605",
        "category_option_combo": "COC001",
        "category_option_combo_name": "Male, 20-24",
        "attribute_option_combo": "AOC001",
        "attribute_option_combo_name": "Default",
        "value": "Some text",
        "created_at_source": None,
        "last_updated_at_source": None,
    }

    observation = transformer.transform(bronze_record)

    assert observation.value_raw == "Some text"
    assert observation.value_numeric is None
    assert observation.quality_status == "NON_NUMERIC"
    assert observation.quality_reason == (
        "Value could not be parsed as numeric"
    )

def test_silver_transformer_rejects_missing_required_identity():
    transformer = SilverDHIS2Transformer()

    bronze_record = {
        "bronze_id": 104,
        "batch_id": UUID("11111111-1111-1111-1111-111111111111"),
        "source_system": "DHIS2",
        "source_instance": "live_test",
        "dataset_id": "DS001",
        "data_element": "DE001",
        "data_element_name": "TX_CURR",
        "org_unit": "OU001",
        "org_unit_name": "Example Health Centre",
        "period": None,
        "category_option_combo": "COC001",
        "category_option_combo_name": "Male, 20-24",
        "attribute_option_combo": "AOC001",
        "attribute_option_combo_name": "Default",
        "value": "15",
        "created_at_source": None,
        "last_updated_at_source": None,
    }

    with pytest.raises(
        ValueError,
        match="period is required",
    ):
        transformer.transform(bronze_record)