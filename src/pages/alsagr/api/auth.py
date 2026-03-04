"""
Al Sagr Authentication Token Handler
Extracts and manages JWT auth token from browser after Selenium login.

Al Sagr stores the token in localStorage after SSO login.
The token is required for all API calls to ndapi.alsagrins.ae.
"""

import json
import re
from src.utils.logger import alsagr_logger
from .mapping import DEFAULT_HEADERS, API_BASE_URL


class AlSagrAuthToken:
    """
    Handles extraction and storage of Al Sagr JWT auth token.
    
    After Selenium login to https://sso.alsagrins.ae/login,
    the JWT token is stored in browser localStorage.
    This token is required for Authorization header in API calls.
    """
    
    def __init__(self):
        self.token = None
    
    async def extract_token_from_browser(self, page):
        """
        Extract JWT auth token from browser localStorage after login.
        
        Al Sagr stores the token in localStorage with various possible keys.
        This method searches common key patterns to find the JWT token.
        
        Args:
            page: Playwright/Patchright page object after successful login
            
        Returns:
            str: The extracted JWT token or None if not found
        """
        alsagr_logger.info("Starting token extraction from browser storage...")
        
        try:
            # Common token keys used by Al Sagr portal
            token_keys = [
                "token",
                "auth_token", 
                "authToken",
                "access_token",
                "accessToken",
                "jwt",
                "id_token",
                "bearer_token",
                "bearerToken",
            ]
            
            # Try each common key
            for key in token_keys:
                alsagr_logger.debug(f"Checking localStorage['{key}']...")
                token = await page.evaluate(f"localStorage.getItem('{key}')")
                if token:
                    self.token = token.strip('"')
                    alsagr_logger.info(f"✓ Token found in localStorage['{key}'] (length: {len(self.token)})")
                    alsagr_logger.debug(f"Token format: {self.token[:30]}...{self.token[-20:]}")
                    return self.token
            
            # If not found in common keys, scan all localStorage
            alsagr_logger.debug("Token not found in common keys, scanning all localStorage items...")
            
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
            
            alsagr_logger.debug(f"All localStorage keys: {list(all_storage.keys())}")
            
            # Look for JWT-like values (format: xxx.xxx.xxx)
            for key, value in all_storage.items():
                if value and isinstance(value, str):
                    # JWT tokens have 3 parts separated by dots
                    if value.count('.') == 2 and len(value) > 50:
                        self.token = value.strip('"')
                        alsagr_logger.info(f"✓ JWT token found in localStorage['{key}'] (length: {len(self.token)})")
                        return self.token
                    
                    # Check if value is JSON containing a token
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, dict):
                            for tk in ['token', 'access_token', 'accessToken', 'id_token', 'jwt']:
                                if tk in parsed:
                                    self.token = str(parsed[tk]).strip('"')
                                    alsagr_logger.info(f"✓ Token found in localStorage['{key}'].{tk}")
                                    return self.token
                    except (json.JSONDecodeError, TypeError):
                        pass
            
            # Also check sessionStorage
            alsagr_logger.debug("Checking sessionStorage...")
            
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
            
            alsagr_logger.debug(f"All sessionStorage keys: {list(session_storage.keys())}")
            
            for key, value in session_storage.items():
                if value and isinstance(value, str):
                    if value.count('.') == 2 and len(value) > 50:
                        self.token = value.strip('"')
                        alsagr_logger.info(f"✓ JWT token found in sessionStorage['{key}']")
                        return self.token
            
            alsagr_logger.error("❌ Token not found in localStorage or sessionStorage")
            return None
            
        except Exception as e:
            alsagr_logger.error(f"Error extracting token: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_headers(self):
        """
        Get HTTP headers with Authorization token for API requests.
        
        Returns:
            dict: Headers dict with Authorization Bearer token
        """
        if not self.token:
            alsagr_logger.error("No token available for headers")
            return DEFAULT_HEADERS.copy()
        
        headers = DEFAULT_HEADERS.copy()
        headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def is_authenticated(self) -> bool:
        """
        Check if we have a valid token.
        
        Returns:
            bool: True if token is available
        """
        return self.token is not None and len(self.token) > 0
    
    async def extract_quotation_info_from_page(self, page):
        """
        Extract quotationId and other parameters from the current page.
        
        This method checks:
        1. URL for quotationId parameter
        2. Page DOM/localStorage for stored quotation data
        3. Network requests for API calls containing quotationId
        
        Args:
            page: Playwright/Patchright page object
            
        Returns:
            dict: {"quotationId": int, "proposalId": int} or None if not found
        """
        alsagr_logger.info("Extracting quotation information from page...")
        
        quotation_info = {
            "quotationId": None,
            "proposalId": None,
        }
        
        try:
            # Method 1: Check URL for quotationId
            current_url = page.url
            alsagr_logger.debug(f"Current URL: {current_url}")
            
            # Pattern 1: quotationId=123 or quotationId:123
            match = re.search(r'quotationId[=:](\d+)', current_url, re.IGNORECASE)
            if match:
                quotation_info["quotationId"] = int(match.group(1))
                alsagr_logger.info(f"✓ Found quotationId in URL: {quotation_info['quotationId']}")
            
            # Pattern 2: /quotation/123 or /quote/123
            if not quotation_info["quotationId"]:
                match = re.search(r'/(?:quotation|quote)/(\d+)', current_url, re.IGNORECASE)
                if match:
                    quotation_info["quotationId"] = int(match.group(1))
                    alsagr_logger.info(f"✓ Found quotationId in URL path: {quotation_info['quotationId']}")
            
            # Method 2: Check localStorage for quotation data
            if not quotation_info["quotationId"]:
                alsagr_logger.debug("Checking localStorage for quotation data...")
                
                storage_keys = [
                    "quotationId",
                    "currentQuotation",
                    "quotation",
                    "quoteId",
                    "selectedQuotation",
                ]
                
                for key in storage_keys:
                    value = await page.evaluate(f"localStorage.getItem('{key}')")
                    if value:
                        try:
                            # Try to parse as integer
                            quotation_info["quotationId"] = int(value)
                            alsagr_logger.info(f"✓ Found quotationId in localStorage['{key}']: {quotation_info['quotationId']}")
                            break
                        except:
                            # Try to parse as JSON
                            try:
                                parsed = json.loads(value)
                                if isinstance(parsed, dict) and "quotationId" in parsed:
                                    quotation_info["quotationId"] = int(parsed["quotationId"])
                                    alsagr_logger.info(f"✓ Found quotationId in localStorage['{key}'].quotationId: {quotation_info['quotationId']}")
                                    if "proposalId" in parsed:
                                        quotation_info["proposalId"] = int(parsed["proposalId"])
                                    break
                            except:
                                pass
            
            # Method 3: Check sessionStorage
            if not quotation_info["quotationId"]:
                alsagr_logger.debug("Checking sessionStorage for quotation data...")
                
                for key in storage_keys:
                    value = await page.evaluate(f"sessionStorage.getItem('{key}')")
                    if value:
                        try:
                            quotation_info["quotationId"] = int(value)
                            alsagr_logger.info(f"✓ Found quotationId in sessionStorage['{key}']: {quotation_info['quotationId']}")
                            break
                        except:
                            try:
                                parsed = json.loads(value)
                                if isinstance(parsed, dict) and "quotationId" in parsed:
                                    quotation_info["quotationId"] = int(parsed["quotationId"])
                                    alsagr_logger.info(f"✓ Found quotationId in sessionStorage['{key}'].quotationId")
                                    if "proposalId" in parsed:
                                        quotation_info["proposalId"] = int(parsed["proposalId"])
                                    break
                            except:
                                pass
            
            # Method 4: Extract from page DOM
            if not quotation_info["quotationId"]:
                alsagr_logger.debug("Checking page DOM for quotation data...")
                
                # Look for hidden inputs or data attributes
                quotation_id_selectors = [
                    "input[name='quotationId']",
                    "input[id='quotationId']",
                    "[data-quotation-id]",
                    "[data-quotationid]",
                ]
                
                for selector in quotation_id_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            value = await element.get_attribute("value") or await element.get_attribute("data-quotation-id") or await element.get_attribute("data-quotationid")
                            if value:
                                quotation_info["quotationId"] = int(value)
                                alsagr_logger.info(f"✓ Found quotationId in DOM ({selector}): {quotation_info['quotationId']}")
                                break
                    except:
                        pass
            
            # Return results
            if quotation_info["quotationId"]:
                alsagr_logger.info(f"Successfully extracted quotation info: {quotation_info}")
                return quotation_info
            else:
                alsagr_logger.warning("Could not extract quotationId from page")
                return None
                
        except Exception as e:
            alsagr_logger.error(f"Error extracting quotation info: {e}")
            import traceback
            traceback.print_exc()
            return None
