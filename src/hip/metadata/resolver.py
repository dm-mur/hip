from dataclasses import dataclass

from hip.metadata.service import DHIS2MetadataService
from hip.repositories.metadata import DHIS2MetadataRepository


@dataclass(frozen=True)
class DHIS2MetadataLookups:
    """Resolved metadata lookups for one DHIS2 batch."""

    data_elements: dict[str, str]
    org_units: dict[str, str]
    category_option_combos: dict[str, str]
    attribute_option_combos: dict[str, str]


class DHIS2MetadataResolver:
    """Resolve DHIS2 metadata using persistent cache before the API."""

    def __init__(
        self,
        *,
        repository: DHIS2MetadataRepository,
        api_service: DHIS2MetadataService,
    ) -> None:
        self.repository = repository
        self.api_service = api_service

    def resolve_many(
        self,
        *,
        source_instance: str,
        data_elements: set[str],
        org_units: set[str],
        category_option_combos: set[str],
        attribute_option_combos: set[str],
    ) -> DHIS2MetadataLookups:
        data_element_names = self.repository.get_many(
            source_instance=source_instance,
            metadata_type="DATA_ELEMENT",
            uids=data_elements,
        )
        org_unit_names = self.repository.get_many(
            source_instance=source_instance,
            metadata_type="ORG_UNIT",
            uids=org_units,
        )
        category_option_combo_names = self.repository.get_many(
            source_instance=source_instance,
            metadata_type="CATEGORY_OPTION_COMBO",
            uids=category_option_combos,
        )
        attribute_option_combo_names = self.repository.get_many(
            source_instance=source_instance,
            metadata_type="ATTRIBUTE_OPTION_COMBO",
            uids=attribute_option_combos,
        )

        missing_data_elements = data_elements - data_element_names.keys()
        missing_org_units = org_units - org_unit_names.keys()
        missing_category_option_combos = (
            category_option_combos - category_option_combo_names.keys()
        )
        missing_attribute_option_combos = (
            attribute_option_combos - attribute_option_combo_names.keys()
        )

        missing_combos = (
            missing_category_option_combos
            | missing_attribute_option_combos
        )

        if (
            missing_data_elements
            or missing_org_units
            or missing_combos
        ):
            self.api_service.preload(
                data_elements=missing_data_elements,
                org_units=missing_org_units,
                category_option_combos=missing_combos,
            )

        for uid in missing_data_elements:
            metadata = self.api_service.resolve(
                data_element=uid,
                org_unit="",
                category_option_combo=None,
                attribute_option_combo=None,
            )
            if metadata.data_element_name is not None:
                data_element_names[uid] = metadata.data_element_name

        for uid in missing_org_units:
            metadata = self.api_service.resolve(
                data_element="",
                org_unit=uid,
                category_option_combo=None,
                attribute_option_combo=None,
            )
            if metadata.org_unit_name is not None:
                org_unit_names[uid] = metadata.org_unit_name

        for uid in missing_category_option_combos:
            metadata = self.api_service.resolve(
                data_element="",
                org_unit="",
                category_option_combo=uid,
                attribute_option_combo=None,
            )
            if metadata.category_option_combo_name is not None:
                category_option_combo_names[uid] = (
                    metadata.category_option_combo_name
                )

        for uid in missing_attribute_option_combos:
            metadata = self.api_service.resolve(
                data_element="",
                org_unit="",
                category_option_combo=None,
                attribute_option_combo=uid,
            )
            if metadata.attribute_option_combo_name is not None:
                attribute_option_combo_names[uid] = (
                    metadata.attribute_option_combo_name
                )

        new_data_elements = {
            uid: data_element_names[uid]
            for uid in missing_data_elements
            if uid in data_element_names
        }
        new_org_units = {
            uid: org_unit_names[uid]
            for uid in missing_org_units
            if uid in org_unit_names
        }
        new_category_option_combos = {
            uid: category_option_combo_names[uid]
            for uid in missing_category_option_combos
            if uid in category_option_combo_names
        }
        new_attribute_option_combos = {
            uid: attribute_option_combo_names[uid]
            for uid in missing_attribute_option_combos
            if uid in attribute_option_combo_names
        }

        if new_data_elements:
            self.repository.upsert_many(
                source_instance=source_instance,
                metadata_type="DATA_ELEMENT",
                metadata=new_data_elements,
            )

        if new_org_units:
            self.repository.upsert_many(
                source_instance=source_instance,
                metadata_type="ORG_UNIT",
                metadata=new_org_units,
            )

        if new_category_option_combos:
            self.repository.upsert_many(
                source_instance=source_instance,
                metadata_type="CATEGORY_OPTION_COMBO",
                metadata=new_category_option_combos,
            )

        if new_attribute_option_combos:
            self.repository.upsert_many(
                source_instance=source_instance,
                metadata_type="ATTRIBUTE_OPTION_COMBO",
                metadata=new_attribute_option_combos,
            )

        return DHIS2MetadataLookups(
            data_elements=data_element_names,
            org_units=org_unit_names,
            category_option_combos=category_option_combo_names,
            attribute_option_combos=attribute_option_combo_names,
        )
