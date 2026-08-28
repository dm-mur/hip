import pytest

from hip.transformers.base import BaseTransformer


def test_base_transformer_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseTransformer()
