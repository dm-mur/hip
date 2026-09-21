from unittest.mock import MagicMock, Mock

from hip.config.database import DatabaseSettings
from hip.repositories.bronze import BronzeDHIS2Repository


def test_bronze_repository_fetches_unprocessed_records():
    settings = Mock(spec=DatabaseSettings)
    repository = BronzeDHIS2Repository(settings)

    cursor = Mock()
    cursor.description = [
        Mock(name="bronze_id"),
        Mock(name="period"),
    ]

    cursor.description[0].name = "bronze_id"
    cursor.description[1].name = "period"

    cursor.fetchall.return_value = [
        (101, "202605"),
        (102, "202606"),
    ]

    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor

    result = repository.fetch_unprocessed(
        connection,
        limit=100,
    )

    assert result == [
        {
            "bronze_id": 101,
            "period": "202605",
        },
        {
            "bronze_id": 102,
            "period": "202606",
        },
    ]

    query, params = cursor.execute.call_args.args

    assert "LEFT JOIN silver.dhis2_observation" in query
    assert "WHERE s.bronze_id IS NULL" in query
    assert "ORDER BY b.bronze_id" in query
    assert "LIMIT %s" in query
    assert params == (100,)
