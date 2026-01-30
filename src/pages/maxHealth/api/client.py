"""
MaxHealth API Client
HTTP client to fetch dropdown data from MaxHealth API.
"""

import aiohttp
import ssl
import json
import os
import urllib3
from datetime import datetime, timedelta
from src.utils.logger import maxhealth_logger
from src.utils.load_yaml import MAXHEALTH_GENERATED_CENSUS_DIR

# Suppress SSL warnings (MaxHealth cert has issues on some systems)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MaxHealthAPIClient:
    """HTTP client for MaxHealth API calls."""
    
    BASE_URL = "https://api.maxhealth.ae/api"
    
    def __init__(self, auth):
        """
        Initialize client with auth token.
        
        Args:
            auth: MaxHealthAuthToken instance with valid token
        """
        self.auth = auth
        self.session = None
        # Path to generated census file (with actual member data)
        self.census_file_path = os.path.join(MAXHEALTH_GENERATED_CENSUS_DIR, "MaxHealth.xlsx")
        # Create SSL context that doesn't verify certificates
        # (MaxHealth's certificate has issues on some systems)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def __aenter__(self):
        """Create aiohttp session with SSL bypass."""
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        self.session = aiohttp.ClientSession(
            headers=self.auth.get_headers(),
            connector=connector
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def get_case_lookups(self) -> dict:
        """
        Fetch all dropdown lookups from case-lookups API.
        This single endpoint returns all TPAs, Networks, Regions, Plans, etc.
        
        Returns:
            dict: Complete lookups data
        """
        url = f"{self.BASE_URL}/case/case-lookups"
        
        maxhealth_logger.info(f"Fetching case lookups from {url}")
        print(f"\n📡 Calling API: {url}")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    maxhealth_logger.info("Successfully fetched case lookups")
                    return data
                else:
                    error_text = await response.text()
                    maxhealth_logger.error(f"API error {response.status}: {error_text}")
                    print(f"❌ API Error {response.status}: {error_text[:200]}")
                    return None
        except Exception as e:
            maxhealth_logger.error(f"Request failed: {e}")
            print(f"❌ Request failed: {e}")
            return None
    
    async def get_plans_by_upload(self, network_id: str, product_id: str) -> dict:
        """
        Get plans by uploading census file.
        The plans are returned based on network + product combination.
        
        Args:
            network_id: Network ID (e.g., "1" for MEDNET)
            product_id: Product ID (e.g., "9" for MAXFLEX)
            
        Returns:
            dict: Response with plans data
        """
        import requests
        
        url = f"{self.BASE_URL}/case/upload-census"
        
        # Generate tomorrow's date for policy start
        tomorrow = datetime.now() + timedelta(days=1)
        policy_date = tomorrow.strftime("%Y-%m-%dT00:00:00.000Z")
        
        maxhealth_logger.debug(f"Uploading census for network={network_id}, product={product_id}")
        
        try:
            # Check if census file exists
            if not os.path.exists(self.census_file_path):
                maxhealth_logger.error(f"Census file not found: {self.census_file_path}")
                print(f"   ⚠️ Census file not found: {self.census_file_path}")
                return None
            
            # Use requests library for file upload (more compatible with form-data)
            headers = {
                "Authorization": f"Bearer {self.auth.token}",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://portal.maxhealth.ae",
                "Referer": "https://portal.maxhealth.ae/"
            }
            
            # Form data fields
            form_data = {
                'networkID': str(network_id),
                'productID': str(product_id),
                'targetGroupCategoryID': '0',
                'policyStartDate': policy_date
            }
            
            # File to upload
            files = {
                'files': ('MaxHealth.xlsx', open(self.census_file_path, 'rb'), 
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            response = requests.post(url, headers=headers, data=form_data, files=files, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("isSuccess"):
                    return result
                else:
                    msg = result.get('message', 'Unknown error')
                    maxhealth_logger.warning(f"API returned error: {msg}")
                    print(f"      ⚠️ API error: {msg}")
                    return None
            else:
                maxhealth_logger.error(f"Upload failed {response.status_code}: {response.text[:200]}")
                print(f"      ⚠️ HTTP {response.status_code}: {response.text[:100]}")
                return None
                    
        except Exception as e:
            maxhealth_logger.error(f"Upload census failed: {e}")
            return None
