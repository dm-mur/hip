from unittest.mock import MagicMock, Mock, patch

from hip.config.database import DatabaseSettings
from hip.loaders.result import LoadResult
from hip.metadata.resolver import DHIS2MetadataLookups
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
    metadata_resolver = Mock()
    transformer = Mock()
    loader = Mock()

    bronze_records = [
        {
            "bronze_id": 101,
            "source_instance": "test_instance",
            "data_element": "DE001",
            "data_element_name": None,
            "org_unit": "OU001",
            "org_unit_name": None,
            "category_option_combo": "COC001",
            "category_option_combo_name": None,
            "attribute_option_combo": "AOC001",
            "attribute_option_combo_name": None,
        },
        {
            "bronze_id": 102,
            "source_instance": "test_instance",
            "data_element": "DE002",
            "data_element_name": None,
            "org_unit": "OU001",
            "org_unit_name": None,
            "category_option_combo": "COC001",
            "category_option_combo_name": None,
            "attribute_option_combo": "AOC001",
            "attribute_option_combo_name": None,
        },
    ]

    repository.fetch_unprocessed.return_value = bronze_records

    metadata_resolver.resolve_many.return_value = (
        DHIS2MetadataLookups(
            data_elements={
                "DE001": "Data Element One",
                "DE002": "Data Element Two",
            },
            org_units={
                "OU001": "Organisation Unit One",
            },
            category_option_combos={
                "COC001": "Category Combo One",
            },
            attribute_option_combos={
                "AOC001": "Attribute Combo One",
            },
        )
    )

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
            metadata_resolver=metadata_resolver,
            transformer=transformer,
            loader=loader,
        )

        result = pipeline.run(
            source_instance="test_instance",
            limit=100,
        )

    repository.fetch_unprocessed.assert_called_once_with(
        connection.__enter__.return_value,
        source_instance="test_instance",
        limit=100,
    )

    assert transformer.transform.call_count == 2

    metadata_resolver.resolve_many.assert_called_once_with(
        source_instance="test_instance",
        data_elements={"DE001", "DE002"},
        org_units={"OU001"},
        category_option_combos={"COC001"},
        attribute_option_combos={"AOC001"},
    )

    transformed_records = [
        call.args[0]
        for call in transformer.transform.call_args_list
    ]

    assert transformed_records[0]["data_element_name"] == (
        "Data Element One"
    )
    assert transformed_records[1]["data_element_name"] == (
        "Data Element Two"
    )

    assert transformed_records[0]["org_unit_name"] == (
        "Organisation Unit One"
    )
    assert transformed_records[0]["category_option_combo_name"] == (
        "Category Combo One"
    )
    assert transformed_records[0]["attribute_option_combo_name"] == (
        "Attribute Combo One"
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
    metadata_resolver = Mock()
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
            metadata_resolver=metadata_resolver,
            transformer=transformer,
            loader=loader,
        )

        result = pipeline.run(
            source_instance="test_instance",
            limit=100,
        )

        repository.fetch_unprocessed.assert_called_once_with(
            connection.__enter__.return_value,
            source_instance="test_instance",
            limit=100,
        )

    metadata_resolver.resolve_many.assert_not_called()
    transformer.transform.assert_not_called()
    loader.load.assert_called_once_with([])

    assert result.inserted_rows == 0
    assert result.duplicate_rows == 0

def test_silver_pipeline_preserves_existing_bronze_metadata():
    settings = DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test_password",
    )

    repository = Mock()
    metadata_resolver = Mock()
    transformer = Mock()
    loader = Mock()

    bronze_record = {
        "bronze_id": 201,
        "source_instance": "test_instance",
        "data_element": "DE001",
        "data_element_name": "Existing Data Element",
        "org_unit": "OU001",
        "org_unit_name": "Existing Organisation Unit",
        "category_option_combo": "COC001",
        "category_option_combo_name": "Existing Category Combo",
        "attribute_option_combo": "AOC001",
        "attribute_option_combo_name": "Existing Attribute Combo",
    }

    repository.fetch_unprocessed.return_value = [
        bronze_record
    ]

    metadata_resolver.resolve_many.return_value = (
        DHIS2MetadataLookups(
            data_elements={
                "DE001": "Resolved Data Element",
            },
            org_units={
                "OU001": "Resolved Organisation Unit",
            },
            category_option_combos={
                "COC001": "Resolved Category Combo",
            },
            attribute_option_combos={
                "AOC001": "Resolved Attribute Combo",
            },
        )
    )

    observation = Mock()
    transformer.transform.return_value = observation

    loader.load.return_value = LoadResult(
        inserted_rows=1,
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
            metadata_resolver=metadata_resolver,
            transformer=transformer,
            loader=loader,
        )

        result = pipeline.run(
            source_instance="test_instance",
        )

    repository.fetch_unprocessed.assert_called_once_with(
        connection.__enter__.return_value,
        source_instance="test_instance",
        limit=None,
    )

    metadata_resolver.resolve_many.assert_called_once_with(
        source_instance="test_instance",
        data_elements={"DE001"},
        org_units={"OU001"},
        category_option_combos={"COC001"},
        attribute_option_combos={"AOC001"},
    )

    transformed_record = transformer.transform.call_args.args[0]

    assert transformed_record["data_element_name"] == (
        "Existing Data Element"
    )
    assert transformed_record["org_unit_name"] == (
        "Existing Organisation Unit"
    )
    assert transformed_record["category_option_combo_name"] == (
        "Existing Category Combo"
    )
    assert transformed_record["attribute_option_combo_name"] == (
        "Existing Attribute Combo"
    )

    loader.load.assert_called_once_with([observation])

    assert result.inserted_rows == 1
    assert result.duplicate_rows == 0
