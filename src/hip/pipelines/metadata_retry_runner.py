"""Application-level execution for DHIS2 metadata retry."""

from hip.config.database import DatabaseSettings
from hip.config.settings import DHIS2Settings
from hip.loaders.silver_postgres import SilverPostgresLoader
from hip.metadata.api import DHIS2APIMetadataService
from hip.metadata.retry import DHIS2MetadataRetryService
from hip.repositories.metadata import DHIS2MetadataRepository


class DHIS2MetadataRetryRunner:
    """Construct and execute DHIS2 metadata retry processing."""

    @staticmethod
    def run(
        *,
        source_instance: str,
        database_settings: DatabaseSettings,
        dhis2_settings: DHIS2Settings,
    ) -> dict[str, int]:
        """Retry unresolved metadata for one DHIS2 source instance."""

        repository = DHIS2MetadataRepository(database_settings)

        api_service = DHIS2APIMetadataService(
            source_instance=source_instance,
            settings=dhis2_settings,
        )

        silver_loader = SilverPostgresLoader(database_settings)

        service = DHIS2MetadataRetryService(
            repository=repository,
            api_service=api_service,
            silver_loader=silver_loader,
        )

        return service.retry(
            source_instance=source_instance,
        )
