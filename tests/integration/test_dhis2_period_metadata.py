"""Integration tests for DHIS2 period metadata."""

from datetime import date

import psycopg
import pytest

from hip.config.database import DatabaseSettings


@pytest.fixture
def connection():
    settings = DatabaseSettings.from_environment()

    with psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.username,
        password=settings.password,
    ) as connection:
        yield connection
        connection.rollback()


def test_dhis2_period_metadata_contract(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO silver.dhis2_period (
                source_instance,
                period_type,
                period,
                period_start_date,
                period_end_date
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
                source_instance,
                period_type,
                period,
                period_start_date,
                period_end_date
            """,
            (
                "period_test",
                "Monthly",
                "202604",
                date(2026, 4, 1),
                date(2026, 4, 30),
            ),
        )

        row = cursor.fetchone()

    assert row == (
        "period_test",
        "Monthly",
        "202604",
        date(2026, 4, 1),
        date(2026, 4, 30),
    )


def test_dhis2_period_metadata_is_source_scoped(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO silver.dhis2_period (
                source_instance,
                period_type,
                period,
                period_start_date,
                period_end_date
            )
            VALUES
                (%s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s)
            """,
            (
                "period_source_a",
                "Monthly",
                "202604",
                date(2026, 4, 1),
                date(2026, 4, 30),
                "period_source_b",
                "Monthly",
                "202604",
                date(2026, 4, 1),
                date(2026, 4, 30),
            ),
        )


def test_dhis2_period_metadata_rejects_duplicate_key(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO silver.dhis2_period (
                source_instance,
                period_type,
                period,
                period_start_date,
                period_end_date
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                "period_duplicate_test",
                "Monthly",
                "202604",
                date(2026, 4, 1),
                date(2026, 4, 30),
            ),
        )

        with pytest.raises(psycopg.errors.UniqueViolation):
            cursor.execute(
                """
                INSERT INTO silver.dhis2_period (
                    source_instance,
                    period_type,
                    period,
                    period_start_date,
                    period_end_date
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    "period_duplicate_test",
                    "Monthly",
                    "202604",
                    date(2026, 4, 1),
                    date(2026, 4, 30),
                ),
            )


def test_dhis2_period_metadata_rejects_reversed_dates(connection):
    with connection.cursor() as cursor, pytest.raises(psycopg.errors.CheckViolation):
        cursor.execute(
            """
                INSERT INTO silver.dhis2_period (
                    source_instance,
                    period_type,
                    period,
                    period_start_date,
                    period_end_date
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
            (
                "period_invalid_test",
                "Monthly",
                "202604",
                date(2026, 4, 30),
                date(2026, 4, 1),
            ),
        )
