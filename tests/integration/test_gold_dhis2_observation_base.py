"""Integration tests for the Gold DHIS2 observation base view."""

import psycopg

from hip.config.database import DatabaseSettings


def test_gold_dhis2_observation_base_exposes_analytics_contract():
    """Gold should expose authoritative dataset and period metadata."""

    settings = DatabaseSettings.from_environment()

    with (
        psycopg.connect(
            host=settings.host,
            port=settings.port,
            dbname=settings.database,
            user=settings.username,
            password=settings.password,
        ) as connection,
        connection.cursor() as cursor,
    ):
            cursor.execute(
                """
                SELECT
                    source_instance,
                    dataset_id,
                    dataset_name,
                    period,
                    period_type,
                    period_year,
                    period_month,
                    period_start_date,
                    period_end_date,
                    reported_value,
                    quality_status
                FROM gold.dhis2_observation_base
                WHERE source_instance = %s
                  AND dataset_id = %s
                  AND period = %s
                ORDER BY org_unit_id, data_element_id
                LIMIT 1
                """,
                (
                    "live_test",
                    "wRQAtvYToKU",
                    "202604",
                ),
            )

            row = cursor.fetchone()

    assert row is not None

    assert row[0] == "live_test"
    assert row[1] == "wRQAtvYToKU"
    assert row[2] == "Care & Tx Reporting Tool"
    assert row[3] == "202604"
    assert row[4] == "Monthly"
    assert row[5] == 2026
    assert row[6] == 4
    assert row[7].isoformat() == "2026-04-01"
    assert row[8].isoformat() == "2026-04-30"
    assert row[9] is not None
    assert row[10] == "VALID"

def test_gold_preserves_observation_without_dataset_metadata():
    """Gold should not drop observations when dataset metadata is unavailable."""

    settings = DatabaseSettings.from_environment()

    source_instance = "gold_missing_metadata_test"
    dataset_id = "DATASET_WITHOUT_METADATA"

    with psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.username,
        password=settings.password,
    ) as connection:
        with connection.cursor() as cursor:
            # Create the audit batch required by Bronze and Silver.
            cursor.execute(
                """
                INSERT INTO audit.etl_batch (
                    batch_id,
                    source_system,
                    started_at,
                    status,
                    batch_name,
                    environment,
                    initiated_by
                )
                VALUES (
                    gen_random_uuid(),
                    'DHIS2',
                    NOW(),
                    'SUCCESS',
                    'gold missing metadata test',
                    'TEST',
                    'integration-test'
                )
                RETURNING batch_id
                """
            )

            batch_id = cursor.fetchone()[0]

            # Create a Bronze observation without corresponding
            # dataset metadata.
            cursor.execute(
                """
                INSERT INTO bronze.dhis2_data (
                    batch_id,
                    source_system,
                    source_instance,
                    dataset_id,
                    data_element,
                    org_unit,
                    period,
                    value,
                    record_hash
                )
                VALUES (
                    %s,
                    'DHIS2',
                    %s,
                    %s,
                    'DE_GOLD_TEST',
                    'OU_GOLD_TEST',
                    '202604',
                    '42',
                    'gold-missing-metadata-test-record'
                )
                RETURNING bronze_id
                """,
                (
                    batch_id,
                    source_instance,
                    dataset_id,
                ),
            )

            bronze_id = cursor.fetchone()[0]

            # Promote the observation to Silver.
            cursor.execute(
                """
                INSERT INTO silver.dhis2_observation (
                    bronze_id,
                    batch_id,
                    source_system,
                    source_instance,
                    dataset_id,
                    data_element,
                    org_unit,
                    period,
                    value_raw,
                    value_numeric,
                    quality_status
                )
                VALUES (
                    %s,
                    %s,
                    'DHIS2',
                    %s,
                    %s,
                    'DE_GOLD_TEST',
                    'OU_GOLD_TEST',
                    '202604',
                    '42',
                    42,
                    'VALID'
                )
                """,
                (
                    bronze_id,
                    batch_id,
                    source_instance,
                    dataset_id,
                ),
            )

            # Gold must retain the observation even though
            # silver.dhis2_dataset has no matching metadata row.
            cursor.execute(
                """
                SELECT
                    dataset_id,
                    dataset_name,
                    period,
                    period_type,
                    reported_value,
                    quality_status
                FROM gold.dhis2_observation_base
                WHERE source_instance = %s
                  AND dataset_id = %s
                """,
                (
                    source_instance,
                    dataset_id,
                ),
            )

            row = cursor.fetchone()

        # Do not leave integration-test data in PostgreSQL.
        connection.rollback()

    assert row is not None
    assert row[0] == dataset_id
    assert row[1] is None
    assert row[2] == "202604"
    assert row[3] is None
    assert row[4] == 42
    assert row[5] == "VALID"