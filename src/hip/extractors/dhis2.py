"""
DHIS2 data extractor.

Responsible only for communicating with a DHIS2 instance
and retrieving aggregate data.
"""

from typing import Any

import requests

from hip.config.settings import DHIS2Settings
from hip.extractors.base import BaseExtractor


class DHIS2Extractor(BaseExtractor):
    """Extract aggregate data from a DHIS2 instance."""

    def __init__(self, settings: DHIS2Settings) -> None:
        self.settings = settings

    def extract(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve data from a DHIS2 endpoint.

        Parameters
        ----------
        endpoint:
            DHIS2 API endpoint relative to the base URL.

        params:
            Query parameters for the request.

        Returns
        -------
        dict
            JSON response returned by DHIS2.
        """

        url = f"{self.settings.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        response = requests.get(
            url,
            params=params,
            auth=(self.settings.username, self.settings.password),
            timeout=60,
        )

        response.raise_for_status()

        return response.json()
