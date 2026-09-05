from unittest.mock import Mock

from hip.audit.service import AuditService
from hip.loaders.result import LoadResult
from hip.pipelines.config import PipelineConfig
from hip.pipelines.dhis2 import DHIS2Pipeline
from hip.pipelines.request import PipelineRequest


def test_dhis2_pipeline_orchestrates_extract_transform_validate_load():
    extractor = Mock()
    transformer = Mock()
    validator = Mock()
    loader = Mock()

    extractor.extract.return_value = {
        "dataSet": "TEST_DATASET",
        "dataValues": [
            {"id": "record-001"},
            {"id": "record-002"},
        ],
    }

    transformed_1 = Mock()
    transformed_2 = Mock()

    transformer.transform.side_effect = [
        transformed_1,
        transformed_2,
    ]

    validator.validate.return_value = True
    loader.load.return_value = LoadResult(
        inserted_rows=2,
        duplicate_rows=0,
    )

    audit = Mock(spec=AuditService)
    audit.start_batch.return_value = "batch-001"

    pipeline = DHIS2Pipeline(
        extractor=extractor,
        transformer=transformer,
        validator=validator,
        loader=loader,
        audit=audit,
        config=PipelineConfig(
            environment="DEV",
            initiated_by="system",
            batch_name="DHIS2 Pipeline",
        ),
    )

    result = pipeline.run(
        request=PipelineRequest(
            endpoint="/api/dataValueSets",
            params={"period": "202608"},
        )
    )

    audit.start_batch.assert_called_once_with(
        source_system="DHIS2",
        batch_name="DHIS2 Pipeline",
        environment="DEV",
        initiated_by="system",
    )

    assert result == 2

    extractor.extract.assert_called_once_with(
        PipelineRequest(
            endpoint="/api/dataValueSets",
            params={"period": "202608"},
        )
    )

    assert transformer.transform.call_count == 2
    first_record = transformer.transform.call_args_list[0].args[0]
    second_record = transformer.transform.call_args_list[1].args[0]

    assert first_record == {
        "id": "record-001",
        "dataSet": "TEST_DATASET",
    }
    assert second_record == {
        "id": "record-002",
        "dataSet": "TEST_DATASET",
    }
    assert validator.validate.call_count == 2

    loader.load.assert_called_once_with(
        [transformed_1, transformed_2]
    )

    audit.complete_batch.assert_called_once_with(
        batch_id="batch-001",
        total_rows=2,
        successful_rows=2,
        failed_rows=0,
        duplicate_rows=0,
   )

def test_dhis2_pipeline_does_not_load_invalid_records():
    extractor = Mock()
    transformer = Mock()
    validator = Mock()
    loader = Mock()

    extractor.extract.return_value = {
        "dataSet": "TEST_DATASET",
        "dataValues": [
            {"id": "record-001"},
            {"id": "record-002"},
        ],
    }

    transformed_1 = Mock()
    transformed_2 = Mock()

    transformer.transform.side_effect = [
        transformed_1,
        transformed_2,
    ]

    validator.validate.side_effect = [
        True,
        False,
    ]

    loader.load.return_value = LoadResult(
        inserted_rows=1,
        duplicate_rows=0,
    )

    audit = Mock(spec=AuditService)
    audit.start_batch.return_value = "batch-001"

    pipeline = DHIS2Pipeline(
        extractor=extractor,
        transformer=transformer,
        validator=validator,
        loader=loader,
        audit=audit,
        config=PipelineConfig(
            environment="DEV",
            initiated_by="system",
            batch_name="DHIS2 Pipeline",
        ),
    )

    result = pipeline.run(
        request=PipelineRequest(
            endpoint="/api/dataValueSets",
            params={"period": "202608"},
        )
    )

    assert result == 1

    loader.load.assert_called_once_with(
        [transformed_1]
    )
    
    audit.complete_batch.assert_called_once_with(
        batch_id=audit.start_batch.return_value,
        total_rows=2,
        successful_rows=1,
        failed_rows=1,
        duplicate_rows=0,
    )
    
def test_dhis2_pipeline_marks_batch_failed_when_extraction_fails():
    extractor = Mock()
    transformer = Mock()
    validator = Mock()
    loader = Mock()
    audit = Mock(spec=AuditService)

    audit.start_batch.return_value = "batch-001"

    extractor.extract.side_effect = RuntimeError(
        "DHIS2 API unavailable"
    )

    pipeline = DHIS2Pipeline(
        extractor=extractor,
        transformer=transformer,
        validator=validator,
        loader=loader,
        audit=audit,
        config=PipelineConfig(
            environment="DEV",
            initiated_by="system",
            batch_name="DHIS2 Pipeline",
        ),
    )

    try:
        pipeline.run(
            request=PipelineRequest(
                endpoint="/api/dataValueSets",
                params={"period": "202608"},
            )
        )
    except RuntimeError:
        pass

    audit.start_batch.assert_called_once_with(
        source_system="DHIS2",
        batch_name="DHIS2 Pipeline",
        environment="DEV",
        initiated_by="system",
    )

    audit.fail_batch.assert_called_once_with(
        batch_id="batch-001",
        total_rows=0,
        successful_rows=0,
        failed_rows=0,
        duplicate_rows=0,
        remarks="DHIS2 API unavailable",
    )

    transformer.transform.assert_not_called()
    validator.validate.assert_not_called()
    loader.load.assert_not_called()
    
def test_dhis2_pipeline_marks_batch_failed_when_transformation_fails():
    extractor = Mock()
    transformer = Mock()
    validator = Mock()
    loader = Mock()
    audit = Mock(spec=AuditService)

    audit.start_batch.return_value = "batch-001"

    extractor.extract.return_value = {
        "dataSet": "TEST_DATASET",
        "dataValues": [
            {"id": "record-001"},
        ],
    }

    transformer.transform.side_effect = RuntimeError(
        "Invalid DHIS2 record structure"
    )

    pipeline = DHIS2Pipeline(
        extractor=extractor,
        transformer=transformer,
        validator=validator,
        loader=loader,
        audit=audit,
        config=PipelineConfig(
            environment="DEV",
            initiated_by="system",
            batch_name="DHIS2 Pipeline",
        ),
    )

    try:
        pipeline.run(
            request=PipelineRequest(
                endpoint="/api/dataValueSets",
                params={"period": "202608"},
            )
        )
    except RuntimeError:
        pass

    audit.fail_batch.assert_called_once_with(
        batch_id="batch-001",
        total_rows=1,
        successful_rows=0,
        failed_rows=1,
        duplicate_rows=0,
        remarks="Invalid DHIS2 record structure",
    )

    validator.validate.assert_not_called()
    loader.load.assert_not_called()
    
def test_dhis2_pipeline_marks_batch_failed_when_loading_fails():
    extractor = Mock()
    transformer = Mock()
    validator = Mock()
    loader = Mock()
    audit = Mock(spec=AuditService)

    audit.start_batch.return_value = "batch-001"

    extractor.extract.return_value = {
        "dataSet": "TEST_DATASET",
        "dataValues": [
            {"id": "record-001"},
        ],
    }

    transformed_record = Mock()

    transformer.transform.return_value = transformed_record
    validator.validate.return_value = True

    loader.load.side_effect = RuntimeError(
        "PostgreSQL connection failed"
    )

    pipeline = DHIS2Pipeline(
        extractor=extractor,
        transformer=transformer,
        validator=validator,
        loader=loader,
        audit=audit,
        config=PipelineConfig(
            environment="DEV",
            initiated_by="system",
            batch_name="DHIS2 Pipeline",
        ),
    )

    try:
        pipeline.run(
            request=PipelineRequest(
                endpoint="/api/dataValueSets",
                params={"period": "202608"},
            )
        )
    except RuntimeError:
        pass

    audit.fail_batch.assert_called_once_with(
        batch_id="batch-001",
        total_rows=1,
        successful_rows=0,
        failed_rows=1,
        duplicate_rows=0,
        remarks="PostgreSQL connection failed",
    )
    
    extractor.extract.assert_called_once()
    transformer.transform.assert_called_once()
    validator.validate.assert_called_once_with(
        transformed_record
    )
    loader.load.assert_called_once_with(
        [transformed_record]
    )

def test_dhis2_pipeline_treats_duplicates_as_successfully_processed():
    extractor = Mock()
    transformer = Mock()
    validator = Mock()
    loader = Mock()

    extractor.extract.return_value = {
        "dataSet": "TEST_DATASET",
        "dataValues": [
            {
                "dataElement": "ELEMENT_1",
                "orgUnit": "ORG_1",
                "period": "202608",
                "value": "10",
            }
        ],
    }

    transformed_record = Mock()
    transformer.transform.return_value = transformed_record
    validator.validate.return_value = True

    loader.load.return_value = LoadResult(
        inserted_rows=0,
        duplicate_rows=1,
    )

    audit = Mock(spec=AuditService)
    audit.start_batch.return_value = "batch-001"

    pipeline = DHIS2Pipeline(
        extractor=extractor,
        transformer=transformer,
        validator=validator,
        loader=loader,
        audit=audit,
        config=PipelineConfig(
            environment="TEST",
            initiated_by="pytest",
            batch_name="duplicate-test",
        ),
    )

    result = pipeline.run(
        PipelineRequest(
            endpoint="/api/dataValueSets",
            params={"period": "202608"},
        )
    )

    assert result == 0

    audit.complete_batch.assert_called_once_with(
        batch_id="batch-001",
        total_rows=1,
        successful_rows=1,
        failed_rows=0,
        duplicate_rows=1,
    )
