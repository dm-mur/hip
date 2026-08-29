from hip.pipelines.config import PipelineConfig


def test_pipeline_config_stores_execution_configuration():
    config = PipelineConfig(
        environment="DEV",
        initiated_by="pytest",
        batch_name="Test Pipeline",
    )

    assert config.environment == "DEV"
    assert config.initiated_by == "pytest"
    assert config.batch_name == "Test Pipeline"
