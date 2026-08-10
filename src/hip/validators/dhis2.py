"""
DHIS2 record validation.

Validates canonical DHIS2Record objects before they move
to the loading layer.
"""

from dataclasses import dataclass

from hip.models.dhis2 import DHIS2Record
from hip.validators.base import BaseValidator


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating one record."""

    is_valid: bool
    errors: tuple[str, ...] = ()


class DHIS2Validator(BaseValidator):
    """Validate canonical DHIS2 records."""

    REQUIRED_FIELDS = (
        "batch_id",
        "source_instance",
        "data_element",
        "org_unit",
        "period",
    )

    def validate(self, record: DHIS2Record) -> bool:
        """Return True when the record passes validation."""

        return self.validate_with_result(record).is_valid

    def validate_with_result(
        self,
        record: DHIS2Record,
    ) -> ValidationResult:
        """Validate a record and return detailed validation errors."""

        errors: list[str] = []

        for field in self.REQUIRED_FIELDS:
            value = getattr(record, field, None)

            if value is None or str(value).strip() == "":
                errors.append(f"{field} is required")

        if record.record_hash is None or not record.record_hash.strip():
            errors.append("record_hash is required")

        return ValidationResult(
            is_valid=not errors,
            errors=tuple(errors),
        )
