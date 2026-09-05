"""
Base loading contract for HIP.

Loaders are responsible for persisting validated records
into a target data store.
"""

from abc import ABC, abstractmethod
from typing import Any

from hip.loaders.result import LoadResult


class BaseLoader(ABC):
    """Abstract base class for all HIP loaders."""

    @abstractmethod
    def load(self, records: list[Any]) -> LoadResult:
        """
        Load records into the target system.

        Parameters
        ----------
        records:
            Records that have already passed validation.

        Returns
        -------
        LoadResult
            Structured outcome of the loading operation.
        """
        raise NotImplementedError