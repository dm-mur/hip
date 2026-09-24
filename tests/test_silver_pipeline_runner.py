from hip.config.database import DatabaseSettings
from hip.config.settings import DHIS2Settings
from hip.loaders.result import LoadResult
from hip.pipelines.silver_runner import SilverDHIS2Runner


def test_silver_runner_constructs_and_runs_pipeline(
    monkeypatch,
):
    database_settings = DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test-password",
    )

    dhis2_settings = DHIS2Settings(
        base_url="https://example.org",
        username="test-user",
        password="test-password",
    )

    captured = {}

    class FakePipeline:
        def __init__(
            self,
            *,
            settings,
            repository,
            dataset_sync,
            metadata_resolver,
            transformer,
            loader,
        ):
            captured["settings"] = settings
            captured["repository"] = repository
            captured["dataset_sync"] = dataset_sync
            captured["metadata_resolver"] = metadata_resolver
            captured["transformer"] = transformer
            captured["loader"] = loader

        def run(
            self,
            *,
            source_instance,
            limit=None,
        ):
            captured["source_instance"] = source_instance
            captured["limit"] = limit

            return LoadResult(
                inserted_rows=17,
                duplicate_rows=3,
            )

    monkeypatch.setattr(
        "hip.pipelines.silver_runner.SilverDHIS2Pipeline",
        FakePipeline,
    )

    result = SilverDHIS2Runner.run(
        source_instance="test_dhis2",
        database_settings=database_settings,
        dhis2_settings=dhis2_settings,
        limit=500,
    )

    assert result == LoadResult(
        inserted_rows=17,
        duplicate_rows=3,
    )

    assert captured["settings"] == database_settings
    assert captured["source_instance"] == "test_dhis2"
    assert captured["limit"] == 500


def test_silver_runner_binds_metadata_service_to_source_instance(
    monkeypatch,
):
    database_settings = DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test-password",
    )

    dhis2_settings = DHIS2Settings(
        base_url="https://example.org",
        username="test-user",
        password="test-password",
    )

    captured = {}

    class FakeMetadataService:
        def __init__(
            self,
            *,
            source_instance,
            settings,
        ):
            captured["metadata_source_instance"] = source_instance
            captured["dhis2_settings"] = settings

    class FakePipeline:
        def __init__(self, **kwargs):
            pass

        def run(
            self,
            *,
            source_instance,
            limit=None,
        ):
            captured["pipeline_source_instance"] = source_instance

            return LoadResult(
                inserted_rows=0,
                duplicate_rows=0,
            )

    monkeypatch.setattr(
        "hip.pipelines.silver_runner.DHIS2APIMetadataService",
        FakeMetadataService,
    )

    monkeypatch.setattr(
        "hip.pipelines.silver_runner.SilverDHIS2Pipeline",
        FakePipeline,
    )

    SilverDHIS2Runner.run(
        source_instance="instance_a",
        database_settings=database_settings,
        dhis2_settings=dhis2_settings,
    )

    assert captured["metadata_source_instance"] == "instance_a"
    assert captured["pipeline_source_instance"] == "instance_a"
    assert captured["dhis2_settings"] == dhis2_settings

def test_silver_runner_constructs_dataset_metadata_sync(
    monkeypatch,
):
    database_settings = DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test-password",
    )

    dhis2_settings = DHIS2Settings(
        base_url="https://example.org",
        username="test-user",
        password="test-password",
    )

    captured = {}

    class FakeDatasetRepository:
        def __init__(self, settings):
            captured["dataset_repository_settings"] = settings

    class FakeDatasetMetadataService:
        def __init__(
            self,
            *,
            source_instance,
            settings,
        ):
            captured["dataset_source_instance"] = source_instance
            captured["dataset_dhis2_settings"] = settings

    class FakeDatasetSync:
        def __init__(
            self,
            *,
            api_service,
            repository,
        ):
            captured["dataset_api_service"] = api_service
            captured["dataset_repository"] = repository

    class FakePipeline:
        def __init__(
            self,
            *,
            dataset_sync,
            **kwargs,
        ):
            captured["pipeline_dataset_sync"] = dataset_sync

        def run(
            self,
            *,
            source_instance,
            limit=None,
        ):
            return LoadResult(
                inserted_rows=0,
                duplicate_rows=0,
            )

    monkeypatch.setattr(
        "hip.pipelines.silver_runner.DHIS2DatasetRepository",
        FakeDatasetRepository,
    )

    monkeypatch.setattr(
        "hip.pipelines.silver_runner.DHIS2DatasetMetadataService",
        FakeDatasetMetadataService,
    )

    monkeypatch.setattr(
        "hip.pipelines.silver_runner.DHIS2DatasetMetadataSync",
        FakeDatasetSync,
    )

    monkeypatch.setattr(
        "hip.pipelines.silver_runner.SilverDHIS2Pipeline",
        FakePipeline,
    )

    SilverDHIS2Runner.run(
        source_instance="instance_a",
        database_settings=database_settings,
        dhis2_settings=dhis2_settings,
    )

    assert (
        captured["dataset_repository_settings"]
        == database_settings
    )
    assert captured["dataset_source_instance"] == "instance_a"
    assert captured["dataset_dhis2_settings"] == dhis2_settings

    assert (
        captured["pipeline_dataset_sync"]
        is not None
    )
