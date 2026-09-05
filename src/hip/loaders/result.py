from dataclasses import dataclass


@dataclass(frozen=True)
class LoadResult:
    """Outcome of a loader operation."""

    inserted_rows: int
    duplicate_rows: int
