"""
HIP application configuration.

Configuration is loaded from environment variables so that
credentials and deployment-specific settings are never
hard-coded in source code.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DHIS2Settings:
    """Configuration required to connect to a DHIS2 instance."""

    base_url: str
    username: str
    password: str

    @classmethod
    def from_environment(cls) -> "DHIS2Settings":
        """Create DHIS2 settings from environment variables."""

        base_url = os.getenv("DHIS2_BASE_URL")
        username = os.getenv("DHIS2_USERNAME")
        password = os.getenv("DHIS2_PASSWORD")

        missing = []

        if not base_url:
            missing.append("DHIS2_BASE_URL")

        if not username:
            missing.append("DHIS2_USERNAME")

        if not password:
            missing.append("DHIS2_PASSWORD")

        if missing:
            raise ValueError(
                f"Missing required DHIS2 configuration: {', '.join(missing)}"
            )

        return cls(
            base_url=base_url,
            username=username,
            password=password,
        )
