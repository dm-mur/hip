"""
Shared pytest configuration for HIP tests.
"""

from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ENV_FILE = PROJECT_ROOT / "docker" / ".env"


def pytest_sessionstart(session) -> None:
    """Load test environment variables before the test suite starts."""

    load_dotenv(TEST_ENV_FILE)
