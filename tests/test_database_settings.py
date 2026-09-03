from hip.config.database import DatabaseSettings


def test_database_settings_defaults(monkeypatch):
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    monkeypatch.delenv("POSTGRES_PORT", raising=False)
    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.setenv("POSTGRES_PASSWORD", "test-password")

    settings = DatabaseSettings.from_environment()

    assert settings.host == "localhost"
    assert settings.port == 5435
    assert settings.database == "hip"
    assert settings.username == "postgres"
    assert settings.password == "test-password"


def test_database_settings_requires_password(monkeypatch):
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)

    try:
        DatabaseSettings.from_environment()
    except ValueError as exc:
        assert str(exc) == (
            "Missing required PostgreSQL configuration: POSTGRES_PASSWORD"
        )
    else:
        raise AssertionError("Expected ValueError")


def test_database_settings_rejects_invalid_port(monkeypatch):
    monkeypatch.setenv("POSTGRES_PASSWORD", "test-password")
    monkeypatch.setenv("POSTGRES_PORT", "not-a-number")

    try:
        DatabaseSettings.from_environment()
    except ValueError as exc:
        assert str(exc) == (
            "Invalid POSTGRES_PORT: not-a-number. Expected an integer."
        )
    else:
        raise AssertionError("Expected ValueError")