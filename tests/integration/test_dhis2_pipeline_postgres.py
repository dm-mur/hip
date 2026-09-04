from unittest.mock import Mock

import psycopg

from hip.audit.service import AuditService
from hip.config.database import DatabaseSettings
from hip.extractors.dhis2 import DHIS2Extractor
from hip.loaders.postgres import PostgresLoader
from hip.pipelines.config import PipelineConfig
from hip.pipelines.dhis2 import DHIS2Pipeline
from hip.pipelines.request import PipelineRequest
from hip.transformers.dhis2 import DHIS2Transformer
from hip.validators.dhis2 import DHIS2Validator

TEST_RECORD_HASH = None


def test_dhis2_pipeline_writes_to_real_postgres():
    settings = DatabaseSettings.from_environment()

    # ------------------------------------------------------------------
    # 1. Mock the external DHIS2 response.
    # ------------------------------------------------------------------

    extractor = Mock(spec=DHIS2Extractor)

    extractor.extract.return_value = {
        "dataSet": "INTEGRATION_DATASET",
        "period": "202608",
        "orgUnit": "INTEGRATION_ORG",
        "dataValues": [
            {
                "dataElement": "INTEGRATION_ELEMENT",
                "orgUnit": "INTEGRATION_ORG",
                "period": "202608",
                "categoryOptionCombo": "DEFAULT",
                "attributeOptionCombo": "DEFAULT",
                "value": "999",
                "comment": None,
                "followup": False,
                "storedBy": "pytest",
                "created": "2026-08-31T10:00:00.000",
                "lastUpdated": "2026-08-31T10:00:00.000",
            }
        ],
    }

    # ------------------------------------------------------------------
    # 2. Create the real HIP components.
    # ------------------------------------------------------------------

    transformer = DHIS2Transformer(
        source_instance="integration_test",
    )

    validator = DHIS2Validator()
    loader = PostgresLoader(settings)
    audit = AuditService(settings)

    # ------------------------------------------------------------------
    # 3.Create the real HIP pipeline components.
    # ------------------------------------------------------------------

    batch_ids = []

    original_start_batch = audit.start_batch

    def capture_batch_id(*args, **kwargs):
        batch_id = original_start_batch(*args, **kwargs)
        batch_ids.append(batch_id)
        return batch_id

    audit.start_batch = Mock(side_effect=capture_batch_id)

    pipeline = DHIS2Pipeline(
        extractor=extractor,
        transformer=transformer,
        validator=validator,
        loader=loader,
        audit=audit,
        config=PipelineConfig(
            environment="TEST",
            initiated_by="pytest",
            batch_name="DHIS2 Integration Test",
        ),
    )

    # ------------------------------------------------------------------
    # 4. Remove the test record if it already exists.
    # ------------------------------------------------------------------

    raw_test_record = {
        **extractor.extract.return_value["dataValues"][0],
        "dataSet": extractor.extract.return_value["dataSet"],
    }

    record_hash = transformer._generate_record_hash(
        raw_test_record
    )

    with psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.username,
        password=settings.password,
    ) as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM bronze.dhis2_data
            WHERE record_hash = %s
            """,
            (record_hash,),
        )

    # ------------------------------------------------------------------
    # 5. Run the actual pipeline.
    # ------------------------------------------------------------------

    result = pipeline.run(
        request=PipelineRequest(
            endpoint="/api/dataValueSets",
            params={"period": "202608"},
        )
    )
    batch_id = batch_ids[0]

    assert result == 1

    # ------------------------------------------------------------------
    # 6. Verify Bronze data.
    # ------------------------------------------------------------------

    with psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.username,
        password=settings.password,
    ) as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                source_instance,
                dataset_id,
                data_element,
                org_unit,
                period,
                category_option_combo,
                attribute_option_combo,
                value,
                stored_by,
                created_at_source,
                last_updated_at_source,
                record_hash
            FROM bronze.dhis2_data
            WHERE record_hash = %s
            """,
            (record_hash,),
        )

        bronze_row = cursor.fetchone()

    assert bronze_row is not None

    (
        source_instance,
        dataset_id,
        data_element,
        org_unit,
        period,
        category_option_combo,
        attribute_option_combo,
        value,
        stored_by,
        created_at_source,
        last_updated_at_source,
        record_hash,
    ) = bronze_row

    assert source_instance == "integration_test"
    assert dataset_id == "INTEGRATION_DATASET"
    assert data_element == "INTEGRATION_ELEMENT"
    assert org_unit == "INTEGRATION_ORG"
    assert period == "202608"
    assert category_option_combo == "DEFAULT"
    assert attribute_option_combo == "DEFAULT"
    assert value == "999"
    assert stored_by == "pytest"
    assert created_at_source is not None
    assert last_updated_at_source is not None
    assert record_hash == bronze_row[11]

    # ------------------------------------------------------------------
    # 7. Verify the audit record.
    # ------------------------------------------------------------------

    with psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.username,
        password=settings.password,
    ) as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT
                    status,
                    total_rows,
                    successful_rows,
                    failed_rows,
                    completed_at,
                    duration_seconds
                FROM audit.etl_batch
                WHERE batch_id = %s
                """,
            (batch_id,),
        )

        audit_row = cursor.fetchone()

    assert audit_row is not None

    (
        status,
        total_rows,
        successful_rows,
        failed_rows,
        completed_at,
        duration_seconds,
    ) = audit_row

    assert status == "SUCCESS"
    assert total_rows == 1
    assert successful_rows == 1
    assert failed_rows == 0
    assert completed_at is not None
    assert duration_seconds is not None
    assert duration_seconds >= 0
