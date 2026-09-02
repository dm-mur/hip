import pytest

from hip.config.database import DatabaseSettings
from hip.config.settings import DHIS2Settings
from hip.config.source import DHIS2SourceConfig
from hip.extractors.dhis2 import DHIS2Extractor
from hip.loaders.postgres import PostgresLoader
from hip.pipelines.base import BasePipeline
from hip.pipelines.config import PipelineConfig
from hip.pipelines.dhis2 import DHIS2Pipeline
from hip.pipelines.factory import PipelineFactory
from hip.transformers.dhis2 import DHIS2Transformer
from hip.validators.dhis2 import DHIS2Validator


class CustomPipeline(BasePipeline):
    """Minimal concrete pipeline used for factory tests."""

    pipeline_type = "custom"

    def run(self, request):
        return 1


@pytest.fixture(autouse=True)
def reset_pipeline_registry():
    original_registry = PipelineFactory._registry.copy()

    yield

    PipelineFactory._registry.clear()
    PipelineFactory._registry.update(original_registry)


def test_factory_creates_dhis2_pipeline():
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
        batch_name="Factory Test",
    )

    pipeline = PipelineFactory.create_dhis2(
        source_config=source_config,
        database_settings=database_settings,
        pipeline_config=pipeline_config,
    )

    assert isinstance(pipeline, DHIS2Pipeline)
    assert isinstance(pipeline.extractor, DHIS2Extractor)
    assert isinstance(pipeline.transformer, DHIS2Transformer)
    assert isinstance(pipeline.validator, DHIS2Validator)
    assert isinstance(pipeline.loader, PostgresLoader)

    assert pipeline.transformer.source_instance == "test_dhis2"
    assert pipeline.config == pipeline_config


def test_factory_registry_contains_dhis2():
    assert "dhis2" in PipelineFactory.registry()


def test_factory_rejects_unknown_pipeline_type():
    source_config = DHIS2SourceConfig(
        source_instance="test_dhis2",
        settings=DHIS2Settings(
            base_url="https://example.org",
            username="test_user",
            password="test_password",
        ),
    )

    with pytest.raises(ValueError, match="Unknown pipeline type"):
        PipelineFactory.create(
            pipeline_type="unknown",
            source_config=source_config,
            database_settings=None,
            pipeline_config=None,
        )


def test_factory_registry_returns_copy():
    registry = PipelineFactory.registry()

    registry.clear()

    assert "dhis2" in PipelineFactory.registry()


def test_factory_rejects_duplicate_registration():
    with pytest.raises(
        ValueError,
        match="Pipeline type already registered",
    ):
        PipelineFactory.register(
            "dhis2",
            PipelineFactory.create_dhis2,
        )


def test_dhis2_pipeline_declares_pipeline_type():
    assert DHIS2Pipeline.pipeline_type == "dhis2"


def test_factory_registers_custom_pipeline_creator():
    def custom_creator(
        *,
        source_config,
        database_settings,
        pipeline_config,
    ):
        return CustomPipeline(
            extractor=None,
            transformer=None,
            validator=None,
            loader=None,
        )

    PipelineFactory.register(
        "custom",
        custom_creator,
    )

    assert "custom" in PipelineFactory.registry()
    assert PipelineFactory.registry()["custom"] is custom_creator


def test_factory_creates_registered_custom_pipeline():
    def custom_creator(
        *,
        source_config,
        database_settings,
        pipeline_config,
    ):
        return CustomPipeline(
            extractor=None,
            transformer=None,
            validator=None,
            loader=None,
        )

    PipelineFactory.register(
        "custom",
        custom_creator,
    )

    result = PipelineFactory.create(
        pipeline_type="custom",
        source_config=None,
        database_settings=None,
        pipeline_config=None,
    )

    assert isinstance(result, CustomPipeline)
    assert isinstance(result, BasePipeline)


def test_factory_registry_contains_callable_creators():
    registry = PipelineFactory.registry()

    for pipeline_type, creator in registry.items():
        assert isinstance(pipeline_type, str)
        assert callable(creator)


def test_factory_registry_creators_return_base_pipeline():
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
        batch_name="Factory Test",
    )

    registry = PipelineFactory.registry()

    for creator in registry.values():
        pipeline = creator(
            source_config=source_config,
            database_settings=database_settings,
            pipeline_config=pipeline_config,
        )

        assert isinstance(pipeline, BasePipeline)


def test_dhis2_factory_rejects_incompatible_source_config():
    class OtherSourceConfig:
        source_instance = "other_source"

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

    with pytest.raises(
        TypeError,
        match="DHIS2 pipeline requires DHIS2SourceConfig",
    ):
        PipelineFactory.create_dhis2(
            source_config=OtherSourceConfig(),
            database_settings=database_settings,
            pipeline_config=pipeline_config,
        )
