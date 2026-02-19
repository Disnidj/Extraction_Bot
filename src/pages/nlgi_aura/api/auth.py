"""
NLGI Aura Authentication Token Handler
Extracts and manages auth token from browser after login.
Updated to match Orient Aura/Qatar pattern.
"""

import json
from src.utils.logger import nlgi_aura_logger


class NLGIAuraAuthToken:
    """Handles extraction and storage of NLGI Aura auth token."""
    
    def __init__(self):
        self.token = None
    
    async def extract_token_from_browser(self, page):
        """
        Extract auth token from browser storage after login.
        
        Args:
            page: Playwright page object after successful login
            
        Returns:
            str: The extracted JWT token or None if not found
        """
        nlgi_aura_logger.info("Starting token extraction from browser storage...")
        
        try:
            # Try sessionStorage first (NLGI typically stores here)
            nlgi_aura_logger.debug("Checking for token in sessionStorage['token']")
            token = await page.evaluate("sessionStorage.getItem('token')")
            if token:
                self.token = token.strip('"')
                nlgi_aura_logger.info(f"✓ Token found in sessionStorage['token'] (length: {len(self.token)})")
                return self.token
            
            # Try localStorage
            nlgi_aura_logger.debug("Checking for token in localStorage['token']")
            token = await page.evaluate("localStorage.getItem('token')")
            if token:
                self.token = token.strip('"')
                nlgi_aura_logger.info(f"✓ Token found in localStorage['token'] (length: {len(self.token)})")
                return self.token
            
            # Try other common token keys
            token_keys = ["auth_token", "authToken", "access_token", "accessToken", "jwt", "id_token"]
            
            for key in token_keys:
                for storage in ["sessionStorage", "localStorage"]:
                    token = await page.evaluate(f"{storage}.getItem('{key}')")
                    if token:
                        self.token = token.strip('"')
                        nlgi_aura_logger.info(f"✓ Token found in {storage}['{key}'] (length: {len(self.token)})")
                        return self.token
            
            # Check all storage items for JWT-like values
            nlgi_aura_logger.debug("Token not found in common keys, checking all storage items...")
            
            for storage_type in ["sessionStorage", "localStorage"]:
                all_storage = await page.evaluate(f"""
                    () => {{
                        let items = {{}};
                        for (let i = 0; i < {storage_type}.length; i++) {{
                            let key = {storage_type}.key(i);
                            items[key] = {storage_type}.getItem(key);
                        }}
                        return items;
                    }}
                """)
                
                nlgi_aura_logger.debug(f"All {storage_type} keys: {list(all_storage.keys())}")
                
                for key, value in all_storage.items():
                    if value and isinstance(value, str):
                        # JWT tokens have 3 parts separated by dots
                        if value.count('.') == 2 and len(value) > 50:
                            self.token = value.strip('"')
                            nlgi_aura_logger.info(f"✓ JWT token found in {storage_type}['{key}']")
                            return self.token
                        # Check if it's a JSON with token inside
                        try:
                            parsed = json.loads(value)
                            if isinstance(parsed, dict):
                                for tk in ['token', 'access_token', 'accessToken', 'id_token']:
                                    if tk in parsed:
                                        self.token = parsed[tk]
                                        nlgi_aura_logger.info(f"✓ Token found in {storage_type}['{key}'].{tk}")
                                        return self.token
                        except:
                            pass
            
            nlgi_aura_logger.error("❌ Token not found in localStorage or sessionStorage")
            return None
            
        except Exception as e:
            nlgi_aura_logger.error(f"Error extracting token: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_headers(self):
        """
        Get HTTP headers with authorization token for API requests.
        
        Returns:
            dict: Headers dict with Authorization bearer token and NLGI-specific headers
        """
        if not self.token:
            nlgi_aura_logger.error("No token available for headers")
            return {}
        
        return {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "insurerurl": "nlgi",
            "reinsurername": "nlgi-ri",
            "client_code": "null",
            "origin": "https://smehealth.aurainsure.tech",
            "referer": "https://smehealth.aurainsure.tech/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"
        }
