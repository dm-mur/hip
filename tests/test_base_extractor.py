import pytest

from hip.extractors.base import BaseExtractor


def test_base_extractor_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseExtractor()
