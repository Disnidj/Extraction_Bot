"""
Takaful API Client
Handles all HTTP requests to Takaful API endpoints.
"""

import aiohttp
from src.utils.logger import takaful_logger
from .mapping import API_BASE_URL, ENDPOINTS


class TakafulAPIClient:
    """HTTP client for Takaful API requests."""
    
    def __init__(self, auth):
        """
        Initialize API client with auth token.
        
        Args:
            auth: TakafulAuthToken instance with valid token
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
        
        try:
            async with self.session.get(url, headers=self.auth.get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    takaful_logger.error(f"API request failed: {url} - Status: {response.status}")
                    return None
        except Exception as e:
            takaful_logger.error(f"API request error: {url} - {e}")
            return None
    
    async def get_emirates(self, group_id):
        """
        Fetch emirates for a group.
        
        Args:
            group_id: Group ID (e.g., 31)
            
        Returns:
            list: Emirates data or empty list
        """
        data = await self._get(ENDPOINTS["emirates"], {"groupId": group_id})
        if data:
            return data.get("response", [])
        return []
    
    async def get_tpas(self, emirates_id):
        """
        Fetch TPAs for an emirate.
        
        Args:
            emirates_id: Emirates ID (e.g., "84,84,84...")
            
        Returns:
            list: TPA data or empty list
        """
        data = await self._get(ENDPOINTS["tpa"], {"emiratesId": emirates_id})
        if data:
            return data.get("response", [])
        return []
    
    async def get_industries(self):
        """
        Fetch industry categories (Business Nature).
        
        Returns:
            list: Industry data or empty list
        """
        data = await self._get(ENDPOINTS["industry"])
        if data:
            return data.get("response", [])
        return []
    
    async def get_plans(self, tpa_id):
        """
        Fetch plans for a TPA.
        
        Args:
            tpa_id: TPA ID (e.g., "386")
            
        Returns:
            list: Plans data or empty list
        """
        # API expects repeated tpa_id format
        tpa_param = ",".join([str(tpa_id)] * 5)
        data = await self._get(ENDPOINTS["plan"], {"tpaId": tpa_param})
        if data:
            return data.get("response", [])
        return []
    
    async def get_benefits(self, plan_id, reinsurer_company_id):
        """
        Fetch benefit dropdown values for a plan.
        
        Args:
            plan_id: Plan ID (e.g., 2422)
            reinsurer_company_id: Reinsurer company ID (e.g., 2)
            
        Returns:
            dict: Benefits data or None
        """
        data = await self._get(ENDPOINTS["benefits"], {
            "planId": plan_id,
            "reinsurerCompanyId": reinsurer_company_id
        })
        if data:
            return data.get("response", data)
        return None
