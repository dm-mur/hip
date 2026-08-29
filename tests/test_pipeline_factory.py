from hip.config.database import DatabaseSettings
from hip.config.settings import DHIS2Settings
from hip.extractors.dhis2 import DHIS2Extractor
from hip.loaders.postgres import PostgresLoader
from hip.pipelines.config import PipelineConfig
from hip.pipelines.dhis2 import DHIS2Pipeline
from hip.pipelines.factory import PipelineFactory
from hip.transformers.dhis2 import DHIS2Transformer
from hip.validators.dhis2 import DHIS2Validator


def test_factory_creates_dhis2_pipeline():
    dhis2_settings = DHIS2Settings(
        base_url="https://example.org",
        username="test_user",
        password="test_password",
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
        batch_name="Factory Test",
    )

    pipeline = PipelineFactory.create_dhis2(
        dhis2_settings=dhis2_settings,
        database_settings=database_settings,
        pipeline_config=pipeline_config,
        source_instance="test_dhis2",
    )

    assert isinstance(pipeline, DHIS2Pipeline)
    assert isinstance(pipeline.extractor, DHIS2Extractor)
    assert isinstance(pipeline.transformer, DHIS2Transformer)
    assert isinstance(pipeline.validator, DHIS2Validator)
    assert isinstance(pipeline.loader, PostgresLoader)

    assert pipeline.transformer.source_instance == "test_dhis2"
    assert pipeline.config == pipeline_config
