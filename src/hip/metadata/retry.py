"""Retry unresolved DHIS2 metadata resolution."""

from hip.loaders.silver_postgres import SilverPostgresLoader
from hip.metadata.service import DHIS2MetadataService
from hip.repositories.metadata import DHIS2MetadataRepository


class DHIS2MetadataRetryService:
    """Retry metadata that previously failed to resolve."""

    def __init__(
        self,
        *,
        repository: DHIS2MetadataRepository,
        api_service: DHIS2MetadataService,
        silver_loader: SilverPostgresLoader,
    ) -> None:
        self.repository = repository
        self.api_service = api_service
        self.silver_loader = silver_loader

    def retry(
        self,
        *,
        source_instance: str,
    ) -> dict[str, int]:
        """Retry unresolved metadata for one source instance."""

        unresolved_records = self.repository.fetch_unresolved(
            source_instance=source_instance,
        )

        data_elements = {
            record["uid"]
            for record in unresolved_records
            if record["metadata_type"] == "DATA_ELEMENT"
        }

        org_units = {
            record["uid"]
            for record in unresolved_records
            if record["metadata_type"] == "ORG_UNIT"
        }

        category_option_combos = {
            record["uid"]
            for record in unresolved_records
            if record["metadata_type"] in {
                "CATEGORY_OPTION_COMBO",
                "ATTRIBUTE_OPTION_COMBO",
            }
        }

        if data_elements or org_units or category_option_combos:
            self.api_service.preload(
                data_elements=data_elements,
                org_units=org_units,
                category_option_combos=category_option_combos,
            )

        resolved_count = 0
        unresolved_count = 0

        for record in unresolved_records:
            metadata_type = record["metadata_type"]
            uid = record["uid"]

            resolve_kwargs = {
                "data_element": None,
                "org_unit": None,
                "category_option_combo": None,
                "attribute_option_combo": None,
            }

            name_attribute_by_type = {
                "DATA_ELEMENT": "data_element_name",
                "ORG_UNIT": "org_unit_name",
                "CATEGORY_OPTION_COMBO": "category_option_combo_name",
                "ATTRIBUTE_OPTION_COMBO": "attribute_option_combo_name",
            }

            request_field_by_type = {
                "DATA_ELEMENT": "data_element",
                "ORG_UNIT": "org_unit",
                "CATEGORY_OPTION_COMBO": "category_option_combo",
                "ATTRIBUTE_OPTION_COMBO": "attribute_option_combo",
            }

            request_field = request_field_by_type[metadata_type]
            resolve_kwargs[request_field] = uid

            metadata = self.api_service.resolve(**resolve_kwargs)

            name_attribute = name_attribute_by_type[metadata_type]
            resolved_name = getattr(metadata, name_attribute)

            if resolved_name is None:
                self.repository.record_unresolved(
                    source_instance=source_instance,
                    metadata_type=metadata_type,
                    uid=uid,
                )
                unresolved_count += 1
                continue

            self.repository.upsert_many(
                source_instance=source_instance,
                metadata_type=metadata_type,
                metadata={
                    uid: resolved_name,
                },
            )

            self.silver_loader.backfill_metadata_name(
                source_instance=source_instance,
                metadata_type=metadata_type,
                uid=uid,
                name=resolved_name,
            )

            self.repository.mark_resolved(
                source_instance=source_instance,
                metadata_type=metadata_type,
                uid=uid,
            )

            resolved_count += 1

        return {
            "attempted": len(unresolved_records),
            "resolved": resolved_count,
            "unresolved": unresolved_count,
        }
