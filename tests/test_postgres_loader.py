from dataclasses import replace

from hip.config.database import DatabaseSettings
from hip.loaders.postgres import PostgresLoader
from hip.models.dhis2 import DHIS2Record


TEST_RECORD_HASH = "integration-test-record-001"


def make_record() -> DHIS2Record:
    return DHIS2Record(
        batch_id="2892bf6e-7ee5-4d60-8830-b749fbc971c3",
        source_instance="integration_test",
        dataset_id="TEST_DATASET",
        data_element="TEST_ELEMENT",
        data_element_name="Integration Test Element",
        org_unit="TEST_ORG_UNIT",
        org_unit_name="Integration Test Organisation",
        period="202608",
        category_option_combo=None,
        category_option_combo_name=None,
        attribute_option_combo=None,
        attribute_option_combo_name=None,
        value="999",
        comment=None,
        followup=None,
        stored_by=None,
        created_at_source=None,
        last_updated_at_source=None,
        raw_payload={
            "dataElement": "TEST_ELEMENT",
            "orgUnit": "TEST_ORG_UNIT",
            "period": "202608",
            "value": "999",
        },
        record_hash=TEST_RECORD_HASH,
    )


def test_postgres_loader_is_idempotent():
    settings = DatabaseSettings.from_environment()
    loader = PostgresLoader(settings)

    record = make_record()

    # Remove only this test record so the test starts clean.
    with loader._connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM bronze.dhis2_data
                WHERE record_hash = %s
                """,
                (TEST_RECORD_HASH,),
            )

    # First load should insert the record.
    first_result = loader.load([record])

    assert first_result == 1

    # Loading the exact same record again should not insert a duplicate.
    second_result = loader.load([record])

    assert second_result == 0

    # Confirm that exactly one copy exists.
    with loader._connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM bronze.dhis2_data
                WHERE record_hash = %s
                """,
                (TEST_RECORD_HASH,),
            )

            count = cursor.fetchone()[0]

    assert count == 1

    # Clean up the test record.
    with loader._connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM bronze.dhis2_data
                WHERE record_hash = %s
                """,
                (TEST_RECORD_HASH,),
            )

def test_postgres_loader_allows_same_hash_for_different_instances():
    settings = DatabaseSettings.from_environment()
    loader = PostgresLoader(settings)

    record_1 = make_record()

    record_2 = replace(
        record_1,
        source_instance="another_integration_test",
    )

    # Remove both possible test records so the test starts clean.
    with loader._connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM bronze.dhis2_data
                WHERE record_hash = %s
                """,
                (TEST_RECORD_HASH,),
            )

    first_result = loader.load([record_1])
    second_result = loader.load([record_2])

    assert first_result == 1
    assert second_result == 1

    with loader._connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM bronze.dhis2_data
                WHERE record_hash = %s
                """,
                (TEST_RECORD_HASH,),
            )

            count = cursor.fetchone()[0]

    assert count == 2

    # Clean up both test records.
    with loader._connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM bronze.dhis2_data
                WHERE record_hash = %s
                """,
                (TEST_RECORD_HASH,),
            )