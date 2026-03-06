"""
Al Sagr API Client
Handles all HTTP requests to Al Sagr API endpoints.

Main endpoints:
- GetGroupQuotationBenefitStructure: Gets plans, categories, benefit layout
- GetBenefitsByPlan: Gets benefit values for a specific plan

Key Finding:
- Benefits are IDENTICAL across categories for the same plan
- Only ONE API call per plan is needed
"""

import ssl
import aiohttp
from typing import Dict, List, Optional, Any, Union
from src.utils.logger import alsagr_logger
from .mapping import API_BASE_URL, ENDPOINTS, DEFAULT_CATEGORY_ID, PRODUCT_TYPE_SME


class AlSagrAPIClient:
    """
    HTTP client for Al Sagr API requests.
    
    Uses aiohttp with JWT Bearer token authentication.
    All API calls go to https://ndapi.alsagrins.ae/MiCore/api/GroupQuotation/
    """
    
    def __init__(self, auth):
        """
        Initialize API client with auth token.
        
        Args:
            auth: AlSagrAuthToken instance with valid token
        """
        self.auth = auth
        self.base_url = API_BASE_URL
        self.session = None
        self.call_count = 0
    
    async def __aenter__(self):
        """Async context manager entry."""
        # Disable SSL verification for self-signed certificate
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
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
        
        self.call_count += 1
        alsagr_logger.debug(f"API Call #{self.call_count}: GET {url}")
        
        try:
            async with self.session.get(url, headers=self.auth.get_headers()) as response:
                alsagr_logger.debug(f"  Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    alsagr_logger.debug(f"  Response received: {len(str(data))} bytes")
                    return data
                else:
                    text = await response.text()
                    alsagr_logger.error(f"API request failed: {url} - Status: {response.status} - {text[:200]}")
                    return None
        except Exception as e:
            alsagr_logger.error(f"API request error: {url} - {e}")
            return None
    
    async def _post(self, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Optional[Any]:
        """
        Make POST request to API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters dict
            data: POST body data (optional)
            
        Returns:
            JSON response or None on error
        """
        url = f"{self.base_url}{endpoint}"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{param_str}"
        
        self.call_count += 1
        alsagr_logger.debug(f"API Call #{self.call_count}: POST {url}")
        
        try:
            headers = self.auth.get_headers()
            headers["Content-Length"] = "0" if not data else str(len(str(data)))
            
            async with self.session.post(url, headers=headers, json=data if data else None) as response:
                alsagr_logger.debug(f"  Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    alsagr_logger.debug(f"  Response received: {len(str(result))} bytes")
                    return result
                else:
                    text = await response.text()
                    alsagr_logger.error(f"API request failed: {url} - Status: {response.status} - {text[:200]}")
                    return None
        except Exception as e:
            alsagr_logger.error(f"API request error: {url} - {e}")
            return None
    
    async def get_tpa_masters(self, product_type_id: int = PRODUCT_TYPE_SME) -> Optional[List[Dict]]:
        """
        Get TPA (Third Party Administrator) options for a product type.
        
        This is a pre-level API call that should be made before other extractions
        to get the available TPA options.
        
        Args:
            product_type_id: Product type ID (default: 183 for SME)
            
        Returns:
            list: TPA options or None on error
            Example: [
                {"domainValue": 1, "domainValueName": "NEXT CARE MANAGEMENT LLC"},
                {"domainValue": 4, "domainValueName": "NAS ADMINISTRATION SERVICES CO. LLC"}
            ]
        """
        alsagr_logger.info(f"Fetching TPA masters for product type {product_type_id}...")
        
        endpoint = ENDPOINTS["tpa_masters"]
        params = {"productTypeId": product_type_id}
        
        data = await self._post(endpoint, params)
        
        if data and isinstance(data, list):
            alsagr_logger.info(f"  ✓ Got {len(data)} TPA options")
            return data
        
        alsagr_logger.error(f"Failed to get TPA masters for product type {product_type_id}")
        return None
    
    async def get_benefit_structure(self, quotation_id: int) -> Optional[Dict]:
        """
        Get the complete benefit structure for a quotation.
        
        This is the main API that returns:
        - planBenefits[]: Available plans with planId, planName, categoryId, categoryName
        - category[]: Category definitions
        - benefitLayout[]: Layout configuration
        - benefitStructure[]: Benefit field definitions with benefitId
        - proposalMasters[]: Proposal information with proposalId
        
        Args:
            quotation_id: Quotation ID (e.g., 530746)
            
        Returns:
            dict: Full benefit structure response or None on error
        """
        alsagr_logger.info(f"Fetching benefit structure for quotation {quotation_id}...")
        
        endpoint = ENDPOINTS["benefit_structure"]
        params = {"quotationId": quotation_id}
        
        # Use POST instead of GET (API returns 405 for GET)
        data = await self._post(endpoint, params)
        
        if data:
            # Log structure summary
            plan_benefits = data.get("planBenefits", [])
            categories = data.get("category", [])
            benefit_structure = data.get("benefitStructure", [])
            proposal_masters = data.get("proposalMasters", [])
            
            alsagr_logger.info(f"  ✓ Got {len(plan_benefits)} plans, {len(categories)} categories, "
                              f"{len(benefit_structure)} benefit fields, {len(proposal_masters)} proposals")
            
            return data
        
        alsagr_logger.error(f"Failed to get benefit structure for quotation {quotation_id}")
        return None
    
    async def get_benefits_by_plan(
        self, 
        plan_id: int,
        quotation_id: int,
        proposal_id: int,
        category_id: int = DEFAULT_CATEGORY_ID
    ) -> Optional[Dict]:
        """
        Get benefit values for a specific plan.
        
        KEY FINDING: Benefits are IDENTICAL across categories for the same plan.
        So we only need ONE API call per plan, using any categoryId.
        
        Args:
            plan_id: Plan ID (e.g., 882)
            quotation_id: Quotation ID (e.g., 530746)
            proposal_id: Proposal ID from proposalMasters (e.g., 139987)
            category_id: Category ID (default: 2). Any value works since benefits are same.
            
        Returns:
            dict: Benefits response with benefitId -> value mapping, or None on error
        """
        alsagr_logger.debug(f"Fetching benefits for plan {plan_id} (quotation={quotation_id}, proposal={proposal_id})...")
        
        endpoint = ENDPOINTS["benefits_by_plan"]
        params = {
            "planId": plan_id,
            "categoryId": category_id,
            "quotationId": quotation_id,
            "proposalId": proposal_id,
        }
        
        # Use POST instead of GET (API returns 405 for GET)
        data = await self._post(endpoint, params)
        
        if data:
            # Data is a list of benefit objects with benefitId and value fields
            if isinstance(data, list):
                alsagr_logger.debug(f"  ✓ Got {len(data)} benefit values for plan {plan_id}")
            return data
        
        alsagr_logger.error(f"Failed to get benefits for plan {plan_id}")
        return None
    
    async def get_quote_information(self, quotation_id: int) -> Optional[Dict]:
        """
        Get quotation metadata/information.
        
        Uses POST with raw quotation_id in body (not query params).
        
        Args:
            quotation_id: Quotation ID
            
        Returns:
            dict: Quote information including quotationNo, tpaId, branch, etc.
        """
        alsagr_logger.debug(f"Fetching quote information for {quotation_id}...")
        
        endpoint = ENDPOINTS["quote_information"]
        
        return await self._post_raw(endpoint, quotation_id)
    
    async def _post_raw(self, endpoint: str, data: Any) -> Optional[Any]:
        """
        Make POST request with raw data (not JSON object).
        
        Used for GetQuoteInformation which expects raw quotation_id in body.
        
        Args:
            endpoint: API endpoint path
            data: Raw data to send (e.g., quotation_id as integer)
            
        Returns:
            JSON response or None on error
        """
        url = f"{self.base_url}{endpoint}"
        
        self.call_count += 1
        alsagr_logger.debug(f"API Call #{self.call_count}: POST (raw) {url}")
        
        try:
            headers = self.auth.get_headers()
            
            # Send raw data as string
            async with self.session.post(url, headers=headers, data=str(data)) as response:
                alsagr_logger.debug(f"  Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    alsagr_logger.debug(f"  Response received: {len(str(result))} bytes")
                    return result
                else:
                    text = await response.text()
                    alsagr_logger.error(f"API request failed: {url} - Status: {response.status} - {text[:200]}")
                    return None
        except Exception as e:
            alsagr_logger.error(f"API request error: {url} - {e}")
            return None
    
    def get_call_count(self) -> int:
        """
        Get total number of API calls made.
        
        Returns:
            int: Number of API calls
        """
        return self.call_count
