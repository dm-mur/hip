"""
DHIS2 transformation logic.

Transforms source-specific DHIS2 records into the canonical
HIP DHIS2Record model.
"""

import hashlib
import json
from typing import Any

from hip.mappings.dhis2 import DEFAULT_DHIS2_MAPPING
from hip.metadata.dhis2 import DHIS2Metadata
from hip.metadata.service import DHIS2MetadataService
from hip.models.dhis2 import DHIS2Record
from hip.pipelines.context import PipelineContext
from hip.transformers.base import BaseTransformer


class DHIS2Transformer(BaseTransformer):
    """Transform raw DHIS2 records into canonical HIP records."""

    def __init__(
        self,
        source_instance: str,
        mapping: dict[str, str] | None = None,
        metadata_service: DHIS2MetadataService | None = None,
    ) -> None:
        self.source_instance = source_instance
        self.mapping = (
            DEFAULT_DHIS2_MAPPING
            if mapping is None
            else mapping
        )
        self.metadata_service = metadata_service

    def transform(
        self,
        record: dict[str, Any],
        context: PipelineContext,
    ) -> DHIS2Record:
        """Transform one raw DHIS2 record into a canonical DHIS2Record."""

        canonical = {
            field: record.get(source_field)
            for field, source_field in self.mapping.items()
        }

        record_hash = self._generate_record_hash(record)

        metadata = DHIS2Metadata()

        if self.metadata_service is not None:
            metadata = self.metadata_service.resolve(
                data_element=canonical["data_element"],
                org_unit=canonical["org_unit"],
                category_option_combo=canonical["category_option_combo"],
                attribute_option_combo=canonical["attribute_option_combo"],
            )

        return DHIS2Record(
            batch_id=context.batch_id,
            source_instance=self.source_instance,
            dataset_id=canonical["dataset_id"],
            data_element=canonical["data_element"],
            org_unit=canonical["org_unit"],
            period=canonical["period"],
            category_option_combo=canonical["category_option_combo"],
            attribute_option_combo=canonical["attribute_option_combo"],
            data_element_name=(
                metadata.data_element_name
                or record.get("dataElementName")
            ),
            org_unit_name=(
                metadata.org_unit_name
                or record.get("orgUnitName")
            ),
            category_option_combo_name=(
                metadata.category_option_combo_name
                or record.get("categoryOptionComboName")
            ),
            attribute_option_combo_name=(
                metadata.attribute_option_combo_name
                or record.get("attributeOptionComboName")
            ),
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