"""
Sukoon API Client

Calls the single "Mega API" endpoint that returns all dropdown options.
Uses Playwright page.request to maintain session cookies + F5 tokens.

Unlike ADNIC (14 endpoints), Sukoon uses ONE endpoint:
    POST /GenerateQuotes.aspx/PopulateDDL
    → Returns ALL dropdown options based on indemnityId "master switch"
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from patchright.async_api import Page
from src.utils.logger import sukoon_logger
from .mapping import SUKOON_API_URL, DEFAULT_HEADERS


@dataclass
class DropdownOption:
    """Represents a single dropdown option from API response."""
    text: str          # Display text
    value: str         # Option value
    selected: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "value": self.value,
            "selected": self.selected
        }


class SukoonApiClient:
    """
    HTTP client for Sukoon's PopulateDDL Mega API.
    
    Unlike ADNIC (14 endpoints), Sukoon uses ONE endpoint that returns
    ALL dropdown options based on the indemnityId "master switch".
    
    Example payload:
        {"indemnityId": "4", "regionName": "Dubai", "productId": 1}
    
    Example response:
        {"d": {
            "ProductIndemnity": [...],
            "IndemnityGeographical": [...],
            "IndemnityNetwork": [...],
            "IndemnityDeductible": [...],
            "IndemnityCoinsurance": [...],
            "IndemnityLabXRay": [...],
            ...
        }}
    """
    
    def __init__(self, page: Page):
        """
        Initialize client with authenticated Playwright page.
        
        Args:
            page: Playwright page with active Sukoon session
        """
        self.page = page
        self.api_url = SUKOON_API_URL
        self.call_count = 0
    
    async def call_populate_ddl(
        self,
        indemnity_id: str,
        region_name: str = "Dubai",
        product_id: int = 1
    ) -> Dict[str, List[DropdownOption]]:
        """
        Call the PopulateDDL Mega API.
        
        This single call returns ALL dropdown options for the given indemnityId.
        
        Args:
            indemnity_id: The "master switch" - determines all sub-options
            region_name: Region context (Dubai, Abu Dhabi, etc.)
            product_id: Product type (1 = SME Health)
            
        Returns:
            Dict mapping field names to lists of DropdownOption
        """
        payload = {
            "indemnityId": str(indemnity_id),
            "regionName": region_name,
            "productId": product_id
        }
        
        self.call_count += 1
        
        try:
            # Build headers including cookies from browser context to ensure
            # the API call carries the same session + F5 tokens as the page.
            headers = DEFAULT_HEADERS.copy()
            headers.update({
                "Content-Type": "application/json; charset=UTF-8",
                "Accept": "application/json, text/javascript, */*; q=0.01",
            })

            # Collect cookies for the Sukoon domain and set Cookie header
            try:
                cookies = await self.page.context.cookies()
                cookie_pairs = [f"{c['name']}={c['value']}" for c in cookies if 'sukoon' in c.get('domain', '')]
                if cookie_pairs:
                    headers["Cookie"] = "; ".join(cookie_pairs)
            except Exception:
                # If cookies collection fails, continue without explicit Cookie header
                pass

            sukoon_logger.debug(f"PopulateDDL payload: {payload}")

            response = await self.page.request.post(
                self.api_url,
                data=json.dumps(payload),
                headers=headers
            )

            sukoon_logger.debug(f"PopulateDDL status: {response.status}")

            # Try to parse JSON; record raw for debugging
            try:
                data = await response.json()
            except Exception:
                text = await response.text()
                sukoon_logger.debug(f"PopulateDDL raw response text: {text}")
                data = {}

            # Parse the "d" object containing all dropdown arrays
            d_object = data.get("d", {}) if isinstance(data, dict) else {}

            if isinstance(d_object, str):
                # Sometimes ASP.NET returns JSON as a string
                try:
                    d_object = json.loads(d_object)
                except Exception:
                    sukoon_logger.debug(f"PopulateDDL could not parse d_object string: {d_object}")
                    d_object = {}

            sukoon_logger.debug(f"PopulateDDL d_object keys: {list(d_object.keys())}")

            return self._parse_response(d_object)

        except Exception as e:
            sukoon_logger.error(f"PopulateDDL API Error: {e}")
            print(f"   ❌ API Error: {e}")
            return {}
    
    def _parse_response(self, d_object: Dict) -> Dict[str, List[DropdownOption]]:
        """
        Parse the API response into organized dropdown options.
        
        Args:
            d_object: The "d" object from API response
            
        Returns:
            Dict mapping field keys to lists of DropdownOption
        """
        result = {}
        
        # Expected fields in response
        field_keys = [
            "ProductIndemnity",
            "IndemnityGeographical",
            "IndemnityNetwork",
            "IndemnityDeductible",
            "IndemnityCoinsurance",
            "IndemnityLabXRay",
            "IndemnityNetworkEP",
            "IndemnityCoinsuranceEP"
        ]
        
        for key in field_keys:
            if key in d_object:
                options = []
                items = d_object[key]
                
                # Log when items are present but seem empty
                if isinstance(items, list) and len(items) > 0:
                    sample = items[:3]
                    sukoon_logger.debug(f"Parsing {key}: first items sample: {sample}")

                if isinstance(items, list):
                    # Field-specific key mapping for Sukoon responses
                    field_key_map = {
                        "ProductIndemnity": ("IndemnityName", "IndemnityID"),
                        "IndemnityGeographical": ("GeographicalAreaName", "GeographicalAreaID"),
                        "IndemnityNetwork": ("NetworkName", "NetworkID"),
                        "IndemnityDeductible": ("DeductibleName", "DeductibleID"),
                        "IndemnityCoinsurance": ("CoinsuranceName", "CoinsuranceID"),
                        "IndemnityLabXRay": ("LabXRayName", "LabXRayID"),
                        "IndemnityNetworkEP": ("NetworkName", "NetworkID"),
                        "IndemnityCoinsuranceEP": ("CoinsuranceName", "CoinsuranceID"),
                        "IndemnityPharmacy": ("PharmacyName", "PharmacyID"),
                        "IndemnityConsultation": ("ConsultationName", "ConsultationID"),
                    }

                    for item in items:
                        # Handle different response formats
                        if isinstance(item, dict):
                            # Try field-specific keys first
                            text_key, value_key = field_key_map.get(key, (None, None))

                            text_val = None
                            value_val = None

                            if text_key:
                                text_val = item.get(text_key)
                            if value_key:
                                value_val = item.get(value_key)

                            # Fallbacks if specific keys not present
                            if not text_val:
                                text_val = (
                                    item.get("Text") or item.get("text") or
                                    item.get("Name") or item.get("Label") or
                                    item.get("Description") or ""
                                )

                            if not value_val:
                                value_val = (
                                    item.get("Value") or item.get("value") or
                                    item.get("ID") or item.get("Code") or text_val
                                )

                            selected_val = (
                                item.get("Selected") or item.get("selected") or
                                item.get("IsDefault") or item.get("isDefault") or False
                            )

                            # Normalize and append
                            text_norm = str(text_val) if text_val is not None else ""
                            value_norm = str(value_val) if value_val is not None else ""

                            options.append(DropdownOption(
                                text=text_norm,
                                value=value_norm,
                                selected=bool(selected_val)
                            ))
                        elif isinstance(item, str):
                            options.append(DropdownOption(text=item, value=item))
                        else:
                            # Unknown item shape — log it
                            sukoon_logger.debug(f"Unknown item type for {key}: {item}")

                    # After parsing, log a summary of parsed options
                    if options:
                        sample_parsed = [opt.to_dict() for opt in options[:5]]
                        sukoon_logger.debug(f"Parsed {key}: count={len(options)}, sample={sample_parsed}")
                else:
                    # Not a list — log for debugging
                    sukoon_logger.debug(f"Unexpected type for {key}: {type(items)}")
                
                result[key] = options
        
        return result
    
    async def get_indemnity_options(self, region_name: str = "Dubai") -> List[DropdownOption]:
        """
        Get the master list of Indemnity Limit options.
        
        These are the "master switch" values used to drive all other dropdowns.
        Call with indemnityId='0' or empty to get the initial list.
        
        Args:
            region_name: Region context
            
        Returns:
            List of indemnity limit options
        """
        # First call with empty/zero to get initial indemnity list
        result = await self.call_populate_ddl(
            indemnity_id="0",  # Initial call to get indemnity list
            region_name=region_name
        )
        
        return result.get("ProductIndemnity", [])
    
    def get_stats(self) -> Dict:
        """Get API call statistics."""
        return {
            "total_api_calls": self.call_count
        }
