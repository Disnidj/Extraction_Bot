# src/pages/qatar/login_page.py

import asyncio
from src.utils.load_yaml import QATAR_EMAIL, QATAR_PASSWORD, MED_SLEEP

from src.utils.logger import qatar_logger

class LoginPage:
    def __init__(self, page):
        self.page = page

    async def login(self, max_retries: int = 3):
        """
        Perform login with retry logic
        
        Args:
            max_retries: Maximum number of login attempts
            
        Returns:
            bool: True if login successful, False otherwise
        """
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                await self._perform_login()
                qatar_logger.debug("Login Completed and Verified")
                return True  # Login successful
            except Exception as e:
                retry_count += 1
                qatar_logger.warning(f"Login attempt {retry_count} failed: {e}")
                
                if retry_count < max_retries:
                    qatar_logger.debug(f"Retrying login (attempt {retry_count + 1}/{max_retries})")
                    await asyncio.sleep(2)  # Wait before retry (reduced from 5s)
                else:
                    qatar_logger.error(f"Login failed after {max_retries} attempts")
                    return False

    async def _perform_login(self):
        """Perform the actual login steps"""
        # Navigate to the login page
        await self.page.goto("https://smehealth.aurainsure.tech/04/qic/login", timeout=150000)
        await self.page.wait_for_load_state('networkidle')
        
        qatar_logger.debug("Login Page Loaded")
        
        # Wait for the email input to be visible
        await self.page.wait_for_selector('[formcontrolname="email"]', timeout=10000)

        # Fill in email and password
        qatar_logger.debug("Entering Email and Password")
        
        qatar_logger.debug(f"Email: {QATAR_EMAIL}")
        await self.page.fill('input[formcontrolname="email"]', QATAR_EMAIL)
        qatar_logger.debug(f"After filling Email: {QATAR_EMAIL}")
        await asyncio.sleep(MED_SLEEP)  
        
        qatar_logger.debug(f"Password: {QATAR_PASSWORD}")
        await self.page.fill('input[formcontrolname="password"]', QATAR_PASSWORD)
        qatar_logger.debug(f"After filling Password: {QATAR_PASSWORD}")
        await asyncio.sleep(MED_SLEEP)  
        qatar_logger.debug("Email and Password entered")

        # Click login button
        await self.page.get_by_role("button", name="Login", exact=True).click()
        qatar_logger.debug("Login Button Clicked")
        await asyncio.sleep(MED_SLEEP * 2)
        await self.page.wait_for_load_state('networkidle')
        
        # Verify login success by checking for the presence of "Create new quote" button
        try:
            # Wait for the main dashboard to load with "Create new quote" button
            await self.page.wait_for_selector('text="Create new quote"', timeout=45000)
            qatar_logger.debug("Login Success - Dashboard loaded with 'Create new quote' button visible")
        except Exception as e:
            qatar_logger.error(f"Login verification failed - Dashboard not loaded properly: {e}")
            
            # Check if we're still on login page (login failed)
            if await self.page.locator('[formcontrolname="email"]').is_visible():
                qatar_logger.error("Login failed - Still on login page")
                raise Exception("Login failed - credentials might be incorrect or page didn't redirect")
            
            # Check current URL for debugging
            current_url = self.page.url
            qatar_logger.error(f"Login verification failed - Current URL: {current_url}")
            raise Exception(f"Login verification failed - Expected dashboard but got URL: {current_url}")