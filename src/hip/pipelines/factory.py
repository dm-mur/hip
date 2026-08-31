"""
Factory for constructing HIP pipelines.

The factory centralizes dependency wiring so application code
does not need to manually construct every pipeline component.
"""

from hip.audit.service import AuditService
from hip.config.database import DatabaseSettings
from hip.config.source import DHIS2SourceConfig
from hip.extractors.dhis2 import DHIS2Extractor
from hip.loaders.postgres import PostgresLoader
from hip.pipelines.config import PipelineConfig
from hip.pipelines.dhis2 import DHIS2Pipeline
from hip.transformers.dhis2 import DHIS2Transformer
from hip.validators.dhis2 import DHIS2Validator


class PipelineFactory:
    """Construct fully configured HIP pipelines."""

    _registry: dict[str, object] = {}

    @classmethod
    def register(
        cls,
        pipeline_type: str,
        creator: object,
    ) -> None:
        """Register a pipeline creator."""

        if pipeline_type in cls._registry:
            raise ValueError(
                f"Pipeline type already registered: {pipeline_type}"
            )

        cls._registry[pipeline_type] = creator

    @classmethod
    def registry(cls) -> dict[str, object]:
        """Return a copy of the registered pipeline types."""

        return cls._registry.copy()

    @classmethod
    def create(
        cls,
        pipeline_type: str,
        source_config: DHIS2SourceConfig,
        database_settings: DatabaseSettings,
        pipeline_config: PipelineConfig,
    ) -> DHIS2Pipeline:
        """Create a pipeline from the registered pipeline types."""

        if pipeline_type not in cls._registry:
            raise ValueError(
                f"Unknown pipeline type: {pipeline_type}"
            )

        creator = cls._registry[pipeline_type]

        return creator(
            source_config=source_config,
            database_settings=database_settings,
            pipeline_config=pipeline_config,
        )

    @staticmethod
    def create_dhis2(
        source_config: DHIS2SourceConfig,
        database_settings: DatabaseSettings,
        pipeline_config: PipelineConfig,
    ) -> DHIS2Pipeline:
        """
        Create a fully configured DHIS2 pipeline.

        Parameters
        ----------
        source_config:
            Configuration identifying the DHIS2 source instance.

        database_settings:
            Configuration for the PostgreSQL destination.

        pipeline_config:
            Execution configuration for the pipeline.

        Returns
        -------
        DHIS2Pipeline
            Fully wired DHIS2 pipeline.
        """

        extractor = DHIS2Extractor(
            settings=source_config.settings,
        )

        transformer = DHIS2Transformer(
            source_instance=source_config.source_instance,
        )
        validator = DHIS2Validator()

        loader = PostgresLoader(
            settings=database_settings,
        )

        audit = AuditService(
            settings=database_settings,
        )

        return DHIS2Pipeline(
            extractor=extractor,
            transformer=transformer,
            validator=validator,
            loader=loader,
            audit=audit,
            config=pipeline_config,
        )


PipelineFactory.register(
    DHIS2Pipeline.pipeline_type,
    PipelineFactory.create_dhis2,
)