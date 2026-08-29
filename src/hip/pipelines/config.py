"""
Configuration for HIP pipeline execution.

Pipeline configuration defines how a pipeline should be executed,
while PipelineContext identifies a specific execution.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    """Configuration governing a pipeline execution."""

    environment: str
    initiated_by: str
    batch_name: str
