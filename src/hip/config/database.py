"""
PostgreSQL database configuration for HIP.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv("docker/.env")


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

        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5435")),
            database=os.getenv("POSTGRES_DB", "hip"),
            username=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
        )
