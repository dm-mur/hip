
import pytest

from hip.pipelines.base import BasePipeline


def test_base_pipeline_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BasePipeline()
