from hip.models.dhis2 import DHIS2Record


def test_dhis2_record_can_be_created():
    record = DHIS2Record(
        batch_id="batch-001",
        source_instance="kenya_demo",
        dataset_id="DEMO_DATASET",
        data_element="DEMO_ELEMENT",
        data_element_name="Demo Element",
        org_unit="DEMO_ORG_UNIT",
        org_unit_name="Demo Organisation Unit",
        period="202608",
        category_option_combo=None,
        category_option_combo_name=None,
        attribute_option_combo=None,
        attribute_option_combo_name=None,
        value="100",
        comment=None,
        followup=None,
        stored_by=None,
        created_at_source=None,
        last_updated_at_source=None,
        raw_payload={
            "dataElement": "DEMO_ELEMENT",
            "orgUnit": "DEMO_ORG_UNIT",
            "period": "202608",
            "value": "100",
        },
        record_hash="abc123",
    )

    assert record.source_instance == "kenya_demo"
    assert record.data_element == "DEMO_ELEMENT"
    assert record.value == "100"
    assert record.raw_payload["dataElement"] == "DEMO_ELEMENT"
