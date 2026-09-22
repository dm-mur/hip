from unittest.mock import MagicMock

from hip.metadata.dhis2 import DHIS2Metadata
from hip.metadata.resolver import DHIS2MetadataResolver


def test_resolver_uses_cache_and_fetches_only_missing_metadata():
    repository = MagicMock()
    api_service = MagicMock()

    repository.get_many.side_effect = [
        {"DE001": "Cached Data Element"},
        {"OU001": "Cached Organisation Unit"},
        {"COC001": "Cached Category Combo"},
        {"AOC001": "Cached Attribute Combo"},
    ]

    def resolve_metadata(
        *,
        data_element,
        org_unit,
        category_option_combo,
        attribute_option_combo,
    ):
        return DHIS2Metadata(
            data_element_name=(
                "Fetched Data Element"
                if data_element == "DE002"
                else None
            ),
            org_unit_name=(
                "Fetched Organisation Unit"
                if org_unit == "OU002"
                else None
            ),
            category_option_combo_name=(
                "Fetched Category Combo"
                if category_option_combo == "COC002"
                else None
            ),
            attribute_option_combo_name=(
                "Fetched Attribute Combo"
                if attribute_option_combo == "AOC002"
                else None
            ),
        )

    api_service.resolve.side_effect = resolve_metadata

    resolver = DHIS2MetadataResolver(
        repository=repository,
        api_service=api_service,
    )

    result = resolver.resolve_many(
        source_instance="test_instance",
        data_elements={"DE001", "DE002"},
        org_units={"OU001", "OU002"},
        category_option_combos={"COC001", "COC002"},
        attribute_option_combos={"AOC001", "AOC002"},
    )

    api_service.preload.assert_called_once_with(
        data_elements={"DE002"},
        org_units={"OU002"},
        category_option_combos={"COC002", "AOC002"},
    )

    assert result.data_elements == {
        "DE001": "Cached Data Element",
        "DE002": "Fetched Data Element",
    }
    assert result.org_units == {
        "OU001": "Cached Organisation Unit",
        "OU002": "Fetched Organisation Unit",
    }
    assert result.category_option_combos == {
        "COC001": "Cached Category Combo",
        "COC002": "Fetched Category Combo",
    }
    assert result.attribute_option_combos == {
        "AOC001": "Cached Attribute Combo",
        "AOC002": "Fetched Attribute Combo",
    }

    repository.upsert_many.assert_any_call(
        source_instance="test_instance",
        metadata_type="DATA_ELEMENT",
        metadata={"DE002": "Fetched Data Element"},
    )
    repository.upsert_many.assert_any_call(
        source_instance="test_instance",
        metadata_type="ORG_UNIT",
        metadata={"OU002": "Fetched Organisation Unit"},
    )
    repository.upsert_many.assert_any_call(
        source_instance="test_instance",
        metadata_type="CATEGORY_OPTION_COMBO",
        metadata={"COC002": "Fetched Category Combo"},
    )
    repository.upsert_many.assert_any_call(
        source_instance="test_instance",
        metadata_type="ATTRIBUTE_OPTION_COMBO",
        metadata={"AOC002": "Fetched Attribute Combo"},
    )

def test_resolver_does_not_call_api_when_all_metadata_is_cached():
    repository = MagicMock()
    api_service = MagicMock()

    repository.get_many.side_effect = [
        {"DE001": "Cached Data Element"},
        {"OU001": "Cached Organisation Unit"},
        {"COC001": "Cached Category Combo"},
        {"AOC001": "Cached Attribute Combo"},
    ]

    resolver = DHIS2MetadataResolver(
        repository=repository,
        api_service=api_service,
    )

    result = resolver.resolve_many(
        source_instance="test_instance",
        data_elements={"DE001"},
        org_units={"OU001"},
        category_option_combos={"COC001"},
        attribute_option_combos={"AOC001"},
    )

    api_service.preload.assert_not_called()
    api_service.resolve.assert_not_called()
    repository.upsert_many.assert_not_called()

    assert result.data_elements == {
        "DE001": "Cached Data Element",
    }
    assert result.org_units == {
        "OU001": "Cached Organisation Unit",
    }
    assert result.category_option_combos == {
        "COC001": "Cached Category Combo",
    }
    assert result.attribute_option_combos == {
        "AOC001": "Cached Attribute Combo",
    }

def test_resolver_leaves_unresolved_metadata_absent():
    repository = MagicMock()
    api_service = MagicMock()

    repository.get_many.side_effect = [
        {},
        {},
        {},
        {},
    ]

    api_service.resolve.return_value = DHIS2Metadata()

    resolver = DHIS2MetadataResolver(
        repository=repository,
        api_service=api_service,
    )

    result = resolver.resolve_many(
        source_instance="test_instance",
        data_elements={"UNKNOWN_DE"},
        org_units=set(),
        category_option_combos=set(),
        attribute_option_combos=set(),
    )

    api_service.preload.assert_called_once_with(
        data_elements={"UNKNOWN_DE"},
        org_units=set(),
        category_option_combos=set(),
    )

    assert result.data_elements == {}
    assert result.org_units == {}
    assert result.category_option_combos == {}
    assert result.attribute_option_combos == {}

    repository.upsert_many.assert_not_called()
