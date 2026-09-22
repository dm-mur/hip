from typing import Any

from hip.config.database import DatabaseSettings


class BronzeDHIS2Repository:
    """Read DHIS2 records eligible for Silver processing."""

    def __init__(self, settings: DatabaseSettings) -> None:
        self.settings = settings

    def fetch_unprocessed(
        self,
        connection,
        *,
        source_instance: str,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                b.bronze_id,
                b.batch_id,
                b.source_system,
                b.source_instance,
                b.dataset_id,
                b.data_element,
                b.data_element_name,
                b.org_unit,
                b.org_unit_name,
                b.period,
                b.category_option_combo,
                b.category_option_combo_name,
                b.attribute_option_combo,
                b.attribute_option_combo_name,
                b.value,
                b.created_at_source,
                b.last_updated_at_source
            FROM bronze.dhis2_data AS b
            LEFT JOIN silver.dhis2_observation AS s
                ON s.bronze_id = b.bronze_id
            WHERE s.bronze_id IS NULL
                AND b.source_instance = %s
            ORDER BY b.bronze_id
        """

        params: tuple = (source_instance,)

        if limit is not None:
            query += "\nLIMIT %s"
            params = (source_instance, limit)

        with connection.cursor() as cursor:
            cursor.execute(query, params)

            columns = [
                description.name
                for description in cursor.description
            ]

            return [
                dict(zip(columns, row, strict=True))
                for row in cursor.fetchall()
            ]
