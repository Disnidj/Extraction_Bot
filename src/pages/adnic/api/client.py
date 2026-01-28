"""
ADNIC API Client

HTTP client for making API calls to ADNIC cascading dropdown endpoints.
Uses Playwright page.request to maintain session cookies.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from patchright.async_api import Page
from src.utils.logger import adnic_logger
from .mapping import ADNIC_API_BASE_URL, DEFAULT_HEADERS


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


class ADNICApiClient:
    """
    HTTP client for ADNIC API calls.
    
    Uses Playwright page.request to maintain session cookies
    established during the login/census upload flow.
    """
    
    def __init__(self, page: Page):
        """
        Initialize client with authenticated Playwright page.
        
        Args:
            page: Playwright page with active ADNIC session
        """
        self.page = page
        self.base_url = ADNIC_API_BASE_URL
        self.call_count = 0
    
    def _build_known_values(self, dependencies: Dict[str, str]) -> str:
        """
        Build the knownCategoryValues string for cascading dropdowns.
        
        Format: "TPA:TPA9;Plan:438;TCover:1;"
        
        Args:
            dependencies: Dict of {category: value} pairs
            
        Returns:
            Formatted string for API payload
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
            endpoint: API endpoint name (e.g., "GetTPAByProduct")
            category: Category parameter for the API
            known_values: Dependencies as {category: value} dict
            
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
        
        try:
            response = await self.page.request.post(
                url,
                data=json.dumps(payload),
                headers={
                    "Content-Type": "application/json; charset=UTF-8",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
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
            
            return options
            
        except Exception as e:
            adnic_logger.error(f"API Error {endpoint}: {e}")
            return []
    
    async def get_independent_options(self, endpoint: str, category: str) -> List[DropdownOption]:
        """
        Fetch options for independent (Level 0) dropdowns.
        
        Args:
            endpoint: API endpoint
            category: Category parameter
            
        Returns:
            List of dropdown options
        """
        return await self.call_api(endpoint, category)
    
    async def get_tpa_dependent_options(
        self, 
        endpoint: str, 
        category: str, 
        tpa_value: str
    ) -> List[DropdownOption]:
        """
        Fetch options dependent on TPA (Level 1).
        
        Args:
            endpoint: API endpoint
            category: Category parameter
            tpa_value: Selected TPA value
            
        Returns:
            List of dropdown options
        """
        return await self.call_api(endpoint, category, {"TPA": tpa_value})
    
    async def get_network_dependent_options(
        self,
        endpoint: str,
        category: str,
        tpa_value: str,
        network_value: str
    ) -> List[DropdownOption]:
        """
        Fetch options dependent on TPA + Network (Level 2).
        
        Args:
            endpoint: API endpoint
            category: Category parameter
            tpa_value: Selected TPA value
            network_value: Selected Network/Plan value
            
        Returns:
            List of dropdown options
        """
        return await self.call_api(
            endpoint, 
            category, 
            {"TPA": tpa_value, "Plan": network_value}
        )
    
    async def get_tcover_dependent_options(
        self,
        endpoint: str,
        category: str,
        tpa_value: str,
        network_value: str,
        tcover_value: str
    ) -> List[DropdownOption]:
        """
        Fetch options dependent on TPA + Network + TCover (Level 3).
        
        Args:
            endpoint: API endpoint
            category: Category parameter
            tpa_value: Selected TPA value
            network_value: Selected Network/Plan value
            tcover_value: Selected Territorial Cover value
            
        Returns:
            List of dropdown options
        """
        return await self.call_api(
            endpoint,
            category,
            {"TPA": tpa_value, "Plan": network_value, "TCover": tcover_value}
        )
    
    def get_stats(self) -> Dict:
        """Get API call statistics."""
        return {
            "total_api_calls": self.call_count
        }
