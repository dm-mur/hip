from hip.metadata.dhis2 import DHIS2Metadata
from hip.metadata.service import DHIS2MetadataService


class FakeMetadataService:
    def resolve(
        self,
        *,
        data_element: str,
        org_unit: str,
        category_option_combo: str | None,
        attribute_option_combo: str | None,
    ) -> DHIS2Metadata:
        return DHIS2Metadata(
            data_element_name=f"Data Element {data_element}",
            org_unit_name=f"Org Unit {org_unit}",
            category_option_combo_name=category_option_combo,
            attribute_option_combo_name=attribute_option_combo,
        )


def use_metadata_service(
    service: DHIS2MetadataService,
) -> DHIS2Metadata:
    return service.resolve(
        data_element="DE123",
        org_unit="OU456",
        category_option_combo="COC789",
        attribute_option_combo="AOC000",
    )


def test_metadata_service_contract():
    metadata = use_metadata_service(FakeMetadataService())

    assert metadata.data_element_name == "Data Element DE123"
    assert metadata.org_unit_name == "Org Unit OU456"
    assert metadata.category_option_combo_name == "COC789"
    assert metadata.attribute_option_combo_name == "AOC000"
