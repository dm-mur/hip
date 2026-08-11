from hip.config.database import DatabaseSettings


def test_database_settings_defaults():
    settings = DatabaseSettings.from_environment()

    assert settings.host == "localhost"
    assert settings.port == 5435
    assert settings.database == "hip"
    assert settings.username == "postgres"
