"""
Base loading contract for HIP.

Loaders are responsible for persisting validated records
into a target data store.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseLoader(ABC):
    """Abstract base class for all HIP loaders."""

    @abstractmethod
    def load(self, records: list[Any]) -> int:
        """
        Load records into the target system.

        Parameters
        ----------
        records:
            Records that have already passed validation.

        Returns
        -------
        int
            Number of records successfully loaded.
        """
        raise NotImplementedError
