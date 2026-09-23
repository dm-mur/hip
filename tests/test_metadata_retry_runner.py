from hip.config.database import DatabaseSettings
from hip.config.settings import DHIS2Settings
from hip.pipelines.metadata_retry_runner import DHIS2MetadataRetryRunner


def test_metadata_retry_runner_constructs_and_runs_service(
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

    class FakeRetryService:
        def __init__(
            self,
            *,
            repository,
            api_service,
            silver_loader,
        ):
            captured["repository"] = repository
            captured["api_service"] = api_service
            captured["silver_loader"] = silver_loader

        def retry(
            self,
            *,
            source_instance,
        ):
            captured["retry_source_instance"] = source_instance

            return {
                "attempted": 5,
                "resolved": 2,
                "unresolved": 3,
            }

    monkeypatch.setattr(
        "hip.pipelines.metadata_retry_runner.DHIS2APIMetadataService",
        FakeMetadataService,
    )

    monkeypatch.setattr(
        "hip.pipelines.metadata_retry_runner.DHIS2MetadataRetryService",
        FakeRetryService,
    )

    result = DHIS2MetadataRetryRunner.run(
        source_instance="instance_a",
        database_settings=database_settings,
        dhis2_settings=dhis2_settings,
    )

    assert result == {
        "attempted": 5,
        "resolved": 2,
        "unresolved": 3,
    }

    assert captured["metadata_source_instance"] == "instance_a"
    assert captured["retry_source_instance"] == "instance_a"
    assert captured["dhis2_settings"] == dhis2_settings
