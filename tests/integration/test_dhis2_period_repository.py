"""Integration tests for the DHIS2 period repository."""

from datetime import date

from hip.config.database import DatabaseSettings
from hip.repositories.period import DHIS2PeriodRepository


def test_upsert_and_get_period_metadata():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2PeriodRepository(settings)

    repository.upsert(
        source_instance="period_repo_test",
        period_type="Monthly",
        period="202604",
        period_start_date=date(2026, 4, 1),
        period_end_date=date(2026, 4, 30),
    )

    result = repository.get(
        source_instance="period_repo_test",
        period_type="Monthly",
        period="202604",
    )

    assert result == {
        "period_type": "Monthly",
        "period": "202604",
        "period_start_date": date(2026, 4, 1),
        "period_end_date": date(2026, 4, 30),
    }


def test_upsert_refreshes_existing_period_metadata():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2PeriodRepository(settings)

    repository.upsert(
        source_instance="period_repo_refresh",
        period_type="Monthly",
        period="202604",
        period_start_date=date(2026, 4, 1),
        period_end_date=date(2026, 4, 29),
    )

    repository.upsert(
        source_instance="period_repo_refresh",
        period_type="Monthly",
        period="202604",
        period_start_date=date(2026, 4, 1),
        period_end_date=date(2026, 4, 30),
    )

    result = repository.get(
        source_instance="period_repo_refresh",
        period_type="Monthly",
        period="202604",
    )

    assert result["period_end_date"] == date(2026, 4, 30)


def test_get_returns_none_for_missing_period():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2PeriodRepository(settings)

    result = repository.get(
        source_instance="missing_period_source",
        period_type="Monthly",
        period="209912",
    )

    assert result is None
