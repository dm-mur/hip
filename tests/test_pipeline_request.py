import pytest

from hip.pipelines.request import PipelineRequest


def test_pipeline_request_stores_execution_arguments():
    request = PipelineRequest(
        endpoint="/api/dataValueSets",
        params={
            "period": "2026-08",
            "dataSet": "TEST_DATASET",
        },
    )

    assert request.endpoint == "/api/dataValueSets"
    assert request.params == {
        "period": "2026-08",
        "dataSet": "TEST_DATASET",
    }


def test_pipeline_request_params_are_optional():
    request = PipelineRequest(
        endpoint="/api/dataValueSets",
    )

    assert request.endpoint == "/api/dataValueSets"
    assert request.params is None


def test_pipeline_request_is_immutable():
    request = PipelineRequest(
        endpoint="/api/dataValueSets",
    )

    with pytest.raises(AttributeError):
        request.endpoint = "/different/endpoint"
