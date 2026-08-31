import pytest

from hip.config.settings import DHIS2Settings
from hip.config.source import DHIS2SourceConfig


def test_dhis2_source_config_stores_source_identity():
    settings = DHIS2Settings(
        base_url="https://example.org",
        username="test_user",
        password="test_password",
    )

    config = DHIS2SourceConfig(
        source_instance="kenya_dhis2",
        settings=settings,
    )

    assert config.source_instance == "kenya_dhis2"
    assert config.settings == settings


def test_dhis2_source_config_rejects_empty_source_instance():
    settings = DHIS2Settings(
        base_url="https://example.org",
        username="test_user",
        password="test_password",
    )

    with pytest.raises(ValueError, match="source_instance"):
        DHIS2SourceConfig(
            source_instance="",
            settings=settings,
        )


def test_dhis2_source_config_is_immutable():
    settings = DHIS2Settings(
        base_url="https://example.org",
        username="test_user",
        password="test_password",
    )

    config = DHIS2SourceConfig(
        source_instance="kenya_dhis2",
        settings=settings,
    )

    with pytest.raises(AttributeError):
        config.source_instance = "other_dhis2"
