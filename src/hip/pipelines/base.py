"""
Base pipeline orchestration for HIP.

A pipeline coordinates extraction, transformation,
validation and loading without containing source-specific
or destination-specific logic.
"""

from abc import ABC, abstractmethod
from typing import Any

from hip.extractors.base import BaseExtractor
from hip.loaders.base import BaseLoader
from hip.transformers.base import BaseTransformer
from hip.validators.base import BaseValidator


class BasePipeline(ABC):
    """Abstract base class for HIP data pipelines."""

    def __init__(
        self,
        extractor: BaseExtractor,
        transformer: BaseTransformer,
        validator: BaseValidator,
        loader: BaseLoader,
    ) -> None:
        self.extractor = extractor
        self.transformer = transformer
        self.validator = validator
        self.loader = loader

    @abstractmethod
    def run(self, **kwargs: Any) -> int:
        """
        Execute the pipeline.

        Returns
        -------
        int
            Number of records successfully loaded.
        """
        raise NotImplementedError
