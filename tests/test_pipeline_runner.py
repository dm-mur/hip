from unittest.mock import Mock, patch

from hip.config.database import DatabaseSettings
from hip.config.settings import DHIS2Settings
from hip.config.source import DHIS2SourceConfig
from hip.pipelines.config import PipelineConfig
from hip.pipelines.runner import PipelineRunner


def test_pipeline_runner_creates_and_runs_pipeline():
    source_config = DHIS2SourceConfig(
        source_instance="test_dhis2",
        settings=DHIS2Settings(
            base_url="https://example.org",
            username="test_user",
            password="test_password",
        ),
    )

    database_settings = DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test_password",
    )

    pipeline_config = PipelineConfig(
        environment="TEST",
        initiated_by="pytest",
        batch_name="Runner Test",
    )

    mock_pipeline = Mock()
    mock_pipeline.run.return_value = 10

    with patch(
        "hip.pipelines.runner.PipelineFactory.create",
        return_value=mock_pipeline,
    ) as mock_create:

        result = PipelineRunner.run(
            pipeline_type="dhis2",
            source_config=source_config,
            database_settings=database_settings,
            pipeline_config=pipeline_config,
            endpoint="/api/dataValueSets",
        )

    assert result == 10

    mock_create.assert_called_once_with(
        pipeline_type="dhis2",
        source_config=source_config,
        database_settings=database_settings,
        pipeline_config=pipeline_config,
    )

    mock_pipeline.run.assert_called_once_with(
        endpoint="/api/dataValueSets",
        params=None,
    )


def test_pipeline_runner_rejects_unknown_pipeline_type():
    import pytest

    with pytest.raises(ValueError, match="Unknown pipeline type"):
        PipelineRunner.run(
            pipeline_type="unknown",
            source_config=None,
            database_settings=None,
            pipeline_config=None,
        )


def test_pipeline_runner_passes_execution_arguments_to_pipeline():
    source_config = DHIS2SourceConfig(
        source_instance="test_dhis2",
        settings=DHIS2Settings(
            base_url="https://example.org",
            username="test_user",
            password="test_password",
        ),
    )

    database_settings = DatabaseSettings(
        host="localhost",
        port=5435,
        database="hip",
        username="postgres",
        password="test_password",
    )

    pipeline_config = PipelineConfig(
        environment="TEST",
        initiated_by="pytest",
        batch_name="Runner Test",
    )

    mock_pipeline = Mock()
    mock_pipeline.run.return_value = 10

    with patch(
        "hip.pipelines.runner.PipelineFactory.create",
        return_value=mock_pipeline,
    ):

        result = PipelineRunner.run(
            pipeline_type="dhis2",
            source_config=source_config,
            database_settings=database_settings,
            pipeline_config=pipeline_config,
            endpoint="/api/dataValueSets",
            params={
                "period": "2026-08",
                "dataSet": "TEST_DATASET",
            },
        )

    assert result == 10

    mock_pipeline.run.assert_called_once_with(
        endpoint="/api/dataValueSets",
        params={
            "period": "2026-08",
            "dataSet": "TEST_DATASET",
        },
    )
