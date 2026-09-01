"""
Application-level pipeline execution.

PipelineRunner coordinates pipeline creation and execution
without containing source-specific ETL logic.
"""

from typing import Any

from hip.pipelines.factory import PipelineFactory


class PipelineRunner:
    """Create and execute configured HIP pipelines."""

    @staticmethod
    def run(
        pipeline_type: str,
        **kwargs: Any,
    ) -> int:
        """
        Create and execute a pipeline.

        Parameters
        ----------
        pipeline_type:
            Registered pipeline type to execute.

        **kwargs:
            Configuration and runtime arguments required by
            the registered pipeline creator and pipeline itself.

        Returns
        -------
        int
            Number of successfully loaded records.
        """

        pipeline = PipelineFactory.create(
            pipeline_type=pipeline_type,
            source_config=kwargs["source_config"],
            database_settings=kwargs["database_settings"],
            pipeline_config=kwargs["pipeline_config"],
        )

        return pipeline.run()
