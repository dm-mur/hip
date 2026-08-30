"""
Factory for constructing HIP pipelines.

The factory centralizes dependency wiring so application code
does not need to manually construct every pipeline component.
"""

from hip.audit.service import AuditService
from hip.config.database import DatabaseSettings
from hip.config.settings import DHIS2Settings
from hip.extractors.dhis2 import DHIS2Extractor
from hip.loaders.postgres import PostgresLoader
from hip.pipelines.config import PipelineConfig
from hip.pipelines.dhis2 import DHIS2Pipeline
from hip.transformers.dhis2 import DHIS2Transformer
from hip.validators.dhis2 import DHIS2Validator


class PipelineFactory:
    """Construct fully configured HIP pipelines."""

    @staticmethod
    def registry() -> dict[str, object]:
        """Return the registered pipeline types."""

        return {
            "dhis2": PipelineFactory.create_dhis2,
        }

    @staticmethod
    def create(
        pipeline_type: str,
        dhis2_settings: DHIS2Settings,
        database_settings: DatabaseSettings,
        pipeline_config: PipelineConfig,
        source_instance: str,
    ) -> DHIS2Pipeline:
        """Create a pipeline from the registered pipeline types."""

        creators = PipelineFactory.registry()

        if pipeline_type not in creators:
            raise ValueError(
                f"Unknown pipeline type: {pipeline_type}"
            )

        return creators[pipeline_type](
            dhis2_settings=dhis2_settings,
            database_settings=database_settings,
            pipeline_config=pipeline_config,
            source_instance=source_instance,
        )

    @staticmethod
    def create_dhis2(
        dhis2_settings: DHIS2Settings,
        database_settings: DatabaseSettings,
        pipeline_config: PipelineConfig,
        source_instance: str,
    ) -> DHIS2Pipeline:
        """
        Create a fully configured DHIS2 pipeline.

        Parameters
        ----------
        dhis2_settings:
            Configuration for the DHIS2 source instance.

        database_settings:
            Configuration for the PostgreSQL destination.

        pipeline_config:
            Execution configuration for the pipeline.

        source_instance:
            Logical identifier for the DHIS2 source instance.

        Returns
        -------
        DHIS2Pipeline
            Fully wired DHIS2 pipeline.
        """

        extractor = DHIS2Extractor(
            settings=dhis2_settings,
        )

        transformer = DHIS2Transformer(
            source_instance=source_instance,
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
