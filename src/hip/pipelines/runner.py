"""
Application-level pipeline execution.

PipelineRunner coordinates pipeline creation and execution
without containing source-specific ETL logic.
"""

from hip.config.database import DatabaseSettings
from hip.config.source import DHIS2SourceConfig
from hip.pipelines.config import PipelineConfig
from hip.pipelines.factory import PipelineFactory
from hip.pipelines.request import PipelineRequest


class PipelineRunner:
    """Create and execute configured HIP pipelines."""

    @staticmethod
    def run(
        pipeline_type: str,
        source_config: DHIS2SourceConfig,
        database_settings: DatabaseSettings,
        pipeline_config: PipelineConfig,
        request: PipelineRequest,
    ) -> int:
        """
        Create and execute a pipeline.

        Parameters
        ----------
        pipeline_type:
            Registered pipeline type to execute.

        source_config:
            Configuration for the source system.

        database_settings:
            Configuration for the destination database.

        pipeline_config:
            Configuration governing the pipeline execution.

        request:
            Runtime request describing what the pipeline should execute.

        Returns
        -------
        int
            Number of successfully loaded records.
        """

        pipeline = PipelineFactory.create(
            pipeline_type=pipeline_type,
            source_config=source_config,
            database_settings=database_settings,
            pipeline_config=pipeline_config,
        )

        return pipeline.run(request=request)
