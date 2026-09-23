"""Repository for source-scoped DHIS2 dataset metadata."""

from typing import Any

from hip.config.database import DatabaseSettings


class DHIS2DatasetRepository:
    """Persist and retrieve DHIS2 dataset metadata."""

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
        dataset_id: str,
    ) -> dict[str, Any] | None:
        """Return cached metadata for one DHIS2 dataset."""

        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    dataset_id,
                    dataset_name,
                    period_type
                FROM silver.dhis2_dataset
                WHERE source_instance = %s
                  AND dataset_id = %s
                """,
                (
                    source_instance,
                    dataset_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "dataset_id": row[0],
            "dataset_name": row[1],
            "period_type": row[2],
        }

    def upsert(
        self,
        *,
        source_instance: str,
        dataset_id: str,
        dataset_name: str,
        period_type: str,
    ) -> None:
        """Persist or refresh metadata for one DHIS2 dataset."""

        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO silver.dhis2_dataset (
                    source_instance,
                    dataset_id,
                    dataset_name,
                    period_type
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (
                    source_instance,
                    dataset_id
                )
                DO UPDATE SET
                    dataset_name = EXCLUDED.dataset_name,
                    period_type = EXCLUDED.period_type,
                    resolved_at = NOW()
                """,
                (
                    source_instance,
                    dataset_id,
                    dataset_name,
                    period_type,
                ),
            )
