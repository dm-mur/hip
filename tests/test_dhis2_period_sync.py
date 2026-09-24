"""Tests for DHIS2 period metadata synchronization."""

from datetime import date
from unittest.mock import Mock

from hip.periods.dhis2 import DHIS2Period, DHIS2PeriodInterpreter
from hip.periods.sync import DHIS2PeriodSync


def test_sync_interprets_and_persists_supported_period():
    repository = Mock()
    sync = DHIS2PeriodSync(repository=repository)

    result = sync.sync(
        source_instance="live_test",
        period_type="Monthly",
        period="202604",
    )

    assert result == DHIS2Period(
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 30),
    )

    repository.upsert.assert_called_once_with(
        source_instance="live_test",
        period_type="Monthly",
        period="202604",
        period_start_date=date(2026, 4, 1),
        period_end_date=date(2026, 4, 30),
    )


def test_sync_does_not_persist_unsupported_period():
    repository = Mock()
    sync = DHIS2PeriodSync(repository=repository)

    result = sync.sync(
        source_instance="live_test",
        period_type="UnsupportedType",
        period="202604",
    )

    assert result is None
    repository.upsert.assert_not_called()


def test_sync_uses_period_interpreter(monkeypatch):
    repository = Mock()

    interpreted = DHIS2Period(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 31),
    )

    interpret = Mock(return_value=interpreted)

    monkeypatch.setattr(
        DHIS2PeriodInterpreter,
        "interpret",
        interpret,
    )

    sync = DHIS2PeriodSync(repository=repository)

    result = sync.sync(
        source_instance="period_source",
        period_type="Quarterly",
        period="2026Q1",
    )

    interpret.assert_called_once_with(
        period_type="Quarterly",
        period="2026Q1",
    )

    assert result == interpreted
