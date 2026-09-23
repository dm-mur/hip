"""Integration tests for the DHIS2 dataset metadata repository."""

from hip.config.database import DatabaseSettings
from hip.repositories.dataset import DHIS2DatasetRepository


def make_settings() -> DatabaseSettings:
    """Return database settings from the integration-test environment."""

    return DatabaseSettings.from_environment()


def test_dataset_repository_upserts_and_gets_dataset_metadata():
    """Repository should persist and retrieve source-scoped dataset metadata."""

    repository = DHIS2DatasetRepository(make_settings())

    repository.upsert(
        source_instance="dataset_repo_test",
        dataset_id="DATASET_REPO_001",
        dataset_name="Repository Test Dataset",
        period_type="Monthly",
    )

    metadata = repository.get(
        source_instance="dataset_repo_test",
        dataset_id="DATASET_REPO_001",
    )

    assert metadata == {
        "dataset_id": "DATASET_REPO_001",
        "dataset_name": "Repository Test Dataset",
        "period_type": "Monthly",
    }


def test_dataset_repository_upsert_refreshes_existing_metadata():
    """A later DHIS2 resolution should refresh stored dataset metadata."""

    repository = DHIS2DatasetRepository(make_settings())

    repository.upsert(
        source_instance="dataset_repo_refresh_test",
        dataset_id="DATASET_REPO_002",
        dataset_name="Original Dataset Name",
        period_type="Monthly",
    )

    repository.upsert(
        source_instance="dataset_repo_refresh_test",
        dataset_id="DATASET_REPO_002",
        dataset_name="Updated Dataset Name",
        period_type="Quarterly",
    )

    metadata = repository.get(
        source_instance="dataset_repo_refresh_test",
        dataset_id="DATASET_REPO_002",
    )

    assert metadata == {
        "dataset_id": "DATASET_REPO_002",
        "dataset_name": "Updated Dataset Name",
        "period_type": "Quarterly",
    }


def test_dataset_repository_get_returns_none_when_missing():
    """Repository should return None when dataset metadata is not cached."""

    repository = DHIS2DatasetRepository(make_settings())

    metadata = repository.get(
        source_instance="dataset_repo_missing_test",
        dataset_id="DOES_NOT_EXIST",
    )

    assert metadata is None
