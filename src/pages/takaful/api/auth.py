"""
Takaful Authentication Token Handler
Extracts and manages auth token from browser after login.
"""

import json
from src.utils.logger import takaful_logger


class TakafulAuthToken:
    """Handles extraction and storage of Takaful auth token."""
    
    def __init__(self):
        self.token = None
    
    async def extract_token_from_browser(self, page):
        """
        Extract auth token from browser localStorage after login.
        The token is stored by Angular in localStorage.
        
        Args:
            page: Playwright page object after successful login
            
        Returns:
            str: The extracted JWT token or None if not found
        """
        takaful_logger.info("Starting token extraction from browser storage...")
        
        try:
            # Common localStorage keys for Angular auth tokens
            token_keys = [
                "token",
                "auth_token", 
                "authToken",
                "access_token",
                "accessToken",
                "jwt",
                "id_token"
            ]
            
            takaful_logger.debug(f"Checking {len(token_keys)} common token keys in localStorage")
            
            # Try each possible key
            for key in token_keys:
                token = await page.evaluate(f"localStorage.getItem('{key}')")
                if token:
                    self.token = token.strip('"')
                    takaful_logger.info(f"✓ Token found in localStorage['{key}'] (length: {len(self.token)})")
                    takaful_logger.debug(f"Token format: {self.token[:20]}...{self.token[-20:]}")
                    return self.token
            
            takaful_logger.debug("Token not found in common keys, checking all localStorage items...")
            
            # If not found, get ALL localStorage items to find the token
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
            
            takaful_logger.debug(f"All localStorage keys: {list(all_storage.keys())}")
            
            # Look for token-like values (JWT format: xxx.xxx.xxx)
            for key, value in all_storage.items():
                if value and isinstance(value, str):
                    # JWT tokens have 3 parts separated by dots
                    if value.count('.') == 2 and len(value) > 50:
                        self.token = value.strip('"')
                        takaful_logger.debug(f"JWT token found in localStorage['{key}']")
                        return self.token
                    # Check if it's a JSON with token inside
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, dict):
                            for tk in ['token', 'access_token', 'accessToken', 'id_token']:
                                if tk in parsed:
                                    self.token = parsed[tk]
                                    takaful_logger.debug(f"Token found in localStorage['{key}'].{tk}")
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
            
            takaful_logger.debug(f"All sessionStorage keys: {list(session_storage.keys())}")
            
            for key, value in session_storage.items():
                if value and isinstance(value, str) and value.count('.') == 2 and len(value) > 50:
                    self.token = value.strip('"')
                    takaful_logger.debug(f"JWT token found in sessionStorage['{key}']")
                    return self.token
            
            takaful_logger.error("No auth token found in browser storage")
            return None
            
        except Exception as e:
            takaful_logger.error(f"Error extracting token: {e}")
            return None
    
    def get_headers(self):
        """
        Return headers with authorization for API calls.
        Includes custom headers for Takaful portal.
        
        Returns:
            dict: Headers dictionary with Bearer token and custom headers
            
        Raises:
            ValueError: If token is not set
        """
        if not self.token:
            raise ValueError("Token not set. Call extract_token_from_browser first.")
        
        # Import here to avoid circular imports
        from .mapping import CUSTOM_HEADERS
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            **CUSTOM_HEADERS  # Add custom headers (insurerurl, reinsurername, client_code)
        }
        return headers
    
    def is_valid(self):
        """Check if token exists."""
        return self.token is not None and len(self.token) > 0
