from hip.transformers.dhis2 import DHIS2Transformer


def test_dhis2_transformer_creates_canonical_record():
    transformer = DHIS2Transformer(
        batch_id="batch-001",
        source_instance="kenya_demo",
    )

    raw_record = {
        "dataset_id": "DEMO_DATASET",
        "data_element": "DEMO_ELEMENT",
        "data_element_name": "Demo Element",
        "org_unit": "DEMO_ORG_UNIT",
        "org_unit_name": "Demo Organisation Unit",
        "period": "202608",
        "value": "100",
    }

    result = transformer.transform(raw_record)

    assert result.batch_id == "batch-001"
    assert result.source_instance == "kenya_demo"
    assert result.data_element == "DEMO_ELEMENT"
    assert result.org_unit == "DEMO_ORG_UNIT"
    assert result.period == "202608"
    assert result.value == "100"

    assert result.raw_payload == raw_record
    assert len(result.record_hash) == 64
