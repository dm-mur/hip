"""
Audit service for HIP ETL batch lifecycle management.
"""

from uuid import uuid4

import psycopg

from hip.config.database import DatabaseSettings


class AuditService:
    """Manage ETL batch audit records."""

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

    def start_batch(
        self,
        source_system: str,
        batch_name: str,
        environment: str,
        initiated_by: str,
    ) -> str:
        """Create and start a new ETL batch."""

        batch_id = str(uuid4())

        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO audit.etl_batch (
                        batch_id,
                        source_system,
                        started_at,
                        status,
                        total_rows,
                        batch_name,
                        environment,
                        initiated_by
                    )
                    VALUES (
                        %s,
                        %s,
                        CURRENT_TIMESTAMP,
                        'RUNNING',
                        0,
                        %s,
                        %s,
                        %s
                    )
                    """,
                (
                    batch_id,
                    source_system,
                    batch_name,
                    environment,
                    initiated_by,
                ),
            )

        return batch_id

    def complete_batch(
        self,
        batch_id: str,
        total_rows: int,
        successful_rows: int,
        failed_rows: int,
        duplicate_rows: int,
    ) -> None:
        """Mark an ETL batch as successfully completed."""

        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    UPDATE audit.etl_batch
                    SET
                        status = 'SUCCESS',
                        total_rows = %s,
                        successful_rows = %s,
                        failed_rows = %s,
                        duplicate_rows = %s,
                        completed_at = CURRENT_TIMESTAMP,
                        duration_seconds = EXTRACT(
                            EPOCH FROM (
                                CURRENT_TIMESTAMP - started_at
                            )
                        )::INTEGER
                    WHERE batch_id = %s
                    """,
                (
                    total_rows,
                    successful_rows,
                    failed_rows,
                    duplicate_rows,
                    batch_id,
                ),
            )

    def fail_batch(
        self,
        batch_id: str,
        total_rows: int,
        successful_rows: int,
        failed_rows: int,
        duplicate_rows: int,
        remarks: str,
    ) -> None:
        """Mark an ETL batch as failed."""

        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    UPDATE audit.etl_batch
                    SET
                        status = 'FAILED',
                        total_rows = %s,
                        successful_rows = %s,
                        failed_rows = %s,
                        duplicate_rows = %s,
                        remarks = %s,
                        completed_at = CURRENT_TIMESTAMP,
                        duration_seconds = EXTRACT(
                            EPOCH FROM (
                                CURRENT_TIMESTAMP - started_at
                            )
                        )::INTEGER
                    WHERE batch_id = %s
                    """,
                (
                    total_rows,
                    successful_rows,
                    failed_rows,
                    duplicate_rows,
                    remarks,
                    batch_id,
                ),
            )
