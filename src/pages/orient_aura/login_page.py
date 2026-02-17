# src/pages/orient_aura/login_page.py

import asyncio
from src.utils.load_yaml import ORIENT_AURA_EMAIL, ORIENT_AURA_PASSWORD, MED_SLEEP
from src.utils.logger import orient_aura_logger


class LoginPage:
    def __init__(self, page):
        self.page = page

    async def login(self):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                await self._perform_login()
                orient_aura_logger.debug("Login Completed and Verified")
                return  # Login successful, exit the retry loop
            except Exception as e:
                retry_count += 1
                orient_aura_logger.warning(f"Login attempt {retry_count} failed: {e}")
                
                if retry_count < max_retries:
                    orient_aura_logger.debug(f"Retrying login (attempt {retry_count + 1}/{max_retries})")
                    await asyncio.sleep(5)  # Wait before retry
                else:
                    orient_aura_logger.error(f"Login failed after {max_retries} attempts")
                    raise Exception(f"Login failed after {max_retries} attempts: {e}")

    async def _perform_login(self):
        # Navigate to the login page
        await self.page.goto("https://smehealth.aurainsure.tech/08/orient/login", timeout=150000)
        await self.page.wait_for_load_state('networkidle')
        
        orient_aura_logger.debug("Login Page Loaded")
        # Wait for the email input to be visible
        await self.page.wait_for_selector('[formcontrolname="email"]', timeout=10000)

        # Enter email and password
        orient_aura_logger.debug("Entering Email and Password")

        orient_aura_logger.debug(f"Email: {ORIENT_AURA_EMAIL}")
        await self.page.fill('[formcontrolname="email"]', ORIENT_AURA_EMAIL) 
        orient_aura_logger.debug(f"After filling Email: {ORIENT_AURA_EMAIL}") 
        await asyncio.sleep(MED_SLEEP) 

        orient_aura_logger.debug(f"Password: {ORIENT_AURA_PASSWORD}")
        await self.page.fill('[formcontrolname="password"]', ORIENT_AURA_PASSWORD)
        orient_aura_logger.debug(f"After filling Password: {ORIENT_AURA_PASSWORD}")  
        await asyncio.sleep(MED_SLEEP)  
        orient_aura_logger.debug("Email and Password entered") 

        # Click login
        await self.page.click('button:has-text("Login")')
        
        orient_aura_logger.debug("Login Button Clicked")
        await asyncio.sleep(MED_SLEEP * 2) 
        await self.page.wait_for_load_state('networkidle')
        
        # Verify login success by checking for the presence of "Create new quote" button or dashboard elements
        try:
            # Wait for the main dashboard to load with "Create new quote" button
            await self.page.wait_for_selector('text="Create new quote"', timeout=90000)
            orient_aura_logger.debug("Login Success - Dashboard loaded with 'Create new quote' button visible")
        except Exception as e:
            orient_aura_logger.error(f"Login verification failed - Dashboard not loaded properly: {e}")
            
            # Check if we're still on login page (login failed)
            if await self.page.locator('[formcontrolname="email"]').is_visible():
                orient_aura_logger.error("Login failed - Still on login page")
                raise Exception("Login failed - credentials might be incorrect or page didn't redirect")
            
            # Check current URL for debugging
            current_url = self.page.url
            orient_aura_logger.error(f"Login verification failed - Current URL: {current_url}")
            raise Exception(f"Login verification failed - Expected dashboard but got URL: {current_url}")
