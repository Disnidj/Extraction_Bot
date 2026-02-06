"""
Qatar API Client
HTTP client for making API requests to the Aura platform.
"""

import aiohttp
from src.utils.logger import qatar_logger
from .mapping import API_ENDPOINTS


class QatarAPIClient:
    """HTTP client for Qatar Insurance API calls."""
    
    def __init__(self, auth):
        """
        Initialize API client.
        
        Args:
            auth: QatarAuthToken instance with valid token
        """
        self.auth = auth
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self.auth.get_headers())
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_industries(self) -> list:
        """
        Get industry categories.
        
        Returns:
            list: Industry data
        """
        url = API_ENDPOINTS['industry']
        qatar_logger.debug(f"Fetching industries: {url}")
        
        async with self.session.get(url) as response:
            data = await response.json()
            if "response" in data:
                return data.get("response", [])
            else:
                qatar_logger.error(f"Industry API error: {data}")
                return []
    
    async def get_emirates(self, group_id: int) -> list:
        """
        Get emirates list for a group.
        
        Args:
            group_id: The group ID (272 for Qatar)
            
        Returns:
            list: Emirates data
        """
        url = f"{API_ENDPOINTS['emirates']}?groupId={group_id}"
        qatar_logger.debug(f"Fetching emirates: {url}")
        
        async with self.session.get(url) as response:
            data = await response.json()
            if data.get("statusCode") == 200:
                return data.get("response", [])
            else:
                qatar_logger.error(f"Emirates API error: {data}")
                return []
    
    async def get_tpas(self, emirates_id: str) -> list:
        """
        Get TPA list for an emirate.
        
        Args:
            emirates_id: The emirates ID string
            
        Returns:
            list: TPA data
        """
        url = f"{API_ENDPOINTS['tpa']}?emiratesId={emirates_id}"
        qatar_logger.debug(f"Fetching TPAs: {url}")
        
        async with self.session.get(url) as response:
            data = await response.json()
            if data.get("statusCode") == 200:
                return data.get("response", [])
            else:
                qatar_logger.error(f"TPA API error: {data}")
                return []
    
    async def get_plans(self, tpa_id: str) -> list:
        """
        Get plans for a TPA.
        
        Args:
            tpa_id: The TPA ID string
            
        Returns:
            list: Plan data
        """
        url = f"{API_ENDPOINTS['plan']}?tpaId={tpa_id}"
        qatar_logger.debug(f"Fetching plans: {url}")
        
        async with self.session.get(url) as response:
            data = await response.json()
            if data.get("statusCode") == 200:
                return data.get("response", [])
            else:
                qatar_logger.error(f"Plans API error: {data}")
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
        url = f"{API_ENDPOINTS['benefits']}?planId={plan_id}&reinsurerCompanyId={reinsurer_company_id}"
        qatar_logger.debug(f"Fetching benefits: {url}")
        
        async with self.session.get(url) as response:
            data = await response.json()
            if data.get("statusCode") == 200:
                return data.get("response", {})
            else:
                qatar_logger.error(f"Benefits API error: {data}")
                return {}
