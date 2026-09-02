"""
Base extractor interface for HIP.

Extractors are responsible for retrieving data from external
source systems and returning it in a form that can be passed
to the validation and transformation layers.
"""

from abc import ABC, abstractmethod
from typing import Any
from hip.pipelines.request import PipelineRequest


class BaseExtractor(ABC):
    """
    Abstract base class for all HIP data extractors.

    A concrete extractor must implement the `extract` method.
    """

    @abstractmethod
    def extract(self, request: PipelineRequest) -> Any:
        """
        Extract data from the source system.

        Returns
        -------
        Any
            Data retrieved from the source system.

        Raises
        ------
        NotImplementedError
            Raised by concrete implementations that do not
            implement this method.
        """
        raise NotImplementedError
