import pytest

from hip.config.settings import DHIS2Settings


def test_dhis2_settings_requires_configuration(monkeypatch):
    monkeypatch.delenv("DHIS2_BASE_URL", raising=False)
    monkeypatch.delenv("DHIS2_USERNAME", raising=False)
    monkeypatch.delenv("DHIS2_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="DHIS2_BASE_URL"):
        DHIS2Settings.from_environment()


def test_dhis2_settings_loads_from_environment(monkeypatch):
    monkeypatch.setenv("DHIS2_BASE_URL", "https://example.org")
    monkeypatch.setenv("DHIS2_USERNAME", "test_user")
    monkeypatch.setenv("DHIS2_PASSWORD", "test_password")

    settings = DHIS2Settings.from_environment()

    assert settings.base_url == "https://example.org"
    assert settings.username == "test_user"
    assert settings.password == "test_password"
