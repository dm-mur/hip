from decimal import Decimal, InvalidOperation

from hip.models.silver import SilverDHIS2Observation


class SilverDHIS2Transformer:
    def transform(
        self,
        record: dict,
    ) -> SilverDHIS2Observation:
        required_fields = (
            "bronze_id",
            "batch_id",
            "source_system",
            "source_instance",
            "data_element",
            "org_unit",
            "period",
        )

        for field in required_fields:
            if record.get(field) in (None, ""):
                raise ValueError(f"{field} is required")

        value_raw = record.get("value")

        value_numeric = None
        quality_status = "VALID"
        quality_reason = None

        if value_raw is not None:
            try:
                value_numeric = Decimal(str(value_raw))
            except InvalidOperation:
                quality_status = "NON_NUMERIC"
                quality_reason = "Value could not be parsed as numeric"

        return SilverDHIS2Observation(
            bronze_id=record["bronze_id"],
            batch_id=record["batch_id"],
            source_system=record["source_system"],
            source_instance=record["source_instance"],
            dataset_id=record.get("dataset_id"),
            data_element=record["data_element"],
            data_element_name=record.get("data_element_name"),
            org_unit=record["org_unit"],
            org_unit_name=record.get("org_unit_name"),
            period=record["period"],
            category_option_combo=record.get("category_option_combo"),
            category_option_combo_name=record.get(
                "category_option_combo_name"
            ),
            attribute_option_combo=record.get(
                "attribute_option_combo"
            ),
            attribute_option_combo_name=record.get(
                "attribute_option_combo_name"
            ),
            value_raw=value_raw,
            value_numeric=value_numeric,
            quality_status=quality_status,
            quality_reason=quality_reason,
            created_at_source=record.get("created_at_source"),
            last_updated_at_source=record.get(
                "last_updated_at_source"
            ),
        )
