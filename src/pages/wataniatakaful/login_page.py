import asyncio
from src.utils.load_yaml import WATANIATAKAFUL_USERNAME, WATANIATAKAFUL_PASSWORD, MIN_SLEEP
import re
from src.utils.logger import wataniatakaful_logger

class LoginPage:
    def __init__(self, page):
        self.page = page

    async def perform_login(self):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                await self._perform_login_attempt()
                wataniatakaful_logger.debug("Login Completed and Verified")
                return  # Login successful, exit the retry loop
            except Exception as e:
                retry_count += 1
                wataniatakaful_logger.warning(f"Login attempt {retry_count} failed: {e}")
                
                if retry_count < max_retries:
                    wataniatakaful_logger.debug(f"Retrying login (attempt {retry_count + 1}/{max_retries})")
                    await asyncio.sleep(5)  # Wait before retry
                else:
                    wataniatakaful_logger.error(f"Login failed after {max_retries} attempts")
                    raise Exception(f"Login failed after {max_retries} attempts: {e}")

    async def _perform_login_attempt(self):
        await self.page.wait_for_load_state('networkidle')
        await self.page.goto("https://smehealth.aurainsure.tech/12/watania-takaful/login")
        await self.page.wait_for_load_state('networkidle')
        
        wataniatakaful_logger.debug("Login Page Loaded")

        # Wait explicitly for the Email Id textbox to appear (increase reliability)
        await self.page.locator("div").filter(has_text=re.compile(r"^Email Id$")).get_by_role("textbox").wait_for(timeout=20000)

        # Enter login credentials
        wataniatakaful_logger.debug("Entering Email and Password")
        await self.page.locator("div").filter(has_text=re.compile(r"^Email Id$")).get_by_role("textbox").fill(WATANIATAKAFUL_USERNAME)
        await self.page.locator("div").filter(has_text=re.compile(r"^Password$")).get_by_role("textbox").fill(WATANIATAKAFUL_PASSWORD)      

        # Click sign-in button
        await self.page.get_by_role("button", name="Login").click(timeout=10000)
        wataniatakaful_logger.debug('Login button clicked')
        await asyncio.sleep(MIN_SLEEP)
        await self.page.wait_for_load_state('networkidle')
        
        # Verify login success by checking for expected dashboard elements
        await self._verify_login_success()

    async def _verify_login_success(self):
        """Verify that login was successful by checking for dashboard elements"""
        try:
            # Wait for dashboard elements to appear - checking for typical post-login elements
            # You may need to adjust these selectors based on what appears after successful login
            
            # Try to find common dashboard elements
            dashboard_selectors = [
                'text="Create new quote"',
            ]
            
            login_successful = False
            for selector in dashboard_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=80000)
                    wataniatakaful_logger.debug(f"Login Success - Found dashboard element: {selector}")
                    login_successful = True
                    break
                except:
                    continue
            
            if not login_successful:
                # Check if we're still on login page (login failed)
                if await self.page.locator("div").filter(has_text=re.compile(r"^Email Id$")).get_by_role("textbox").is_visible():
                    wataniatakaful_logger.error("Login failed - Still on login page")
                    raise Exception("Login failed - credentials might be incorrect or page didn't redirect")
                
                # If not on login page but no dashboard elements found, log current URL for debugging
                current_url = self.page.url
                wataniatakaful_logger.warning(f"Login verification uncertain - Current URL: {current_url}")
                # Don't fail here, just log the warning and proceed
                wataniatakaful_logger.debug("Proceeding despite uncertain login verification")
            
        except Exception as e:
            wataniatakaful_logger.error(f"Login verification failed: {e}")
            raise Exception(f"Login verification failed: {e}")
