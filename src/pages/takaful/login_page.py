# src/pages/takaful/login_page.py

import asyncio
from src.utils.load_yaml import TAKAFUL_EMAIL, TAKAFUL_PASSWORD, MED_SLEEP

from src.utils.logger import takaful_logger

class LoginPage:
    def __init__(self, page):
        self.page = page

    async def login(self):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                await self._perform_login()
                takaful_logger.debug("Login Completed and Verified")
                return  # Login successful, exit the retry loop
            except Exception as e:
                retry_count += 1
                takaful_logger.warning(f"Login attempt {retry_count} failed: {e}")
                
                if retry_count < max_retries:
                    takaful_logger.debug(f"Retrying login (attempt {retry_count + 1}/{max_retries})")
                    await asyncio.sleep(5)  # Wait before retry
                else:
                    takaful_logger.error(f"Login failed after {max_retries} attempts")
                    raise Exception(f"Login failed after {max_retries} attempts: {e}")

    async def _perform_login(self):
        # Navigate to the login page
        await self.page.goto("https://smehealth.aurainsure.tech/01/takafulemarat/login", timeout=150000)
        await self.page.wait_for_load_state('networkidle')
        
        takaful_logger.debug("Login Page Loaded")
        # Wait for the email input to be visible
        await self.page.wait_for_selector('[formcontrolname="email"]', timeout=10000)

        # Enter email and password
        takaful_logger.debug("Entering Email and Password")

        takaful_logger.debug(f"Email: {TAKAFUL_EMAIL}")
        await self.page.fill('[formcontrolname="email"]', TAKAFUL_EMAIL) 
        takaful_logger.debug(f"After filling Email: {TAKAFUL_EMAIL}") 
        await asyncio.sleep(MED_SLEEP) 

        takaful_logger.debug(f"Password: {TAKAFUL_PASSWORD}")
        await self.page.fill('[formcontrolname="password"]', TAKAFUL_PASSWORD)
        takaful_logger.debug(f"After filling Password: {TAKAFUL_PASSWORD}")  
        await asyncio.sleep(MED_SLEEP)  
        takaful_logger.debug("Email and Password entered") 

        # Click login
        await self.page.click('button:has-text("Login")')
        
        takaful_logger.debug("Login Button Clicked")
        await asyncio.sleep(MED_SLEEP * 2) 
        await self.page.wait_for_load_state('networkidle')
        
        # Verify login success by checking for the presence of "Create new quote" button or dashboard elements
        try:
            # Wait for the main dashboard to load with "Create new quote" button
            await self.page.wait_for_selector('text="Create new quote"', timeout=90000)
            takaful_logger.debug("Login Success - Dashboard loaded with 'Create new quote' button visible")
        except Exception as e:
            takaful_logger.error(f"Login verification failed - Dashboard not loaded properly: {e}")
            
            # Check if we're still on login page (login failed)
            if await self.page.locator('[formcontrolname="email"]').is_visible():
                takaful_logger.error("Login failed - Still on login page")
                raise Exception("Login failed - credentials might be incorrect or page didn't redirect")
            
            # Check current URL for debugging
            current_url = self.page.url
            takaful_logger.error(f"Login verification failed - Current URL: {current_url}")
            raise Exception(f"Login verification failed - Expected dashboard but got URL: {current_url}")

        