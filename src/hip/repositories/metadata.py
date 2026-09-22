from hip.config.database import DatabaseSettings


class DHIS2MetadataRepository:
    """Persist and retrieve instance-scoped DHIS2 metadata."""

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
        metadata_type: str,
        uid: str,
    ) -> str | None:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT name
                FROM silver.dhis2_metadata
                WHERE source_instance = %s
                  AND metadata_type = %s
                  AND uid = %s
                """,
                (
                    source_instance,
                    metadata_type,
                    uid,
                ),
            )

            row = cursor.fetchone()

        return row[0] if row is not None else None

    def get_many(
        self,
        *,
        source_instance: str,
        metadata_type: str,
        uids: set[str],
    ) -> dict[str, str]:
        """Return cached names for the requested metadata UIDs."""

        if not uids:
            return {}

        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT uid, name
                FROM silver.dhis2_metadata
                WHERE source_instance = %s
                  AND metadata_type = %s
                  AND uid = ANY(%s)
                """,
                (
                    source_instance,
                    metadata_type,
                    list(uids),
                ),
            )

            rows = cursor.fetchall()

        return {uid: name for uid, name in rows}

    def upsert(
        self,
        *,
        source_instance: str,
        metadata_type: str,
        uid: str,
        name: str,
    ) -> None:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO silver.dhis2_metadata (
                    source_instance,
                    metadata_type,
                    uid,
                    name
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (
                    source_instance,
                    metadata_type,
                    uid
                )
                DO UPDATE SET
                    name = EXCLUDED.name,
                    resolved_at = NOW()
                """,
                (
                    source_instance,
                    metadata_type,
                    uid,
                    name,
                ),
            )

    def upsert_many(
        self,
        *,
        source_instance: str,
        metadata_type: str,
        metadata: dict[str, str],
    ) -> int:
        """Persist multiple metadata UID-to-name mappings."""

        if not metadata:
            return 0

        rows = [
            (
                source_instance,
                metadata_type,
                uid,
                name,
            )
            for uid, name in metadata.items()
        ]

        with self._connection() as connection, connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO silver.dhis2_metadata (
                    source_instance,
                    metadata_type,
                    uid,
                    name
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (
                    source_instance,
                    metadata_type,
                    uid
                )
                DO UPDATE SET
                    name = EXCLUDED.name,
                    resolved_at = NOW()
                """,
                rows,
            )

        return len(rows)

    def seed_from_bronze(self, *, source_instance: str) -> int:
        """Seed the metadata cache from names already available in Bronze."""

        metadata_sources = (
            ("DATA_ELEMENT", "data_element", "data_element_name"),
            ("ORG_UNIT", "org_unit", "org_unit_name"),
            (
                "CATEGORY_OPTION_COMBO",
                "category_option_combo",
                "category_option_combo_name",
            ),
            (
                "ATTRIBUTE_OPTION_COMBO",
                "attribute_option_combo",
                "attribute_option_combo_name",
            ),
        )

        inserted_or_updated = 0

        with self._connection() as connection, connection.cursor() as cursor:
            for metadata_kind, uid_column, name_column in metadata_sources:
                query = f"""
                    INSERT INTO silver.dhis2_metadata (
                        source_instance,
                        metadata_type,
                        uid,
                        name
                    )
                    SELECT DISTINCT ON ({uid_column})
                        source_instance,
                        %s,
                        {uid_column},
                        {name_column}
                    FROM bronze.dhis2_data
                    WHERE source_instance = %s
                      AND NULLIF(BTRIM({uid_column}), '') IS NOT NULL
                      AND NULLIF(BTRIM({name_column}), '') IS NOT NULL
                    ORDER BY {uid_column}, ingested_at DESC
                    ON CONFLICT (
                        source_instance,
                        metadata_type,
                        uid
                    )
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        resolved_at = NOW()
                """

                cursor.execute(
                    query,
                    (
                        metadata_kind,
                        source_instance,
                    ),
                )

                inserted_or_updated += cursor.rowcount

        return inserted_or_updated
