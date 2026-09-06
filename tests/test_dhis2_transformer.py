from hip.mappings.dhis2 import DEFAULT_DHIS2_MAPPING
from hip.metadata.in_memory import InMemoryDHIS2MetadataService
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
        "dataSet": "DEMO_DATASET",
        "dataElement": "DEMO_ELEMENT",
        "orgUnit": "DEMO_ORG_UNIT",
        "period": "202608",
        "categoryOptionCombo": "DEFAULT",
        "attributeOptionCombo": "DEFAULT",
        "value": "100",
        "comment": None,
        "followup": False,
        "storedBy": "pytest",
        "created": "2026-08-31T10:00:00.000",
        "lastUpdated": "2026-08-31T10:00:00.000",
    }

    result = transformer.transform(
        raw_record,
        context=context,
    )

    assert result.batch_id == "batch-001"
    assert result.source_instance == "kenya_demo"
    assert result.dataset_id == "DEMO_DATASET"
    assert result.data_element == "DEMO_ELEMENT"
    assert result.org_unit == "DEMO_ORG_UNIT"
    assert result.period == "202608"
    assert result.category_option_combo == "DEFAULT"
    assert result.attribute_option_combo == "DEFAULT"
    assert result.value == "100"
    assert result.comment is None
    assert result.followup is False
    assert result.stored_by == "pytest"
    assert result.created_at_source == "2026-08-31T10:00:00.000"
    assert result.last_updated_at_source == "2026-08-31T10:00:00.000"

    assert result.data_element_name is None
    assert result.org_unit_name is None
    assert result.category_option_combo_name is None
    assert result.attribute_option_combo_name is None

    assert result.raw_payload == raw_record
    assert len(result.record_hash) == 64

def test_dhis2_transformer_implements_base_transformer():
    transformer = DHIS2Transformer(
        source_instance="test_dhis2",
    )

    assert isinstance(transformer, BaseTransformer)


def test_transformer_enriches_record_with_metadata():
    metadata_service = InMemoryDHIS2MetadataService(
        data_elements={
            "DE123": "TX_CURR",
        },
        org_units={
            "OU456": "Example Health Centre",
        },
        category_option_combos={
            "COC789": "Male, 20-24",
        },
        attribute_option_combos={
            "AOC000": "Default",
        },
    )

    transformer = DHIS2Transformer(
        source_instance="test_instance",
        mapping=DEFAULT_DHIS2_MAPPING,
        metadata_service=metadata_service,
    )

    context = PipelineContext(
        batch_id="batch-001",
        environment="TEST",
        initiated_by="pytest",
    )

    record = {
        "dataSet": "DS001",
        "dataElement": "DE123",
        "orgUnit": "OU456",
        "period": "202608",
        "categoryOptionCombo": "COC789",
        "attributeOptionCombo": "AOC000",
        "value": "100",
    }

    result = transformer.transform(
        record,
        context,
    )

    assert result.data_element_name == "TX_CURR"
    assert result.org_unit_name == "Example Health Centre"
    assert result.category_option_combo_name == "Male, 20-24"
    assert result.attribute_option_combo_name == "Default"


def test_transformer_works_without_metadata_service():
    transformer = DHIS2Transformer(
        source_instance="test_instance",
        mapping=DEFAULT_DHIS2_MAPPING,
    )

    context = PipelineContext(
        batch_id="batch-001",
        environment="TEST",
        initiated_by="pytest",
    )

    record = {
        "dataSet": "DS001",
        "dataElement": "DE123",
        "dataElementName": "Existing Data Element Name",
        "orgUnit": "OU456",
        "orgUnitName": "Existing Facility Name",
        "period": "202608",
        "categoryOptionCombo": "COC789",
        "attributeOptionCombo": "AOC000",
        "value": "100",
    }

    result = transformer.transform(
        record,
        context,
    )

    assert result.data_element_name == "Existing Data Element Name"
    assert result.org_unit_name == "Existing Facility Name"