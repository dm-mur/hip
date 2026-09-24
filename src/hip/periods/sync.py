"""Synchronization of interpreted DHIS2 period metadata."""

from hip.periods.dhis2 import DHIS2Period, DHIS2PeriodInterpreter
from hip.repositories.period import DHIS2PeriodRepository


class DHIS2PeriodSync:
    """Interpret and persist DHIS2 period metadata."""

    def __init__(
        self,
        *,
        repository: DHIS2PeriodRepository,
    ) -> None:
        self.repository = repository

    def sync(
        self,
        *,
        source_instance: str,
        period_type: str,
        period: str,
    ) -> DHIS2Period | None:
        interpreted = DHIS2PeriodInterpreter.interpret(
            period_type=period_type,
            period=period,
        )

        if interpreted is None:
            return None

        self.repository.upsert(
            source_instance=source_instance,
            period_type=period_type,
            period=period,
            period_start_date=interpreted.start_date,
            period_end_date=interpreted.end_date,
        )

        return interpreted
