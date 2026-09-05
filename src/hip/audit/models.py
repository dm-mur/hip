"""Read models for HIP audit information."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BatchSummary:
    """Operational summary of an ETL batch."""

    batch_id: str
    source_system: str
    batch_name: str | None
    environment: str
    status: str
    total_rows: int
    successful_rows: int
    failed_rows: int
    duplicate_rows: int

    @property
    def inserted_rows(self) -> int:
        """Return the number of newly inserted records."""

        return self.successful_rows - self.duplicate_rows
