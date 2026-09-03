"""
PostgreSQL loader for HIP Bronze data.
"""

import psycopg
from psycopg.types.json import Jsonb

from hip.config.database import DatabaseSettings
from hip.loaders.base import BaseLoader
from hip.models.dhis2 import DHIS2Record


class PostgresLoader(BaseLoader):
    """Load validated DHIS2 records into PostgreSQL Bronze."""

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

    def load(self, records: list[DHIS2Record]) -> int:
        """
        Load records into bronze.dhis2_data.

        Existing records with the same record_hash are skipped.

        Returns
        -------
        int
            Number of newly inserted records.
        """

        if not records:
            return 0

        inserted = 0

        with self._connection() as connection, connection.cursor() as cursor:

            for record in records:
                cursor.execute(
                    """
                        SELECT 1
                        FROM bronze.dhis2_data
                        WHERE source_instance = %s
                        AND record_hash = %s
                        LIMIT 1
                        """,
                    (
                        record.source_instance,
                        record.record_hash,
                    ),
                )

                if cursor.fetchone() is not None:
                    continue

                cursor.execute(
                    """
                        INSERT INTO bronze.dhis2_data (
                            batch_id,
                            source_system,
                            source_instance,
                            dataset_id,
                            data_element,
                            data_element_name,
                            org_unit,
                            org_unit_name,
                            period,
                            category_option_combo,
                            category_option_combo_name,
                            attribute_option_combo,
                            attribute_option_combo_name,
                            value,
                            comment,
                            followup,
                            stored_by,
                            created_at_source,
                            last_updated_at_source,
                            raw_payload,
                            record_hash
                        )
                        VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s
                        )
                        """,
                    (
                        record.batch_id,
                        "DHIS2",
                        record.source_instance,
                        record.dataset_id,
                        record.data_element,
                        record.data_element_name,
                        record.org_unit,
                        record.org_unit_name,
                        record.period,
                        record.category_option_combo,
                        record.category_option_combo_name,
                        record.attribute_option_combo,
                        record.attribute_option_combo_name,
                        record.value,
                        record.comment,
                        record.followup,
                        record.stored_by,
                        record.created_at_source,
                        record.last_updated_at_source,
                        Jsonb(record.raw_payload),
                        record.record_hash,
                    ),
                )

                inserted += 1

        return inserted
