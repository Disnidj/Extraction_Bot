"""
MaxHealth Authentication Token Handler
Extracts and manages auth token from browser after login.
"""

import json
from src.utils.logger import maxhealth_logger


class MaxHealthAuthToken:
    """Handles extraction and storage of MaxHealth auth token."""
    
    def __init__(self):
        self.token = None
        self.token_type = None  # 'localStorage', 'sessionStorage', or 'cookie'
    
    async def extract_token_from_browser(self, page):
        """
        Extract auth token from browser storage after login.
        Checks localStorage, sessionStorage, and cookies.
        
        Args:
            page: Playwright page object after successful login
            
        Returns:
            str: The extracted token or None if not found
        """
        try:
            # Step 1: Check localStorage
            maxhealth_logger.debug("Checking localStorage for auth token...")
            local_storage = await page.evaluate("""
                () => {
                    let items = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        let key = localStorage.key(i);
                        items[key] = localStorage.getItem(key);
                    }
                    return items;
                }
            """)
            
            print(f"\n📋 localStorage keys found: {list(local_storage.keys())}")
            maxhealth_logger.debug(f"localStorage keys: {list(local_storage.keys())}")
            
            # Common localStorage keys for auth tokens
            token_keys = ["token", "auth_token", "authToken", "access_token", 
                          "accessToken", "jwt", "id_token", "bearerToken"]
            
            for key in token_keys:
                if key in local_storage and local_storage[key]:
                    self.token = local_storage[key].strip('"')
                    self.token_type = 'localStorage'
                    maxhealth_logger.debug(f"Token found in localStorage['{key}']")
                    return self.token
            
            # Look for JWT-like values in localStorage
            for key, value in local_storage.items():
                if value and isinstance(value, str):
                    # JWT tokens have 3 parts separated by dots
                    if value.count('.') == 2 and len(value) > 50:
                        self.token = value.strip('"')
                        self.token_type = 'localStorage'
                        maxhealth_logger.debug(f"JWT token found in localStorage['{key}']")
                        return self.token
                    # Check if it's a JSON with token inside
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, dict):
                            for tk in token_keys:
                                if tk in parsed:
                                    self.token = parsed[tk]
                                    self.token_type = 'localStorage'
                                    maxhealth_logger.debug(f"Token found in localStorage['{key}'].{tk}")
                                    return self.token
                    except:
                        pass
            
            # Step 2: Check sessionStorage
            maxhealth_logger.debug("Checking sessionStorage for auth token...")
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
            
            print(f"📋 sessionStorage keys found: {list(session_storage.keys())}")
            maxhealth_logger.debug(f"sessionStorage keys: {list(session_storage.keys())}")
            
            for key in token_keys:
                if key in session_storage and session_storage[key]:
                    self.token = session_storage[key].strip('"')
                    self.token_type = 'sessionStorage'
                    maxhealth_logger.debug(f"Token found in sessionStorage['{key}']")
                    return self.token
            
            # Look for JWT-like values in sessionStorage
            for key, value in session_storage.items():
                if value and isinstance(value, str):
                    if value.count('.') == 2 and len(value) > 50:
                        self.token = value.strip('"')
                        self.token_type = 'sessionStorage'
                        maxhealth_logger.debug(f"JWT token found in sessionStorage['{key}']")
                        return self.token
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, dict):
                            for tk in token_keys:
                                if tk in parsed:
                                    self.token = parsed[tk]
                                    self.token_type = 'sessionStorage'
                                    maxhealth_logger.debug(f"Token found in sessionStorage['{key}'].{tk}")
                                    return self.token
                    except:
                        pass
            
            # Step 3: Check cookies
            maxhealth_logger.debug("Checking cookies for auth token...")
            cookies = await page.context.cookies()
            cookie_names = [c['name'] for c in cookies]
            print(f"🍪 Cookie names found: {cookie_names}")
            maxhealth_logger.debug(f"Cookie names: {cookie_names}")
            
            for cookie in cookies:
                name = cookie['name'].lower()
                value = cookie['value']
                if any(tk in name for tk in ['token', 'auth', 'jwt', 'bearer', 'session']):
                    if len(value) > 20:  # Token should be reasonably long
                        self.token = value
                        self.token_type = 'cookie'
                        maxhealth_logger.debug(f"Token found in cookie '{cookie['name']}'")
                        return self.token
            
            maxhealth_logger.warning("No auth token found in localStorage, sessionStorage, or cookies")
            return None
            
        except Exception as e:
            maxhealth_logger.error(f"Error extracting token: {e}")
            return None
    
    def get_headers(self):
        """
        Get HTTP headers with auth token.
        
        Returns:
            dict: Headers dict with Authorization bearer token
        """
        if not self.token:
            raise ValueError("No token available. Call extract_token_from_browser first.")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://portal.maxhealth.ae",
            "Referer": "https://portal.maxhealth.ae/"
        }
    
    def is_valid(self):
        """Check if token exists."""
        return self.token is not None and len(self.token) > 20
