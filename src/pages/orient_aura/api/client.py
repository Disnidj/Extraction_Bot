"""
Orient Aura API Client
Handles all HTTP requests to Orient Aura API endpoints.
"""

import aiohttp
from src.utils.logger import orient_aura_logger
from .mapping import API_BASE_URL, ENDPOINTS


class OrientAuraAPIClient:
    """HTTP client for Orient Aura API requests."""
    
    def __init__(self, auth):
        """
        Initialize API client with auth token.
        
        Args:
            auth: OrientAuraAuthToken instance with valid token
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
        
        orient_aura_logger.debug(f"API Request: GET {url}")
        
        try:
            async with self.session.get(url, headers=self.auth.get_headers()) as response:
                orient_aura_logger.debug(f"  Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    orient_aura_logger.debug(f"  Response received: {len(str(data))} bytes")
                    return data
                else:
                    text = await response.text()
                    orient_aura_logger.error(f"API request failed: {url} - Status: {response.status} - {text[:200]}")
                    return None
        except Exception as e:
            orient_aura_logger.error(f"API request error: {url} - {e}")
            return None
    
    async def get_industries(self):
        """
        Fetch industry categories (Business Nature).
        
        Pre-Level API: Called before any other endpoints.
        
        Returns:
            list: Industry data or empty list
        """
        orient_aura_logger.debug("Fetching industries...")
        data = await self._get(ENDPOINTS["industry"])
        if data:
            industries = data.get("response", [])
            orient_aura_logger.debug(f"Found {len(industries)} industries")
            return industries
        return []
    
    async def get_groups(self, version_id=44):
        """
        Fetch available groups for Orient portal.
        
        This is Orient-specific - not present in Takaful/Qatar.
        
        Args:
            version_id: Version ID (default: 44)
            
        Returns:
            list: Group data or empty list
        """
        endpoint = ENDPOINTS["group"].format(version_id=version_id)
        orient_aura_logger.debug(f"Fetching groups for version {version_id}...")
        data = await self._get(endpoint)
        if data:
            groups = data.get("response", [])
            orient_aura_logger.debug(f"Found {len(groups)} groups")
            return groups
        return []
    
    async def get_emirates(self, group_id):
        """
        Fetch emirates for a specific group.
        
        Args:
            group_id: Group ID (e.g., 173 for Nextcare Sme)
            
        Returns:
            list: Emirates data or empty list
        """
        orient_aura_logger.debug(f"Fetching emirates for group {group_id}...")
        data = await self._get(ENDPOINTS["emirates"], {"groupId": group_id})
        if data:
            emirates = data.get("response", [])
            orient_aura_logger.debug(f"Found {len(emirates)} emirates")
            return emirates
        return []
    
    async def get_tpas(self, emirates_id):
        """
        Fetch TPAs for an emirate.
        
        Args:
            emirates_id: Emirates ID (e.g., "501,501,501..." for Dubai)
            
        Returns:
            list: TPA data or empty list
        """
        orient_aura_logger.debug(f"Fetching TPAs for emirates_id {emirates_id[:50]}...")
        data = await self._get(ENDPOINTS["tpa"], {"emiratesId": emirates_id})
        if data:
            tpas = data.get("response", [])
            orient_aura_logger.debug(f"Found {len(tpas)} TPAs")
            return tpas
        return []
    
    async def get_plans(self, tpa_id):
        """
        Fetch plans for a TPA.
        
        Args:
            tpa_id: TPA ID (e.g., "500,500,500..." for Nextcare)
            
        Returns:
            list: Plan data or empty list
        """
        orient_aura_logger.debug(f"Fetching plans for tpa_id {tpa_id[:50]}...")
        data = await self._get(ENDPOINTS["plan"], {"tpaId": tpa_id})
        if data:
            plans = data.get("response", [])
            orient_aura_logger.debug(f"Found {len(plans)} plans")
            return plans
        return []
    
    async def get_benefits(self, plan_id, reinsurer_company_id):
        """
        Fetch benefits/dropdown options for a plan.
        
        Args:
            plan_id: Plan ID (e.g., 5746)
            reinsurer_company_id: Reinsurer company ID (e.g., 22)
            
        Returns:
            dict: Benefits data keyed by benefit header ID, or empty dict
        """
        orient_aura_logger.debug(f"Fetching benefits for plan {plan_id}, reinsurer {reinsurer_company_id}...")
        data = await self._get(
            ENDPOINTS["benefits"], 
            {
                "planId": plan_id,
                "reinsurerCompanyId": reinsurer_company_id
            }
        )
        if data and "response" in data:
            benefits = data["response"]
            benefit_count = len(benefits) if isinstance(benefits, dict) else 0
            orient_aura_logger.debug(f"Found {benefit_count} benefit categories")
            return benefits
        return {}
