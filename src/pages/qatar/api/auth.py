"""
Qatar Authentication Token Handler
Extracts and manages auth token from browser after login.
Uses same Aura platform as Takaful.
"""

import json
from src.utils.logger import qatar_logger


class QatarAuthToken:
    """Handles extraction and storage of Qatar auth token."""
    
    def __init__(self):
        self.token = None
    
    async def extract_token_from_browser(self, page):
        """
        Extract auth token from browser storage after login.
        Checks localStorage, sessionStorage, and cookies.
        
        Args:
            page: Playwright page object after successful login
            
        Returns:
            str: The extracted JWT token or None if not found
        """
        qatar_logger.info("Starting token extraction from browser storage...")
        
        try:
            # Common token keys
            token_keys = [
                "token",
                "auth_token", 
                "authToken",
                "access_token",
                "accessToken",
                "jwt",
                "id_token"
            ]
            
            qatar_logger.debug(f"Checking {len(token_keys)} common token keys in localStorage")
            
            # First try localStorage
            for key in token_keys:
                token = await page.evaluate(f"localStorage.getItem('{key}')")
                if token:
                    self.token = token.strip('"')
                    qatar_logger.info(f"✓ Token found in localStorage['{key}'] (length: {len(self.token)})")
                    return self.token
            
            # Try sessionStorage (Qatar might use this instead)
            qatar_logger.debug("Checking sessionStorage...")
            for key in token_keys:
                token = await page.evaluate(f"sessionStorage.getItem('{key}')")
                if token:
                    self.token = token.strip('"')
                    qatar_logger.info(f"✓ Token found in sessionStorage['{key}'] (length: {len(self.token)})")
                    print(f"   ✅ Token found in sessionStorage['{key}']")
                    return self.token
            
            # Get ALL sessionStorage items
            all_session = await page.evaluate("""
                () => {
                    let items = {};
                    for (let i = 0; i < sessionStorage.length; i++) {
                        let key = sessionStorage.key(i);
                        items[key] = sessionStorage.getItem(key);
                    }
                    return items;
                }
            """)
            
            print(f"   📋 sessionStorage keys: {list(all_session.keys())}")
            qatar_logger.debug(f"All sessionStorage keys: {list(all_session.keys())}")
            
            # Look for JWT tokens in sessionStorage
            for key, value in all_session.items():
                if value and isinstance(value, str):
                    # JWT tokens have 3 parts separated by dots
                    if value.count('.') == 2 and len(value) > 50:
                        self.token = value.strip('"')
                        qatar_logger.debug(f"JWT token found in sessionStorage['{key}']")
                        print(f"   ✅ JWT token found in sessionStorage['{key}']")
                        return self.token
                    # Check if it's a JSON with token inside
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, dict):
                            for tk in ['token', 'access_token', 'accessToken', 'id_token']:
                                if tk in parsed:
                                    self.token = parsed[tk]
                                    qatar_logger.debug(f"Token found in sessionStorage['{key}'].{tk}")
                                    print(f"   ✅ Token found in sessionStorage['{key}'].{tk}")
                                    return self.token
                    except:
                        pass
            
            # Check cookies as last resort
            qatar_logger.debug("Checking cookies...")
            cookies = await page.context.cookies()
            print(f"   🍪 Cookie names: {[c['name'] for c in cookies]}")
            
            for cookie in cookies:
                if any(tk in cookie['name'].lower() for tk in ['token', 'auth', 'jwt', 'access']):
                    value = cookie['value']
                    if value.count('.') == 2 and len(value) > 50:
                        self.token = value
                        qatar_logger.debug(f"JWT token found in cookie['{cookie['name']}']")
                        print(f"   ✅ Token found in cookie['{cookie['name']}']")
                        return self.token
            
            qatar_logger.warning("No auth token found in any storage")
            return None
            
        except Exception as e:
            qatar_logger.error(f"Error extracting token: {e}")
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
            "Origin": "https://smehealth.aurainsure.tech",
            "Referer": "https://smehealth.aurainsure.tech/"
        }
    
    def is_valid(self):
        """Check if token exists."""
        return self.token is not None and len(self.token) > 50
