"""
Liva Insurance API Client

HTTP client for making API calls to Liva Insurance cascading dropdown endpoints.
Uses Playwright page.request to maintain session cookies.

API Base URL: https://health.livainsurance.ae/Portal/Eng/Services/SMEservice.asmx
Payload format: {"knownCategoryValues": "tpa:VALUE;region:VALUE;nw:VALUE;", "category": "CategoryName"}
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from patchright.async_api import Page
from src.utils.logger import liva_insurance_logger
from .mapping import LIVA_API_BASE_URL


@dataclass
class DropdownOption:
    """Represents a single dropdown option from API response."""
    name: str
    value: str
    is_default: bool = False

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "is_default": self.is_default
        }


class LivaInsuranceApiClient:
    """
    HTTP client for Liva Insurance API calls.

    Uses Playwright page.request to maintain session cookies
    established during the login/census upload flow.
    """

    def __init__(self, page: Page):
        self.page = page
        self.base_url = LIVA_API_BASE_URL
        self.call_count = 0

    def _build_known_values(self, dependencies: Dict[str, str]) -> str:
        """
        Build the knownCategoryValues string for cascading dropdowns.

        Format: "tpa:TPA3;region:DXB / NE;nw:N7;"
        Uses lowercase keys as required by the Liva Insurance API.
        """
        if not dependencies:
            return ""
        return "".join(f"{k}:{v};" for k, v in dependencies.items())

    async def call_api(
        self,
        endpoint: str,
        category: str,
        known_values: Optional[Dict[str, str]] = None
    ) -> List[DropdownOption]:
        """
        Make an API call to fetch dropdown options.

        Args:
            endpoint: API endpoint name (e.g., "GetDropDownTPA")
            category: Category parameter for the API
            known_values: Dependencies as {key: value} dict

        Returns:
            List of DropdownOption objects
        """
        url = f"{self.base_url}/{endpoint}"
        known_str = self._build_known_values(known_values or {})

        payload = {
            "knownCategoryValues": known_str,
            "category": category
        }

        self.call_count += 1

        liva_insurance_logger.debug(f"API Call #{self.call_count}: {endpoint}")
        liva_insurance_logger.debug(f"  Category: {category}")
        liva_insurance_logger.debug(f"  Dependencies: {known_str if known_str else 'None'}")

        try:
            response = await self.page.request.post(
                url,
                data=json.dumps(payload),
                headers={
                    "Content-Type": "application/json; charset=UTF-8",
                    "Accept": "*/*",
                }
            )

            data = await response.json()

            options = [
                DropdownOption(
                    name=item.get("name", ""),
                    value=item.get("value", ""),
                    is_default=item.get("isDefaultValue", False)
                )
                for item in data.get("d", [])
            ]

            liva_insurance_logger.debug(f"  Response: {len(options)} options received")
            if options:
                liva_insurance_logger.debug(f"  Sample: {options[0].name} (value={options[0].value})")

            return options

        except Exception as e:
            liva_insurance_logger.error(f"API Error {endpoint}: {e}")
            return []

    async def get_independent_options(self, endpoint: str, category: str) -> List[DropdownOption]:
        """Fetch options for independent (Level 0) dropdowns - TPA."""
        return await self.call_api(endpoint, category)

    async def get_tpa_dependent_options(
        self, endpoint: str, category: str, tpa_value: str
    ) -> List[DropdownOption]:
        """Fetch options dependent on TPA (Level 1) - Region."""
        return await self.call_api(endpoint, category, {"tpa": tpa_value})

    async def get_region_dependent_options(
        self, endpoint: str, category: str, tpa_value: str, region_value: str
    ) -> List[DropdownOption]:
        """Fetch options dependent on TPA + Region (Level 2) - Network."""
        return await self.call_api(endpoint, category, {"tpa": tpa_value, "region": region_value})

    async def get_network_dependent_options(
        self, endpoint: str, category: str,
        tpa_value: str, region_value: str, network_value: str
    ) -> List[DropdownOption]:
        """Fetch options dependent on TPA + Region + Network (Level 3) - Benefit fields."""
        return await self.call_api(
            endpoint, category,
            {"tpa": tpa_value, "region": region_value, "nw": network_value}
        )

    async def get_annual_limit_dependent_options(
        self, endpoint: str, category: str,
        tpa_value: str, region_value: str, network_value: str, al_value: str
    ) -> List[DropdownOption]:
        """Fetch options dependent on TPA + Region + Network + Annual Limit (Level 4) - Dental Limit."""
        return await self.call_api(
            endpoint, category,
            {"tpa": tpa_value, "region": region_value, "nw": network_value, "al": al_value}
        )

    async def get_dental_limit_dependent_options(
        self, endpoint: str, category: str,
        tpa_value: str, region_value: str, network_value: str,
        al_value: str, dental_lim_value: str
    ) -> List[DropdownOption]:
        """Fetch options dependent on TPA+Region+Network+AL+DentalLim (Level 5) - Dental Copay."""
        return await self.call_api(
            endpoint, category,
            {"tpa": tpa_value, "region": region_value, "nw": network_value,
             "al": al_value, "dentalLim": dental_lim_value}
        )

    def get_stats(self) -> Dict:
        """Get client statistics."""
        return {"total_api_calls": self.call_count}
