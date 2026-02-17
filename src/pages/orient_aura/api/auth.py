"""
Orient Aura Authentication Token Handler
Extracts and manages auth token from browser after login.
"""

import json
from src.utils.logger import orient_aura_logger


class OrientAuraAuthToken:
    """Handles extraction and storage of Orient Aura auth token."""
    
    def __init__(self):
        self.token = None
    
    async def extract_token_from_browser(self, page):
        """
        Extract auth token from browser localStorage after login.
        The token is stored by Angular in localStorage with key "token".
        
        Args:
            page: Playwright page object after successful login
            
        Returns:
            str: The extracted JWT token or None if not found
        """
        orient_aura_logger.info("Starting token extraction from browser storage...")
        
        try:
            # Orient stores token in localStorage with key "token"
            orient_aura_logger.debug("Checking for token in localStorage['token']")
            
            token = await page.evaluate("localStorage.getItem('token')")
            if token:
                self.token = token.strip('"')  # Remove quotes if present
                orient_aura_logger.info(f"✓ Token found in localStorage['token'] (length: {len(self.token)})")
                orient_aura_logger.debug(f"Token format: {self.token[:20]}...{self.token[-20:]}")
                return self.token
            
            orient_aura_logger.debug("Token not found in 'token' key, checking other common keys...")
            
            # Try other common token keys
            token_keys = [
                "auth_token", 
                "authToken",
                "access_token",
                "accessToken",
                "jwt",
                "id_token"
            ]
            
            for key in token_keys:
                token = await page.evaluate(f"localStorage.getItem('{key}')")
                if token:
                    self.token = token.strip('"')
                    orient_aura_logger.info(f"✓ Token found in localStorage['{key}'] (length: {len(self.token)})")
                    return self.token
            
            # If not found, get ALL localStorage items to find the token
            orient_aura_logger.debug("Token not found in common keys, checking all localStorage items...")
            
            all_storage = await page.evaluate("""
                () => {
                    let items = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        let key = localStorage.key(i);
                        items[key] = localStorage.getItem(key);
                    }
                    return items;
                }
            """)
            
            orient_aura_logger.debug(f"All localStorage keys: {list(all_storage.keys())}")
            
            # Look for token-like values (JWT format: xxx.xxx.xxx)
            for key, value in all_storage.items():
                if value and isinstance(value, str):
                    # JWT tokens have 3 parts separated by dots
                    if value.count('.') == 2 and len(value) > 50:
                        self.token = value.strip('"')
                        orient_aura_logger.info(f"✓ JWT token found in localStorage['{key}']")
                        return self.token
                    # Check if it's a JSON with token inside
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, dict):
                            for tk in ['token', 'access_token', 'accessToken', 'id_token']:
                                if tk in parsed:
                                    self.token = parsed[tk]
                                    orient_aura_logger.info(f"✓ Token found in localStorage['{key}'].{tk}")
                                    return self.token
                    except:
                        pass
            
            # Also check sessionStorage
            session_storage = await page.evaluate("""
                () => {
                    let items = {};
                    for (let i = 0; i < sessionStorage.length; i++) {
                        let key = sessionStorage.key(i);
                        items[key] = sessionStorage.getItem(key);
                    }
                    return items;
                }
            """)
            
            orient_aura_logger.debug(f"All sessionStorage keys: {list(session_storage.keys())}")
            
            for key, value in session_storage.items():
                if value and isinstance(value, str):
                    if value.count('.') == 2 and len(value) > 50:
                        self.token = value.strip('"')
                        orient_aura_logger.info(f"✓ JWT token found in sessionStorage['{key}']")
                        return self.token
            
            orient_aura_logger.error("❌ Token not found in localStorage or sessionStorage")
            return None
            
        except Exception as e:
            orient_aura_logger.error(f"Error extracting token: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_headers(self):
        """
        Get HTTP headers with authorization token for API requests.
        
        Returns:
            dict: Headers dict with Authorization bearer token and Orient-specific headers
        """
        if not self.token:
            orient_aura_logger.error("No token available for headers")
            return {}
        
        return {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "insurerurl": "orient",
            "reinsurername": "ccr",
            "client_code": "null",
            "origin": "https://smehealth.aurainsure.tech",
            "referer": "https://smehealth.aurainsure.tech/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"
        }
