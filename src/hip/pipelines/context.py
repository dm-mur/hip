"""
Execution context for HIP pipelines.

Carries metadata associated with one pipeline execution.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineContext:
    """Metadata describing one pipeline execution."""

    batch_id: str
    environment: str
    initiated_by: str
