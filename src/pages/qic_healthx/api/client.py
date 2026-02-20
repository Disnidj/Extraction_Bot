"""
QIC HealthX API Client
HTTP client for making API requests to QIC HealthX (wellx.ai) platform.
"""

import aiohttp
from src.utils.logger import qic_healthx_logger
from .mapping import API_BASE_URL, ENDPOINTS, DEFAULT_PLANS_PARAMS, DUBAI_FILTER_KEYWORD


class QICHealthXAPIClient:
    """HTTP client for QIC HealthX API calls."""
    
    def __init__(self, auth):
        """
        Initialize API client.
        
        Args:
            auth: QICHealthXAuthToken instance with valid token
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
        
        qic_healthx_logger.debug(f"API Request: GET {url}")
        if params:
            qic_healthx_logger.debug(f"  Params: {params}")
        
        try:
            async with self.session.get(
                url, 
                headers=self.auth.get_headers(),
                params=params
            ) as response:
                qic_healthx_logger.debug(f"  Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    qic_healthx_logger.debug(f"  Response received: {len(str(data))} bytes")
                    return data
                else:
                    text = await response.text()
                    qic_healthx_logger.error(f"API request failed: {url} - Status: {response.status} - {text[:200]}")
                    return None
        except Exception as e:
            qic_healthx_logger.error(f"API request error: {url} - {e}")
            return None
    
    async def get_all_plans(self) -> list:
        """
        Fetch all published plans for the product.
        
        Returns:
            list: List of plan objects or empty list
        """
        qic_healthx_logger.info("Fetching all plans from API...")
        
        data = await self._get(ENDPOINTS["plans"], params=DEFAULT_PLANS_PARAMS)
        
        if data and "data" in data:
            plans = data["data"]
            qic_healthx_logger.info(f"✓ Fetched {len(plans)} total plans from API")
            return plans
        
        qic_healthx_logger.error("Failed to fetch plans or no data in response")
        return []
    
    async def get_dubai_plans(self) -> list:
        """
        Fetch all plans and filter to Dubai only.
        
        Returns:
            list: List of Dubai plan objects
        """
        all_plans = await self.get_all_plans()
        
        if not all_plans:
            return []
        
        # Filter to only Dubai plans
        dubai_plans = [
            plan for plan in all_plans
            if DUBAI_FILTER_KEYWORD.lower() in plan.get("name", "").lower()
        ]
        
        qic_healthx_logger.info(f"✓ Filtered to {len(dubai_plans)} Dubai plans")
        
        # Log plan names
        for plan in dubai_plans:
            qic_healthx_logger.debug(f"  - {plan.get('name')}")
        
        return dubai_plans
