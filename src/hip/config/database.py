"""
PostgreSQL database configuration for HIP.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseSettings:
    """Configuration required to connect to PostgreSQL."""

    host: str
    port: int
    database: str
    username: str
    password: str

    @classmethod
    def from_environment(cls) -> "DatabaseSettings":
        """Load database configuration from environment variables."""

        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5435")
        database = os.getenv("POSTGRES_DB", "hip")
        username = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD")

        if not password:
            raise ValueError(
                "Missing required PostgreSQL configuration: POSTGRES_PASSWORD"
            )

        try:
            port_number = int(port)
        except ValueError as exc:
            raise ValueError(
                f"Invalid POSTGRES_PORT: {port}. Expected an integer."
            ) from exc

        return cls(
            host=host,
            port=port_number,
            database=database,
            username=username,
            password=password,
        )