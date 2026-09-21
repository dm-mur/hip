from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class SilverDHIS2Observation:
    bronze_id: int
    batch_id: UUID
    source_system: str
    source_instance: str

    dataset_id: str | None
    data_element: str
    data_element_name: str | None

    org_unit: str
    org_unit_name: str | None

    period: str

    category_option_combo: str | None
    category_option_combo_name: str | None

    attribute_option_combo: str | None
    attribute_option_combo_name: str | None

    value_raw: str | None
    value_numeric: Decimal | None

    quality_status: str
    quality_reason: str | None

    created_at_source: datetime | None
    last_updated_at_source: datetime | None
