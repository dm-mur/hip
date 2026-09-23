from decimal import Decimal
from uuid import UUID

from hip.config.database import DatabaseSettings
from hip.loaders.postgres import PostgresLoader
from hip.loaders.silver_postgres import SilverPostgresLoader
from hip.models.dhis2 import DHIS2Record
from hip.models.silver import SilverDHIS2Observation

TEST_RECORD_HASH = "silver-integration-test-record-001"


def make_bronze_record() -> DHIS2Record:
    return DHIS2Record(
        batch_id="2892bf6e-7ee5-4d60-8830-b749fbc971c3",
        source_instance="silver_integration_test",
        dataset_id="SILVER_TEST_DATASET",
        data_element="SILVER_TEST_ELEMENT",
        data_element_name="Silver Test Element",
        org_unit="SILVER_TEST_ORG_UNIT",
        org_unit_name="Silver Test Organisation",
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
            "dataElement": "SILVER_TEST_ELEMENT",
            "orgUnit": "SILVER_TEST_ORG_UNIT",
            "period": "202608",
            "value": "999",
        },
        record_hash=TEST_RECORD_HASH,
    )


def make_silver_record(
    bronze_id: int,
    *,
    category_option_combo: str | None = None,
    category_option_combo_name: str | None = None,
) -> SilverDHIS2Observation:
    return SilverDHIS2Observation(
        bronze_id=bronze_id,
        batch_id=UUID(
            "2892bf6e-7ee5-4d60-8830-b749fbc971c3"
        ),
        source_system="DHIS2",
        source_instance="silver_integration_test",
        dataset_id="SILVER_TEST_DATASET",
        data_element="SILVER_TEST_ELEMENT",
        data_element_name="Silver Test Element",
        org_unit="SILVER_TEST_ORG_UNIT",
        org_unit_name="Silver Test Organisation",
        period="202608",
        category_option_combo=category_option_combo,
        category_option_combo_name=category_option_combo_name,
        attribute_option_combo=None,
        attribute_option_combo_name=None,
        value_raw="999",
        value_numeric=Decimal(999),
        quality_status="VALID",
        quality_reason=None,
        created_at_source=None,
        last_updated_at_source=None,
    )


def test_silver_postgres_loader_is_idempotent():
    settings = DatabaseSettings.from_environment()

    bronze_loader = PostgresLoader(settings)
    silver_loader = SilverPostgresLoader(settings)

    # Remove any previous copy of this test record.
    with bronze_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_observation
            WHERE bronze_id IN (
                SELECT bronze_id
                FROM bronze.dhis2_data
                WHERE record_hash = %s
            )
            """,
            (TEST_RECORD_HASH,),
        )

        cursor.execute(
            """
            DELETE FROM bronze.dhis2_data
            WHERE record_hash = %s
            """,
            (TEST_RECORD_HASH,),
        )

    bronze_loader.load([make_bronze_record()])

    with bronze_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT bronze_id
            FROM bronze.dhis2_data
            WHERE record_hash = %s
              AND source_instance = %s
            """,
            (
                TEST_RECORD_HASH,
                "silver_integration_test",
            ),
        )

        bronze_id = cursor.fetchone()[0]

    record = make_silver_record(bronze_id)

    first_result = silver_loader.load([record])

    assert first_result.inserted_rows == 1
    assert first_result.duplicate_rows == 0

    second_result = silver_loader.load([record])

    assert second_result.inserted_rows == 0
    assert second_result.duplicate_rows == 1

    with silver_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*),
                MAX(value_numeric),
                MAX(quality_status)
            FROM silver.dhis2_observation
            WHERE bronze_id = %s
            """,
            (bronze_id,),
        )

        count, value_numeric, quality_status = cursor.fetchone()

    assert count == 1
    assert value_numeric == Decimal(999)
    assert quality_status == "VALID"

    # Silver must be deleted before its Bronze parent.
    with silver_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_observation
            WHERE bronze_id = %s
            """,
            (bronze_id,),
        )

        cursor.execute(
            """
            DELETE FROM bronze.dhis2_data
            WHERE bronze_id = %s
            """,
            (bronze_id,),
        )

def test_silver_postgres_loader_backfills_category_option_combo_name():
    settings = DatabaseSettings.from_environment()

    bronze_loader = PostgresLoader(settings)
    silver_loader = SilverPostgresLoader(settings)

    source_instance = "silver_integration_test"
    uid = "SILVER_TEST_COC"
    resolved_name = "Silver Test Category Option Combo"

    with bronze_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_observation
            WHERE bronze_id IN (
                SELECT bronze_id
                FROM bronze.dhis2_data
                WHERE record_hash = %s
            )
            """,
            (TEST_RECORD_HASH,),
        )

        cursor.execute(
            """
            DELETE FROM bronze.dhis2_data
            WHERE record_hash = %s
            """,
            (TEST_RECORD_HASH,),
        )

    bronze_loader.load([make_bronze_record()])

    with bronze_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT bronze_id
            FROM bronze.dhis2_data
            WHERE record_hash = %s
              AND source_instance = %s
            """,
            (
                TEST_RECORD_HASH,
                source_instance,
            ),
        )

        bronze_id = cursor.fetchone()[0]

    silver_loader.load(
        [
            make_silver_record(
                bronze_id,
                category_option_combo=uid,
                category_option_combo_name=None,
            )
        ]
    )

    updated = silver_loader.backfill_metadata_name(
        source_instance=source_instance,
        metadata_type="CATEGORY_OPTION_COMBO",
        uid=uid,
        name=resolved_name,
    )

    assert updated == 1

    with silver_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT category_option_combo_name
            FROM silver.dhis2_observation
            WHERE bronze_id = %s
            """,
            (bronze_id,),
        )

        row = cursor.fetchone()

    assert row is not None
    assert row[0] == resolved_name

    # Silver must be deleted before its Bronze parent.
    with silver_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_observation
            WHERE bronze_id = %s
            """,
            (bronze_id,),
        )

        cursor.execute(
            """
            DELETE FROM bronze.dhis2_data
            WHERE bronze_id = %s
            """,
            (bronze_id,),
        )

def test_silver_postgres_loader_does_not_overwrite_existing_metadata_name():
    settings = DatabaseSettings.from_environment()

    bronze_loader = PostgresLoader(settings)
    silver_loader = SilverPostgresLoader(settings)

    source_instance = "silver_integration_test"
    uid = "SILVER_TEST_COC"
    existing_name = "Existing Category Option Combo"
    recovered_name = "Recovered Category Option Combo"

    with bronze_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_observation
            WHERE bronze_id IN (
                SELECT bronze_id
                FROM bronze.dhis2_data
                WHERE record_hash = %s
            )
            """,
            (TEST_RECORD_HASH,),
        )

        cursor.execute(
            """
            DELETE FROM bronze.dhis2_data
            WHERE record_hash = %s
            """,
            (TEST_RECORD_HASH,),
        )

    bronze_loader.load([make_bronze_record()])

    with bronze_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT bronze_id
            FROM bronze.dhis2_data
            WHERE record_hash = %s
              AND source_instance = %s
            """,
            (
                TEST_RECORD_HASH,
                source_instance,
            ),
        )

        bronze_id = cursor.fetchone()[0]

    silver_loader.load(
        [
            make_silver_record(
                bronze_id,
                category_option_combo=uid,
                category_option_combo_name=existing_name,
            )
        ]
    )

    updated = silver_loader.backfill_metadata_name(
        source_instance=source_instance,
        metadata_type="CATEGORY_OPTION_COMBO",
        uid=uid,
        name=recovered_name,
    )

    assert updated == 0

    with silver_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT category_option_combo_name
            FROM silver.dhis2_observation
            WHERE bronze_id = %s
            """,
            (bronze_id,),
        )

        row = cursor.fetchone()

    assert row is not None
    assert row[0] == existing_name

    with silver_loader._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_observation
            WHERE bronze_id = %s
            """,
            (bronze_id,),
        )

        cursor.execute(
            """
            DELETE FROM bronze.dhis2_data
            WHERE bronze_id = %s
            """,
            (bronze_id,),
        )
