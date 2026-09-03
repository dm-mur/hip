from hip.pipelines.context import PipelineContext
from hip.transformers.base import BaseTransformer
from hip.transformers.dhis2 import DHIS2Transformer


def test_dhis2_transformer_creates_canonical_record():
    transformer = DHIS2Transformer(
        source_instance="kenya_demo",
    )

    context = PipelineContext(
        batch_id="batch-001",
        environment="TEST",
        initiated_by="pytest",
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

    result = transformer.transform(
        raw_record,
        context=context,
    )

    assert result.batch_id == "batch-001"
    assert result.source_instance == "kenya_demo"
    assert result.data_element == "DEMO_ELEMENT"
    assert result.org_unit == "DEMO_ORG_UNIT"
    assert result.period == "202608"
    assert result.value == "100"

    assert result.raw_payload == raw_record
    assert len(result.record_hash) == 64
    
def test_dhis2_transformer_implements_base_transformer():
    transformer = DHIS2Transformer(
        source_instance="test_dhis2",
    )

    assert isinstance(transformer, BaseTransformer)