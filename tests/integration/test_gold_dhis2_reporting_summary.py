import psycopg

from hip.config.database import DatabaseSettings


def test_gold_dhis2_reporting_summary_matches_live_silver_data():
    settings = DatabaseSettings.from_environment()

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
                dataset_name,
                org_unit_id,
                org_unit_name,
                period,
                observation_count,
                valid_observation_count,
                non_numeric_observation_count,
                invalid_observation_count,
                reported_value_count
            FROM gold.dhis2_reporting_summary
            WHERE source_instance = %s
              AND dataset_id = %s
              AND period = %s
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
    assert row[5] == "202604"

    assert row[6] > 0
    assert row[7] == row[6]
    assert row[8] == 0
    assert row[9] == 0
    assert row[10] == row[6]