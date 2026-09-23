"""Integration tests for DHIS2 dataset metadata."""

import os

import psycopg
import pytest


def get_connection():
    """Return a PostgreSQL connection for integration testing."""

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=os.getenv("POSTGRES_PORT", "5435"),
        dbname=os.getenv("POSTGRES_DB", "hip"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.environ["POSTGRES_PASSWORD"],
    )


def test_dhis2_dataset_metadata_contract():
    """Dataset metadata should preserve source-scoped DHIS2 configuration."""

    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO silver.dhis2_dataset (
                source_instance,
                dataset_id,
                dataset_name,
                period_type
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                source_instance,
                dataset_id,
                dataset_name,
                period_type,
                resolved_at
            """,
            (
                "dataset_metadata_test",
                "DATASET_TEST_001",
                "Test Reporting Dataset",
                "Monthly",
            ),
        )

        row = cursor.fetchone()

        cursor.execute(
            """
            DELETE FROM silver.dhis2_dataset
            WHERE source_instance = %s
              AND dataset_id = %s
            """,
            (
                "dataset_metadata_test",
                "DATASET_TEST_001",
            ),
        )

    assert row is not None

    (
        source_instance,
        dataset_id,
        dataset_name,
        period_type,
        resolved_at,
    ) = row

    assert source_instance == "dataset_metadata_test"
    assert dataset_id == "DATASET_TEST_001"
    assert dataset_name == "Test Reporting Dataset"
    assert period_type == "Monthly"
    assert resolved_at is not None


def test_dhis2_dataset_metadata_is_source_scoped():
    """The same dataset UID may exist independently across DHIS2 instances."""

    rows = (
        (
            "dataset_source_a",
            "SHARED_DATASET",
            "Dataset A",
            "Monthly",
        ),
        (
            "dataset_source_b",
            "SHARED_DATASET",
            "Dataset B",
            "Quarterly",
        ),
    )

    with get_connection() as connection, connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO silver.dhis2_dataset (
                source_instance,
                dataset_id,
                dataset_name,
                period_type
            )
            VALUES (%s, %s, %s, %s)
            """,
            rows,
        )

        cursor.execute(
            """
            SELECT
                source_instance,
                dataset_name,
                period_type
            FROM silver.dhis2_dataset
            WHERE dataset_id = %s
            ORDER BY source_instance
            """,
            ("SHARED_DATASET",),
        )

        results = cursor.fetchall()

        cursor.execute(
            """
            DELETE FROM silver.dhis2_dataset
            WHERE dataset_id = %s
              AND source_instance IN (%s, %s)
            """,
            (
                "SHARED_DATASET",
                "dataset_source_a",
                "dataset_source_b",
            ),
        )

    assert results == [
        (
            "dataset_source_a",
            "Dataset A",
            "Monthly",
        ),
        (
            "dataset_source_b",
            "Dataset B",
            "Quarterly",
        ),
    ]


def test_dhis2_dataset_metadata_rejects_duplicate_source_dataset():
    """A dataset UID should be unique within one DHIS2 source instance."""

    with (
        pytest.raises(psycopg.errors.UniqueViolation),
        get_connection() as connection,
        connection.cursor() as cursor,
    ):
            cursor.execute(
                """
                INSERT INTO silver.dhis2_dataset (
                    source_instance,
                    dataset_id,
                    dataset_name,
                    period_type
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    "dataset_unique_test",
                    "DATASET_UNIQUE_001",
                    "Original Dataset",
                    "Monthly",
                ),
            )

            cursor.execute(
                """
                INSERT INTO silver.dhis2_dataset (
                    source_instance,
                    dataset_id,
                    dataset_name,
                    period_type
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    "dataset_unique_test",
                    "DATASET_UNIQUE_001",
                    "Duplicate Dataset",
                    "Quarterly",
                ),
            )
