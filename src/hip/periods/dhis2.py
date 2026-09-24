"""Interpret authoritative DHIS2 period codes."""

import calendar
import re
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class DHIS2Period:
    """Calendar boundaries represented by a DHIS2 period."""

    start_date: date
    end_date: date


class DHIS2PeriodInterpreter:
    """Interpret DHIS2 period codes using their authoritative period type."""

    @classmethod
    def interpret(
        cls,
        *,
        period_type: str,
        period: str,
    ) -> DHIS2Period | None:
        """Return calendar boundaries for a supported DHIS2 period."""

        if period_type == "Monthly":
            return cls._monthly(period)

        if period_type == "Quarterly":
            return cls._quarterly(period)

        if period_type == "SixMonthly":
            return cls._six_monthly(period)

        if period_type == "Yearly":
            return cls._yearly(period)

        if period_type == "Daily":
            return cls._daily(period)

        if period_type == "SixMonthlyApril":
            return cls._six_monthly_april(period)

        if period_type == "FinancialApril":
            return cls._financial_year(period, "April", 4)

        if period_type == "FinancialJuly":
            return cls._financial_year(period, "July", 7)

        if period_type == "FinancialOctober":
            return cls._financial_year(period, "Oct", 10)

        if period_type == "Weekly":
            return cls._weekly(period)

        if period_type == "BiMonthly":
            return cls._bi_monthly(period)

        return None

    @staticmethod
    def _monthly(period: str) -> DHIS2Period | None:
        match = re.fullmatch(r"(\d{4})(\d{2})", period)
        if match is None:
            return None

        year = int(match.group(1))
        month = int(match.group(2))

        if not 1 <= month <= 12:
            return None

        last_day = calendar.monthrange(year, month)[1]

        return DHIS2Period(
            start_date=date(year, month, 1),
            end_date=date(year, month, last_day),
        )

    @staticmethod
    def _bi_monthly(period: str) -> DHIS2Period | None:
        match = re.fullmatch(r"(\d{4})(\d{2})B", period)
        if match is None:
            return None

        year = int(match.group(1))
        start_month = int(match.group(2))

        if not 1 <= start_month <= 11:
            return None

        end_month = start_month + 1
        last_day = calendar.monthrange(year, end_month)[1]

        return DHIS2Period(
            start_date=date(year, start_month, 1),
            end_date=date(year, end_month, last_day),
        )

    @staticmethod
    def _quarterly(period: str) -> DHIS2Period | None:
        match = re.fullmatch(r"(\d{4})Q([1-4])", period)
        if match is None:
            return None

        year = int(match.group(1))
        quarter = int(match.group(2))

        start_month = ((quarter - 1) * 3) + 1
        end_month = start_month + 2
        last_day = calendar.monthrange(year, end_month)[1]

        return DHIS2Period(
            start_date=date(year, start_month, 1),
            end_date=date(year, end_month, last_day),
        )

    @staticmethod
    def _six_monthly(period: str) -> DHIS2Period | None:
        match = re.fullmatch(r"(\d{4})S([1-2])", period)
        if match is None:
            return None

        year = int(match.group(1))
        half = int(match.group(2))

        if half == 1:
            return DHIS2Period(
                start_date=date(year, 1, 1),
                end_date=date(year, 6, 30),
            )

        return DHIS2Period(
            start_date=date(year, 7, 1),
            end_date=date(year, 12, 31),
        )

    @staticmethod
    def _yearly(period: str) -> DHIS2Period | None:
        match = re.fullmatch(r"(\d{4})", period)
        if match is None:
            return None

        year = int(match.group(1))

        return DHIS2Period(
            start_date=date(year, 1, 1),
            end_date=date(year, 12, 31),
        )

    @staticmethod
    def _daily(period: str) -> DHIS2Period | None:
        match = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", period)
        if match is None:
            return None

        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        try:
            period_date = date(year, month, day)
        except ValueError:
            return None

        return DHIS2Period(
            start_date=period_date,
            end_date=period_date,
        )

    @staticmethod
    def _weekly(period: str) -> DHIS2Period | None:
        match = re.fullmatch(r"(\d{4})W(\d{1,2})", period)
        if match is None:
            return None

        year = int(match.group(1))
        week = int(match.group(2))

        try:
            start_date = date.fromisocalendar(year, week, 1)
        except ValueError:
            return None

        return DHIS2Period(
            start_date=start_date,
            end_date=start_date + timedelta(days=6),
        )

    @staticmethod
    def _six_monthly_april(period: str) -> DHIS2Period | None:
        match = re.fullmatch(r"(\d{4})AprilS([1-2])", period)
        if match is None:
            return None

        year = int(match.group(1))
        half = int(match.group(2))

        if half == 1:
            return DHIS2Period(
                start_date=date(year, 4, 1),
                end_date=date(year, 9, 30),
            )

        return DHIS2Period(
            start_date=date(year, 10, 1),
            end_date=date(year + 1, 3, 31),
        )

    @staticmethod
    def _financial_year(
        period: str,
        code: str,
        start_month: int,
    ) -> DHIS2Period | None:
        match = re.fullmatch(rf"(\d{{4}}){code}", period)
        if match is None:
            return None

        year = int(match.group(1))

        start_date = date(year, start_month, 1)

        end_month = start_month - 1
        end_year = year + 1
        last_day = calendar.monthrange(end_year, end_month)[1]

        return DHIS2Period(
            start_date=start_date,
            end_date=date(end_year, end_month, last_day),
        )
