"""
DHIS2 transformation logic.

Transforms source-specific DHIS2 records into the canonical
HIP DHIS2Record model.
"""

import hashlib
import json
from typing import Any

from hip.mappings.dhis2 import DEFAULT_DHIS2_MAPPING
from hip.models.dhis2 import DHIS2Record


class DHIS2Transformer:
    """Transform raw DHIS2 records into canonical HIP records."""

    def __init__(
        self,
        source_instance: str,
        mapping: dict[str, str] | None = None,
    ) -> None:
        self.source_instance = source_instance
        self.mapping = mapping or DEFAULT_DHIS2_MAPPING

    def transform(
        self,
        record: dict[str, Any],
        context: Any | None = None,
    ) -> DHIS2Record:
        """
        Transform one raw DHIS2 record into a canonical DHIS2Record.
        """

        if context is None:
            raise ValueError("Pipeline context with batch_id is required")

        canonical = {
            field: record.get(source_field)
            for field, source_field in self.mapping.items()
        }

        record_hash = self._generate_record_hash(record)

        return DHIS2Record(
            batch_id=context.batch_id,
            source_instance=self.source_instance,
            dataset_id=canonical["dataset_id"],
            data_element=canonical["data_element"],
            data_element_name=canonical["data_element_name"],
            org_unit=canonical["org_unit"],
            org_unit_name=canonical["org_unit_name"],
            period=canonical["period"],
            category_option_combo=canonical["category_option_combo"],
            category_option_combo_name=canonical["category_option_combo_name"],
            attribute_option_combo=canonical["attribute_option_combo"],
            attribute_option_combo_name=canonical["attribute_option_combo_name"],
            value=canonical["value"],
            comment=canonical["comment"],
            followup=canonical["followup"],
            stored_by=canonical["stored_by"],
            created_at_source=canonical["created_at_source"],
            last_updated_at_source=canonical["last_updated_at_source"],
            raw_payload=record,
            record_hash=record_hash,
        )

    @staticmethod
    def _generate_record_hash(record: dict[str, Any]) -> str:
        """Generate a deterministic SHA-256 fingerprint for a source record."""

        serialized = json.dumps(
            record,
            sort_keys=True,
            default=str,
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()