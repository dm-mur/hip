from hip.config.database import DatabaseSettings
from hip.repositories.metadata import DHIS2MetadataRepository

SOURCE_INSTANCE = "metadata_repository_test"
METADATA_TYPE = "DATA_ELEMENT"
UID = "TEST_METADATA_UID"


def test_metadata_repository_is_instance_scoped():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata
            WHERE uid = %s
            """,
            (UID,),
        )

    repository.upsert(
        source_instance=SOURCE_INSTANCE,
        metadata_type=METADATA_TYPE,
        uid=UID,
        name="Test Data Element",
    )

    assert repository.get(
        source_instance=SOURCE_INSTANCE,
        metadata_type=METADATA_TYPE,
        uid=UID,
    ) == "Test Data Element"

    assert repository.get(
        source_instance="different_instance",
        metadata_type=METADATA_TYPE,
        uid=UID,
    ) is None

    repository.upsert(
        source_instance="different_instance",
        metadata_type=METADATA_TYPE,
        uid=UID,
        name="Different Meaning",
    )

    assert repository.get(
        source_instance=SOURCE_INSTANCE,
        metadata_type=METADATA_TYPE,
        uid=UID,
    ) == "Test Data Element"

    assert repository.get(
        source_instance="different_instance",
        metadata_type=METADATA_TYPE,
        uid=UID,
    ) == "Different Meaning"

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata
            WHERE uid = %s
            """,
            (UID,),
        )

def test_metadata_repository_seeds_known_metadata_from_bronze():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    seeded_rows = repository.seed_from_bronze(
        source_instance="live_test",
    )

    assert seeded_rows > 0

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM silver.dhis2_metadata
            WHERE source_instance = %s
            """,
            ("live_test",),
        )

        row = cursor.fetchone()

    assert row is not None
    assert row[0] > 0

def test_metadata_repository_get_many_returns_only_cached_uids():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    source_instance = "metadata_bulk_test"
    metadata_type = "DATA_ELEMENT"

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata
            WHERE source_instance IN (%s, %s)
            """,
            (
                source_instance,
                "different_bulk_instance",
            ),
        )

    repository.upsert(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid="DE001",
        name="Data Element One",
    )

    repository.upsert(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid="DE002",
        name="Data Element Two",
    )

    repository.upsert(
        source_instance="different_bulk_instance",
        metadata_type=metadata_type,
        uid="DE003",
        name="Wrong Instance",
    )

    result = repository.get_many(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uids={
            "DE001",
            "DE002",
            "DE003",
            "UNKNOWN",
        },
    )

    assert result == {
        "DE001": "Data Element One",
        "DE002": "Data Element Two",
    }

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata
            WHERE source_instance IN (%s, %s)
            """,
            (
                source_instance,
                "different_bulk_instance",
            ),
        )

def test_metadata_repository_get_many_handles_empty_uid_set():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    result = repository.get_many(
        source_instance="metadata_bulk_test",
        metadata_type="DATA_ELEMENT",
        uids=set(),
    )

    assert result == {}

def test_metadata_repository_upsert_many_persists_metadata():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    source_instance = "metadata_upsert_many_test"
    metadata_type = "DATA_ELEMENT"

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata
            WHERE source_instance = %s
            """,
            (source_instance,),
        )

    processed = repository.upsert_many(
        source_instance=source_instance,
        metadata_type=metadata_type,
        metadata={
            "DE001": "Data Element One",
            "DE002": "Data Element Two",
            "DE003": "Data Element Three",
        },
    )

    assert processed == 3

    result = repository.get_many(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uids={"DE001", "DE002", "DE003"},
    )

    assert result == {
        "DE001": "Data Element One",
        "DE002": "Data Element Two",
        "DE003": "Data Element Three",
    }

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata
            WHERE source_instance = %s
            """,
            (source_instance,),
        )

def test_metadata_repository_upsert_many_handles_empty_metadata():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    processed = repository.upsert_many(
        source_instance="metadata_upsert_many_test",
        metadata_type="DATA_ELEMENT",
        metadata={},
    )

    assert processed == 0

def test_metadata_repository_records_unresolved_metadata():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    source_instance = "metadata_resolution_test"
    metadata_type = "CATEGORY_OPTION_COMBO"
    uid = "UNRESOLVED_COC_001"

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata_resolution
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

    repository.record_unresolved(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid=uid,
    )

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                status,
                attempt_count,
                resolved_at
            FROM silver.dhis2_metadata_resolution
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

    assert row is not None
    assert row[0] == "UNRESOLVED"
    assert row[1] == 1
    assert row[2] is None

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata_resolution
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


def test_metadata_repository_increments_unresolved_attempt_count():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    source_instance = "metadata_resolution_retry_test"
    metadata_type = "CATEGORY_OPTION_COMBO"
    uid = "UNRESOLVED_COC_002"

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata_resolution
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

    repository.record_unresolved(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid=uid,
    )

    repository.record_unresolved(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid=uid,
    )

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                status,
                attempt_count,
                resolved_at
            FROM silver.dhis2_metadata_resolution
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

    assert row is not None
    assert row[0] == "UNRESOLVED"
    assert row[1] == 2
    assert row[2] is None

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata_resolution
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


def test_metadata_repository_marks_unresolved_metadata_resolved():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    source_instance = "metadata_resolution_resolved_test"
    metadata_type = "CATEGORY_OPTION_COMBO"
    uid = "RESOLVED_COC_001"

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata_resolution
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

    repository.record_unresolved(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid=uid,
    )

    repository.mark_resolved(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid=uid,
    )

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                status,
                attempt_count,
                resolved_at
            FROM silver.dhis2_metadata_resolution
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

    assert row is not None
    assert row[0] == "RESOLVED"
    assert row[1] == 1
    assert row[2] is not None

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata_resolution
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

def test_metadata_repository_reopens_resolved_metadata():
    settings = DatabaseSettings.from_environment()
    repository = DHIS2MetadataRepository(settings)

    source_instance = "metadata_resolution_reopen_test"
    metadata_type = "CATEGORY_OPTION_COMBO"
    uid = "REOPEN_COC_001"

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata_resolution
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

    repository.record_unresolved(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid=uid,
    )

    repository.mark_resolved(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid=uid,
    )

    repository.record_unresolved(
        source_instance=source_instance,
        metadata_type=metadata_type,
        uid=uid,
    )

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                status,
                attempt_count,
                resolved_at
            FROM silver.dhis2_metadata_resolution
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

    assert row is not None
    assert row[0] == "UNRESOLVED"
    assert row[1] == 2
    assert row[2] is None

    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM silver.dhis2_metadata_resolution
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
