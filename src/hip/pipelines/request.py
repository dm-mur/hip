"""
Request describing one pipeline execution.

PipelineRequest contains runtime arguments required to execute
a pipeline, while PipelineConfig contains execution configuration
and PipelineContext identifies the actual execution.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PipelineRequest:
    """Runtime request for executing a pipeline."""

    endpoint: str
    params: dict[str, Any] | None = None
