from unittest.mock import Mock, patch

from hip.config.settings import DHIS2Settings
from hip.extractors.dhis2 import DHIS2Extractor
from hip.pipelines.request import PipelineRequest


def test_dhis2_extractor_returns_json():
    settings = DHIS2Settings(
        base_url="https://dhis2.example.org",
        username="test_user",
        password="test_password",
    )

    extractor = DHIS2Extractor(settings)

    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [
            {
                "dataElement": "DE001",
                "orgUnit": "OU001",
                "period": "202608",
                "value": "100",
            }
        ]
    }

    with patch(
        "hip.extractors.dhis2.requests.get",
        return_value=mock_response,
    ) as mock_get:

        request = PipelineRequest(
            endpoint="/api/dataValueSets",
            params={"period": "202608"},
        )

        result = extractor.extract(request)

    mock_get.assert_called_once_with(
        "https://dhis2.example.org/api/dataValueSets",
        params={"period": "202608"},
        auth=("test_user", "test_password"),
        timeout=60,
    )

    mock_response.raise_for_status.assert_called_once()

    assert result["data"][0]["dataElement"] == "DE001"
    assert result["data"][0]["value"] == "100"
