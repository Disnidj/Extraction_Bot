import asyncio

from src.utils.load_yaml import ALITTIHAD_ALWATANI_USERNAME, ALITTIHAD_ALWATANI_PASSWORD, MAX_SLEEP, MED_SLEEP, MIN_SLEEP
from src.utils.logger import alittihad_logger

class LoginPage:
    def __init__(self, page):
        self.page = page
        print("Login page initialized")
        alittihad_logger.info("Login Page Loaded")

    async def login(self):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                await self._perform_login_attempt()
                alittihad_logger.info("Login Completed and Verified")
                return  # Login successful, exit the retry loop
            except Exception as e:
                retry_count += 1
                alittihad_logger.warning(f"Login attempt {retry_count} failed: {e}")
                
                if retry_count < max_retries:
                    alittihad_logger.info(f"Retrying login (attempt {retry_count + 1}/{max_retries})")
                    await asyncio.sleep(5)  # Wait before retry
                else:
                    alittihad_logger.error(f"Login failed after {max_retries} attempts")
                    raise Exception(f"Login failed after {max_retries} attempts: {e}")

    async def _perform_login_attempt(self):
        await self.page.goto("https://smehealth.aurainsure.tech/01/aiaw/login", timeout=60000)
        await self.page.wait_for_load_state('networkidle')
        
        alittihad_logger.info("browser opened")

        # Enter email and password
        alittihad_logger.info("Entering Email and Password")
        await self.page.fill('[formcontrolname="email"]', ALITTIHAD_ALWATANI_USERNAME)  
        await asyncio.sleep(MED_SLEEP)  
        await self.page.fill('[formcontrolname="password"]', ALITTIHAD_ALWATANI_PASSWORD)  
        await asyncio.sleep(MED_SLEEP)  
        alittihad_logger.info("Email and Password entered")  

        # Click login button
        await self.page.get_by_role("button", name="Login", exact=True).click()
        alittihad_logger.info("pressed login button")
        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(MED_SLEEP)
        
        # Verify login success
        await self._verify_login_success()

    async def _verify_login_success(self):
        """Verify that login was successful by checking for dashboard elements"""
        try:
            # Wait for dashboard elements to appear - checking for typical post-login elements
            dashboard_selectors = [
                'text="Create new quote"',
            ]
            
            login_successful = False
            for selector in dashboard_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=80000)
                    alittihad_logger.info(f"Login Success - Found dashboard element: {selector}")
                    login_successful = True
                    break
                except:
                    continue
            
            if not login_successful:
                # Check if we're still on login page (login failed)
                if await self.page.locator('[formcontrolname="email"]').is_visible():
                    alittihad_logger.error("Login failed - Still on login page")
                    raise Exception("Login failed - credentials might be incorrect or page didn't redirect")
                
                # If not on login page but no dashboard elements found, log current URL for debugging
                current_url = self.page.url
                alittihad_logger.warning(f"Login verification uncertain - Current URL: {current_url}")
                
                # Check if URL indicates successful login
                if 'login' not in current_url.lower():
                    alittihad_logger.info("Login appears successful based on URL change")
                    login_successful = True
                else:
                    raise Exception(f"Login verification failed - Still appears to be on login page: {current_url}")
            
        except Exception as e:
            alittihad_logger.error(f"Login verification failed: {e}")
            raise Exception(f"Login verification failed: {e}")