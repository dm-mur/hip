from unittest.mock import MagicMock, Mock, patch

from hip.config.database import DatabaseSettings
from hip.loaders.result import LoadResult
from hip.pipelines.silver_dhis2 import SilverDHIS2Pipeline


def test_silver_pipeline_processes_unprocessed_bronze_records():
    settings = DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test_password",
    )

    repository = Mock()
    transformer = Mock()
    loader = Mock()

    bronze_records = [
        {"bronze_id": 101},
        {"bronze_id": 102},
    ]

    repository.fetch_unprocessed.return_value = bronze_records

    observation_1 = Mock()
    observation_2 = Mock()

    transformer.transform.side_effect = [
        observation_1,
        observation_2,
    ]

    loader.load.return_value = LoadResult(
        inserted_rows=2,
        duplicate_rows=0,
    )

    connection = MagicMock()

    with patch(
        "hip.pipelines.silver_dhis2.psycopg.connect",
        return_value=connection,
    ):
        pipeline = SilverDHIS2Pipeline(
            settings=settings,
            repository=repository,
            transformer=transformer,
            loader=loader,
        )

        result = pipeline.run(limit=100)

    repository.fetch_unprocessed.assert_called_once_with(
        connection.__enter__.return_value,
        limit=100,
    )

    assert transformer.transform.call_count == 2

    transformer.transform.assert_any_call(
        bronze_records[0]
    )
    transformer.transform.assert_any_call(
        bronze_records[1]
    )

    loader.load.assert_called_once_with(
        [observation_1, observation_2]
    )

    assert result.inserted_rows == 2
    assert result.duplicate_rows == 0

def test_silver_pipeline_handles_no_unprocessed_records():
    settings = DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test_password",
    )

    repository = Mock()
    transformer = Mock()
    loader = Mock()

    repository.fetch_unprocessed.return_value = []

    loader.load.return_value = LoadResult(
        inserted_rows=0,
        duplicate_rows=0,
    )

    connection = MagicMock()

    with patch(
        "hip.pipelines.silver_dhis2.psycopg.connect",
        return_value=connection,
    ):
        pipeline = SilverDHIS2Pipeline(
            settings=settings,
            repository=repository,
            transformer=transformer,
            loader=loader,
        )

        result = pipeline.run(limit=100)

    transformer.transform.assert_not_called()
    loader.load.assert_called_once_with([])

    assert result.inserted_rows == 0
    assert result.duplicate_rows == 0
