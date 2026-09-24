"""Repository for source-scoped DHIS2 period metadata."""

from datetime import date
from typing import Any

from hip.config.database import DatabaseSettings


class DHIS2PeriodRepository:
    """Persist and retrieve interpreted DHIS2 period metadata."""

    def __init__(self, settings: DatabaseSettings) -> None:
        self.settings = settings

    def _connection(self):
        import psycopg

        return psycopg.connect(
            host=self.settings.host,
            port=self.settings.port,
            dbname=self.settings.database,
            user=self.settings.username,
            password=self.settings.password,
        )

    def get(
        self,
        *,
        source_instance: str,
        period_type: str,
        period: str,
    ) -> dict[str, Any] | None:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    period_type,
                    period,
                    period_start_date,
                    period_end_date
                FROM silver.dhis2_period
                WHERE source_instance = %s
                  AND period_type = %s
                  AND period = %s
                """,
                (
                    source_instance,
                    period_type,
                    period,
                ),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "period_type": row[0],
            "period": row[1],
            "period_start_date": row[2],
            "period_end_date": row[3],
        }

    def upsert(
        self,
        *,
        source_instance: str,
        period_type: str,
        period: str,
        period_start_date: date,
        period_end_date: date,
    ) -> None:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO silver.dhis2_period (
                    source_instance,
                    period_type,
                    period,
                    period_start_date,
                    period_end_date
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (
                    source_instance,
                    period_type,
                    period
                )
                DO UPDATE SET
                    period_start_date = EXCLUDED.period_start_date,
                    period_end_date = EXCLUDED.period_end_date,
                    resolved_at = NOW()
                """,
                (
                    source_instance,
                    period_type,
                    period,
                    period_start_date,
                    period_end_date,
                ),
            )
