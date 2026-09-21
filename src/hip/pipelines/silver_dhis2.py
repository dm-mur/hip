import psycopg

from hip.config.database import DatabaseSettings
from hip.loaders.result import LoadResult
from hip.loaders.silver_postgres import SilverPostgresLoader
from hip.repositories.bronze import BronzeDHIS2Repository
from hip.transformers.silver_dhis2 import SilverDHIS2Transformer


class SilverDHIS2Pipeline:
    """Process unprocessed DHIS2 Bronze records into Silver."""

    def __init__(
        self,
        *,
        settings: DatabaseSettings,
        repository: BronzeDHIS2Repository,
        transformer: SilverDHIS2Transformer,
        loader: SilverPostgresLoader,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.transformer = transformer
        self.loader = loader

    def run(
        self,
        *,
        limit: int | None = None,
    ) -> LoadResult:
        with psycopg.connect(
            host=self.settings.host,
            port=self.settings.port,
            dbname=self.settings.database,
            user=self.settings.username,
            password=self.settings.password,
        ) as connection:
            bronze_records = self.repository.fetch_unprocessed(
                connection,
                limit=limit,
            )

        observations = [
            self.transformer.transform(record)
            for record in bronze_records
        ]

        return self.loader.load(observations)
