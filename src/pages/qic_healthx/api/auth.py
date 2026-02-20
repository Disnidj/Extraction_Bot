"""
QIC HealthX Authentication Token Handler
Extracts and manages auth token from browser after login.
"""

import json
from src.utils.logger import qic_healthx_logger


class QICHealthXAuthToken:
    """Handles extraction and storage of QIC HealthX auth token."""
    
    def __init__(self):
        self.token = None
    
    async def extract_token_from_browser(self, page):
        """
        Extract auth token from browser storage after login.
        QIC HealthX uses JWT Bearer token stored in localStorage or sessionStorage.
        
        Args:
            page: Playwright page object after successful login
            
        Returns:
            str: The extracted JWT token or None if not found
        """
        qic_healthx_logger.info("Starting token extraction from browser storage...")
        
        try:
            # Try localStorage first
            qic_healthx_logger.debug("Checking localStorage for auth token...")
            token = await page.evaluate("localStorage.getItem('token')")
            if token:
                self.token = token.strip('"')
                qic_healthx_logger.info(f"✓ Token found in localStorage['token'] (length: {len(self.token)})")
                return self.token
            
            # Try sessionStorage
            qic_healthx_logger.debug("Checking sessionStorage for auth token...")
            token = await page.evaluate("sessionStorage.getItem('token')")
            if token:
                self.token = token.strip('"')
                qic_healthx_logger.info(f"✓ Token found in sessionStorage['token'] (length: {len(self.token)})")
                return self.token
            
            # Try other common token keys
            token_keys = [
                "auth_token", "authToken", "access_token", "accessToken",
                "jwt", "id_token", "bearerToken", "Authorization"
            ]
            
            for key in token_keys:
                for storage in ["localStorage", "sessionStorage"]:
                    token = await page.evaluate(f"{storage}.getItem('{key}')")
                    if token:
                        self.token = token.strip('"')
                        qic_healthx_logger.info(f"✓ Token found in {storage}['{key}'] (length: {len(self.token)})")
                        return self.token
            
            # Check all storage items for JWT-like values
            qic_healthx_logger.debug("Token not found in common keys, checking all storage items...")
            
            for storage_type in ["localStorage", "sessionStorage"]:
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
                
                qic_healthx_logger.debug(f"All {storage_type} keys: {list(all_storage.keys())}")
                
                for key, value in all_storage.items():
                    if value and isinstance(value, str):
                        # JWT tokens have 3 parts separated by dots
                        if value.count('.') == 2 and len(value) > 50:
                            self.token = value.strip('"')
                            qic_healthx_logger.info(f"✓ JWT token found in {storage_type}['{key}']")
                            return self.token
                        
                        # Check if it's a JSON object containing a token
                        try:
                            parsed = json.loads(value)
                            if isinstance(parsed, dict):
                                for tk in token_keys:
                                    if tk in parsed and parsed[tk]:
                                        self.token = str(parsed[tk]).strip('"')
                                        qic_healthx_logger.info(f"✓ Token found in {storage_type}['{key}'].{tk}")
                                        return self.token
                        except (json.JSONDecodeError, TypeError):
                            pass
            
            qic_healthx_logger.error("No auth token found in browser storage")
            return None
            
        except Exception as e:
            qic_healthx_logger.error(f"Token extraction error: {e}")
            return None
    
    def get_headers(self) -> dict:
        """
        Get HTTP headers with Bearer authorization.
        
        Returns:
            dict: Headers for API requests
        """
        if not self.token:
            raise ValueError("No token available. Call extract_token_from_browser first.")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://app-hqt.wellx.ai",
            "Referer": "https://app-hqt.wellx.ai/"
        }
