"""
Configuration for HIP data sources.

Source configuration identifies a specific external data source
and contains the connection settings required to access it.
"""

from dataclasses import dataclass

from hip.config.settings import DHIS2Settings


@dataclass(frozen=True)
class DHIS2SourceConfig:
    """Configuration identifying a DHIS2 source instance."""

    source_instance: str
    settings: DHIS2Settings

    def __post_init__(self) -> None:
        """Validate DHIS2 source configuration."""

        if not self.source_instance.strip():
            raise ValueError("source_instance is required")
