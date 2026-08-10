import pytest

from hip.validators.base import BaseValidator


def test_base_validator_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseValidator()
