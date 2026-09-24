"""Tests for DHIS2 period semantics."""

from datetime import date

import pytest

from hip.periods.dhis2 import DHIS2Period, DHIS2PeriodInterpreter


@pytest.mark.parametrize(
    ("period_type", "period", "expected_start", "expected_end"),
    [
        (
            "Daily",
            "20260415",
            date(2026, 4, 15),
            date(2026, 4, 15),
        ),
        (
            "Weekly",
            "2026W1",
            date(2025, 12, 29),
            date(2026, 1, 4),
        ),
        (
            "Weekly",
            "2026W16",
            date(2026, 4, 13),
            date(2026, 4, 19),
        ),
        (
            "SixMonthlyApril",
            "2026AprilS1",
            date(2026, 4, 1),
            date(2026, 9, 30),
        ),
        (
            "SixMonthlyApril",
            "2026AprilS2",
            date(2026, 10, 1),
            date(2027, 3, 31),
        ),
        (
            "FinancialApril",
            "2026April",
            date(2026, 4, 1),
            date(2027, 3, 31),
        ),
        (
            "FinancialJuly",
            "2026July",
            date(2026, 7, 1),
            date(2027, 6, 30),
        ),
        (
            "FinancialOctober",
            "2026Oct",
            date(2026, 10, 1),
            date(2027, 9, 30),
        ),
        (
            "Monthly",
            "202604",
            date(2026, 4, 1),
            date(2026, 4, 30),
        ),
        (
            "BiMonthly",
            "202601B",
            date(2026, 1, 1),
            date(2026, 2, 28),
        ),
        (
            "BiMonthly",
            "202611B",
            date(2026, 11, 1),
            date(2026, 12, 31),
        ),
        (
            "Quarterly",
            "2026Q2",
            date(2026, 4, 1),
            date(2026, 6, 30),
        ),
        (
            "SixMonthly",
            "2026S1",
            date(2026, 1, 1),
            date(2026, 6, 30),
        ),
        (
            "SixMonthly",
            "2026S2",
            date(2026, 7, 1),
            date(2026, 12, 31),
        ),
        (
            "Yearly",
            "2026",
            date(2026, 1, 1),
            date(2026, 12, 31),
        ),
    ],
)
def test_interprets_supported_dhis2_periods(
    period_type,
    period,
    expected_start,
    expected_end,
):
    result = DHIS2PeriodInterpreter.interpret(
        period_type=period_type,
        period=period,
    )

    assert result == DHIS2Period(
        start_date=expected_start,
        end_date=expected_end,
    )


def test_returns_none_for_unsupported_period_type():
    result = DHIS2PeriodInterpreter.interpret(
        period_type="UnsupportedType",
        period="202601",
    )

    assert result is None


@pytest.mark.parametrize(
    ("period_type", "period"),
    [
        ("Daily", "20260230"),
        ("Daily", "20261301"),
        ("BiMonthly", "202613B"),
        ("SixMonthlyApril", "2026AprilS3"),
        ("FinancialApril", "2026March"),
        ("FinancialJuly", "2026June"),
        ("FinancialOctober", "2026October"),
        ("Monthly", "202613"),
        ("Monthly", "2026"),
        ("Quarterly", "2026Q5"),
        ("SixMonthly", "2026S3"),
        ("Yearly", "26"),
    ],
)
def test_returns_none_for_invalid_period_code(period_type, period):
    result = DHIS2PeriodInterpreter.interpret(
        period_type=period_type,
        period=period,
    )

    assert result is None
