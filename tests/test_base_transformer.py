import pytest

from hip.pipelines.context import PipelineContext
from hip.transformers.base import BaseTransformer


def test_base_transformer_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseTransformer()


def test_base_transformer_receives_pipeline_context():
    class DummyTransformer(BaseTransformer):
        def transform(self, record, context):
            return {
                "record": record,
                "batch_id": context.batch_id,
            }

    transformer = DummyTransformer()

    context = PipelineContext(
        batch_id="batch-001",
        environment="TEST",
        initiated_by="pytest",
    )

    result = transformer.transform(
        {"id": "record-001"},
        context=context,
    )

    assert result["record"] == {"id": "record-001"}
    assert result["batch_id"] == "batch-001"