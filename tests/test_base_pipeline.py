import pytest

from hip.pipelines.base import BasePipeline
from hip.pipelines.config import PipelineConfig


def test_base_pipeline_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BasePipeline()


def test_pipeline_config_stores_execution_configuration():
    config = PipelineConfig(
        environment="DEV",
        initiated_by="pytest",
        batch_name="Test Pipeline",
    )

    assert config.environment == "DEV"
    assert config.initiated_by == "pytest"
    assert config.batch_name == "Test Pipeline"


def test_pipeline_config_rejects_invalid_environment():
    with pytest.raises(ValueError, match="Invalid environment"):
        PipelineConfig(
            environment="PRODUCTION",
            initiated_by="pytest",
            batch_name="Test Pipeline",
        )


def test_pipeline_config_rejects_empty_initiated_by():
    with pytest.raises(ValueError, match="initiated_by"):
        PipelineConfig(
            environment="DEV",
            initiated_by="",
            batch_name="Test Pipeline",
        )


def test_pipeline_config_rejects_empty_batch_name():
    with pytest.raises(ValueError, match="batch_name"):
        PipelineConfig(
            environment="DEV",
            initiated_by="pytest",
            batch_name="",
        )


def test_pipeline_config_is_immutable():
    config = PipelineConfig(
        environment="DEV",
        initiated_by="pytest",
        batch_name="Test Pipeline",
    )

    with pytest.raises(AttributeError):
        config.environment = "PROD"