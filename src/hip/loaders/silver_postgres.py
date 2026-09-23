import psycopg

from hip.config.database import DatabaseSettings
from hip.loaders.result import LoadResult
from hip.models.silver import SilverDHIS2Observation


class SilverPostgresLoader:
    """Load canonical DHIS2 observations into the Silver layer."""

    def __init__(self, settings: DatabaseSettings) -> None:
        self.settings = settings

    def _connection(self):
        return psycopg.connect(
            host=self.settings.host,
            port=self.settings.port,
            dbname=self.settings.database,
            user=self.settings.username,
            password=self.settings.password,
        )

    def load(
        self,
        records: list[SilverDHIS2Observation],
    ) -> LoadResult:
        if not records:
            return LoadResult(
                inserted_rows=0,
                duplicate_rows=0,
            )

        inserted = 0
        duplicates = 0

        with self._connection() as connection, connection.cursor() as cursor:
            for record in records:
                cursor.execute(
                    """
                    INSERT INTO silver.dhis2_observation (
                        bronze_id,
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
                        value_raw,
                        value_numeric,
                        quality_status,
                        quality_reason,
                        created_at_source,
                        last_updated_at_source
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (bronze_id) DO NOTHING
                    """,
                    (
                        record.bronze_id,
                        record.batch_id,
                        record.source_system,
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
                        record.value_raw,
                        record.value_numeric,
                        record.quality_status,
                        record.quality_reason,
                        record.created_at_source,
                        record.last_updated_at_source,
                    ),
                )

                if cursor.rowcount == 1:
                    inserted += 1
                else:
                    duplicates += 1

        return LoadResult(
            inserted_rows=inserted,
            duplicate_rows=duplicates,
        )

    def backfill_metadata_name(
        self,
        *,
        source_instance: str,
        metadata_type: str,
        uid: str,
        name: str,
    ) -> int:
        """Backfill a resolved metadata name into existing Silver observations."""

        columns_by_type = {
            "DATA_ELEMENT": (
                "data_element",
                "data_element_name",
            ),
            "ORG_UNIT": (
                "org_unit",
                "org_unit_name",
            ),
            "CATEGORY_OPTION_COMBO": (
                "category_option_combo",
                "category_option_combo_name",
            ),
            "ATTRIBUTE_OPTION_COMBO": (
                "attribute_option_combo",
                "attribute_option_combo_name",
            ),
        }

        if metadata_type not in columns_by_type:
            raise ValueError(
                f"Unsupported metadata type: {metadata_type}"
            )

        uid_column, name_column = columns_by_type[metadata_type]

        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE silver.dhis2_observation
                SET {name_column} = %s
                WHERE source_instance = %s
                AND {uid_column} = %s
                AND {name_column} IS NULL
                """,
                (
                    name,
                    source_instance,
                    uid,
                ),
            )

            return cursor.rowcount
