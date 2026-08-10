import pytest

from hip.loaders.base import BaseLoader


def test_base_loader_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseLoader()
