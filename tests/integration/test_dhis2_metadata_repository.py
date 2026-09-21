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