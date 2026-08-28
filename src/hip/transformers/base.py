"""
Base transformation contract for HIP.

Transformers convert source-specific records into
canonical HIP records.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseTransformer(ABC):
    """Abstract base class for all HIP transformers."""

    @abstractmethod
    def transform(
        self,
        record: dict[str, Any],
        context: Any | None = None,
    ) -> Any:
        """
        Transform one source record into a canonical record.

        Parameters
        ----------
        record:
            Source-specific record.

        context:
            Execution context for the current pipeline run.

        Returns
        -------
        Any
            Canonical transformed record.
        """
        raise NotImplementedError