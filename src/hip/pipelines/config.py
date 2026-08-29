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

    VALID_ENVIRONMENTS = {
        "DEV",
        "TEST",
        "UAT",
        "PROD",
    }

    def __post_init__(self) -> None:
        """Validate pipeline execution configuration."""

        if self.environment not in self.VALID_ENVIRONMENTS:
            raise ValueError(
                f"Invalid environment: {self.environment}. "
                f"Expected one of: {', '.join(sorted(self.VALID_ENVIRONMENTS))}"
            )

        if not self.initiated_by.strip():
            raise ValueError("initiated_by is required")

        if not self.batch_name.strip():
            raise ValueError("batch_name is required")