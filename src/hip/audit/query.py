"""Read-side queries for HIP ETL audit information."""

import psycopg

from hip.audit.models import BatchSummary
from hip.config.database import DatabaseSettings


class AuditQueryService:
    """Query ETL batch audit information."""

    def __init__(self, settings: DatabaseSettings) -> None:
        self.settings = settings

    def _connection(self):
        """Create a PostgreSQL database connection."""

        return psycopg.connect(
            host=self.settings.host,
            port=self.settings.port,
            dbname=self.settings.database,
            user=self.settings.username,
            password=self.settings.password,
        )

    def get_batch_summary(
        self,
        batch_id: str,
    ) -> BatchSummary | None:
        """Return the operational summary for one ETL batch."""

        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    batch_id,
                    source_system,
                    batch_name,
                    environment,
                    status,
                    total_rows,
                    COALESCE(successful_rows, 0),
                    COALESCE(failed_rows, 0),
                    duplicate_rows
                FROM audit.etl_batch
                WHERE batch_id = %s
                """,
                (batch_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return BatchSummary(
            batch_id=str(row[0]),
            source_system=row[1],
            batch_name=row[2],
            environment=row[3],
            status=row[4],
            total_rows=row[5],
            successful_rows=row[6],
            failed_rows=row[7],
            duplicate_rows=row[8],
        )
