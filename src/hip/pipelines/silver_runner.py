"""Application-level execution for DHIS2 Silver processing."""

from hip.config.database import DatabaseSettings
from hip.config.settings import DHIS2Settings
from hip.loaders.result import LoadResult
from hip.loaders.silver_postgres import SilverPostgresLoader
from hip.metadata.api import DHIS2APIMetadataService
from hip.metadata.dataset_api import DHIS2DatasetMetadataService
from hip.metadata.dataset_sync import DHIS2DatasetMetadataSync
from hip.metadata.resolver import DHIS2MetadataResolver
from hip.pipelines.silver_dhis2 import SilverDHIS2Pipeline
from hip.repositories.bronze import BronzeDHIS2Repository
from hip.repositories.dataset import DHIS2DatasetRepository
from hip.repositories.metadata import DHIS2MetadataRepository
from hip.transformers.silver_dhis2 import SilverDHIS2Transformer


class SilverDHIS2Runner:
    """Construct and execute DHIS2 Bronze-to-Silver processing."""

    @staticmethod
    def run(
        *,
        source_instance: str,
        database_settings: DatabaseSettings,
        dhis2_settings: DHIS2Settings,
        limit: int | None = None,
    ) -> LoadResult:
        """Create and execute a configured DHIS2 Silver pipeline."""

        metadata_repository = DHIS2MetadataRepository(database_settings)

        metadata_service = DHIS2APIMetadataService(
            source_instance=source_instance,
            settings=dhis2_settings,
        )

        metadata_resolver = DHIS2MetadataResolver(
            repository=metadata_repository,
            api_service=metadata_service,
        )

        dataset_repository = DHIS2DatasetRepository(
            database_settings
        )

        dataset_service = DHIS2DatasetMetadataService(
            source_instance=source_instance,
            settings=dhis2_settings,
        )

        dataset_sync = DHIS2DatasetMetadataSync(
            api_service=dataset_service,
            repository=dataset_repository,
        )

        pipeline = SilverDHIS2Pipeline(
            settings=database_settings,
            repository=BronzeDHIS2Repository(database_settings),
            dataset_sync=dataset_sync,
            metadata_resolver=metadata_resolver,
            transformer=SilverDHIS2Transformer(),
            loader=SilverPostgresLoader(database_settings),
        )

        return pipeline.run(
            source_instance=source_instance,
            limit=limit,
        )
