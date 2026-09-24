import psycopg

from hip.config.database import DatabaseSettings
from hip.loaders.result import LoadResult
from hip.loaders.silver_postgres import SilverPostgresLoader
from hip.metadata.dataset_sync import DHIS2DatasetMetadataSync
from hip.metadata.resolver import DHIS2MetadataResolver
from hip.repositories.bronze import BronzeDHIS2Repository
from hip.transformers.silver_dhis2 import SilverDHIS2Transformer


class SilverDHIS2Pipeline:
    """Process unprocessed DHIS2 Bronze records into Silver."""

    def __init__(
        self,
        *,
        settings: DatabaseSettings,
        repository: BronzeDHIS2Repository,
        dataset_sync: DHIS2DatasetMetadataSync,
        metadata_resolver: DHIS2MetadataResolver,
        transformer: SilverDHIS2Transformer,
        loader: SilverPostgresLoader,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.dataset_sync = dataset_sync
        self.metadata_resolver = metadata_resolver
        self.transformer = transformer
        self.loader = loader

    def run(
        self,
        *,
        source_instance: str,
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
                source_instance=source_instance,
                limit=limit,
            )

        if not bronze_records:
            return self.loader.load([])

        dataset_ids = {
            record["dataset_id"]
            for record in bronze_records
            if record.get("dataset_id")
        }

        for dataset_id in sorted(dataset_ids):
            self.dataset_sync.sync(
                source_instance=source_instance,
                dataset_id=dataset_id,
            )

        data_elements = {
            record["data_element"]
            for record in bronze_records
            if record.get("data_element")
        }
        org_units = {
            record["org_unit"]
            for record in bronze_records
            if record.get("org_unit")
        }
        category_option_combos = {
            record["category_option_combo"]
            for record in bronze_records
            if record.get("category_option_combo")
        }
        attribute_option_combos = {
            record["attribute_option_combo"]
            for record in bronze_records
            if record.get("attribute_option_combo")
        }

        lookups = self.metadata_resolver.resolve_many(
            source_instance=source_instance,
            data_elements=data_elements,
            org_units=org_units,
            category_option_combos=category_option_combos,
            attribute_option_combos=attribute_option_combos,
        )

        enriched_records = [
            {
                **record,
                "data_element_name": (
                    record.get("data_element_name")
                    or lookups.data_elements.get(
                        record["data_element"]
                    )
                ),
                "org_unit_name": (
                    record.get("org_unit_name")
                    or lookups.org_units.get(
                        record["org_unit"]
                    )
                ),
                "category_option_combo_name": (
                    record.get("category_option_combo_name")
                    or lookups.category_option_combos.get(
                        record.get("category_option_combo")
                    )
                ),
                "attribute_option_combo_name": (
                    record.get("attribute_option_combo_name")
                    or lookups.attribute_option_combos.get(
                        record.get("attribute_option_combo")
                    )
                ),
            }
            for record in bronze_records
        ]

        observations = [
            self.transformer.transform(record)
            for record in enriched_records
        ]

        return self.loader.load(observations)
