"""
Base validation contract for HIP.

Validators determine whether records are structurally acceptable
for the next stage of the data pipeline.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseValidator(ABC):
    """Abstract base class for all HIP validators."""

    @abstractmethod
    def validate(self, record: Any) -> bool:
        """
        Validate a record.

        Returns
        -------
        bool
            True when the record is valid, otherwise False.
        """
        raise NotImplementedError
