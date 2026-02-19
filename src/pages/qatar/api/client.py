"""
Qatar API Client
HTTP client for making API requests to the Aura platform.
Updated to follow Orient Aura pattern with dynamic API calls.
"""

import aiohttp
from src.utils.logger import qatar_logger
from .mapping import API_BASE_URL, ENDPOINTS, CUSTOM_HEADERS


class QatarAPIClient:
    """HTTP client for Qatar Insurance API calls."""
    
    def __init__(self, auth):
        """
        Initialize API client.
        
        Args:
            auth: QatarAuthToken instance with valid token
        """
        self.auth = auth
        self.base_url = API_BASE_URL
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_headers(self):
        """Get headers combining auth + custom headers."""
        headers = self.auth.get_headers()
        headers.update(CUSTOM_HEADERS)
        return headers
    
    async def _get(self, endpoint, params=None):
        """
        Make GET request to API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters dict
            
        Returns:
            dict: JSON response or None on error
        """
        url = f"{self.base_url}{endpoint}"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{param_str}"
        
        qatar_logger.debug(f"API Request: GET {url}")
        
        try:
            async with self.session.get(url, headers=self._get_headers()) as response:
                qatar_logger.debug(f"  Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    qatar_logger.debug(f"  Response received: {len(str(data))} bytes")
                    return data
                else:
                    text = await response.text()
                    qatar_logger.error(f"API request failed: {url} - Status: {response.status} - {text[:200]}")
                    return None
        except Exception as e:
            qatar_logger.error(f"API request error: {url} - {e}")
            return None
    
    async def get_industries(self) -> list:
        """
        Get industry categories (Business Nature).
        
        Returns:
            list: Industry data
        """
        qatar_logger.debug("Fetching industries...")
        data = await self._get(ENDPOINTS["industry"])
        if data:
            industries = data.get("response", [])
            qatar_logger.debug(f"Found {len(industries)} industries")
            return industries
        return []
    
    async def get_groups(self, version_id=50):
        """
        Fetch available groups for Qatar portal.
        
        Args:
            version_id: Version ID (default: 50 for Qatar)
            
        Returns:
            list: Group data or empty list
        """
        endpoint = ENDPOINTS["group"].format(version_id=version_id)
        qatar_logger.debug(f"Fetching groups for version {version_id}...")
        data = await self._get(endpoint)
        if data:
            groups = data.get("response", [])
            qatar_logger.debug(f"Found {len(groups)} groups")
            return groups
        return []
    
    async def get_emirates(self, group_id: int) -> list:
        """
        Get emirates list for a group.
        
        Args:
            group_id: The group ID (281 for SME NAS)
            
        Returns:
            list: Emirates data
        """
        qatar_logger.debug(f"Fetching emirates for group {group_id}...")
        data = await self._get(ENDPOINTS["emirates"], {"groupId": group_id})
        if data:
            emirates = data.get("response", [])
            qatar_logger.debug(f"Found {len(emirates)} emirates")
            return emirates
        return []
    
    async def get_tpas(self, emirates_id: str) -> list:
        """
        Get TPA list for an emirate.
        
        Args:
            emirates_id: The emirates ID string
            
        Returns:
            list: TPA data
        """
        qatar_logger.debug(f"Fetching TPAs for emirates_id {emirates_id[:50]}...")
        data = await self._get(ENDPOINTS["tpa"], {"emiratesId": emirates_id})
        if data:
            tpas = data.get("response", [])
            qatar_logger.debug(f"Found {len(tpas)} TPAs")
            return tpas
        return []
    
    async def get_plans(self, tpa_id: str) -> list:
        """
        Get plans for a TPA.
        
        Args:
            tpa_id: The TPA ID string
            
        Returns:
            list: Plan data
        """
        qatar_logger.debug(f"Fetching plans for tpa_id {tpa_id[:50]}...")
        data = await self._get(ENDPOINTS["plan"], {"tpaId": tpa_id})
        if data:
            plans = data.get("response", [])
            qatar_logger.debug(f"Found {len(plans)} plans")
            return plans
        return []
    
    async def get_benefits(self, plan_id: int, reinsurer_company_id: int) -> dict:
        """
        Get all benefit dropdowns for a plan.
        
        Args:
            plan_id: The plan ID
            reinsurer_company_id: The reinsurer company ID
            
        Returns:
            dict: Benefits data with all dropdown options
        """
        qatar_logger.debug(f"Fetching benefits for plan {plan_id}...")
        data = await self._get(
            ENDPOINTS["benefits"], 
            {"planId": plan_id, "reinsurerCompanyId": reinsurer_company_id}
        )
        if data:
            benefits = data.get("response", {})
            qatar_logger.debug(f"Found {len(benefits)} benefit fields")
            return benefits
        return {}
