"""
NLGI Aura Login Page Handler
Handles browser automation for NLGI Aura portal login
"""

import asyncio
from src.utils.load_yaml import NLGI_AURA_EMAIL, NLGI_AURA_PASSWORD, MED_SLEEP
from src.utils.logger import nlgi_aura_logger


class LoginPage:
    """Handles login to NLGI Aura portal"""
    
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
                nlgi_aura_logger.debug("Login Completed and Verified")
                return True  # Login successful
            except Exception as e:
                retry_count += 1
                nlgi_aura_logger.warning(f"Login attempt {retry_count} failed: {e}")
                
                if retry_count < max_retries:
                    nlgi_aura_logger.debug(f"Retrying login (attempt {retry_count + 1}/{max_retries})")
                    await asyncio.sleep(5)  # Wait before retry
                else:
                    nlgi_aura_logger.error(f"Login failed after {max_retries} attempts")
                    return False

    async def _perform_login(self):
        """Perform the actual login steps"""
        # Navigate to the login page
        await self.page.goto("https://smehealth.aurainsure.tech/06/nlgi/login", timeout=150000)
        await self.page.wait_for_load_state('networkidle')
        
        nlgi_aura_logger.debug("Login Page Loaded")
        
        # Wait for the email input to be visible
        await self.page.wait_for_selector('[formcontrolname="email"]', timeout=10000)

        # Enter email and password
        nlgi_aura_logger.debug("Entering Email and Password")

        nlgi_aura_logger.debug(f"Email: {NLGI_AURA_EMAIL}")
        await self.page.fill('[formcontrolname="email"]', NLGI_AURA_EMAIL) 
        nlgi_aura_logger.debug(f"After filling Email: {NLGI_AURA_EMAIL}") 
        await asyncio.sleep(MED_SLEEP) 

        nlgi_aura_logger.debug(f"Password: {NLGI_AURA_PASSWORD}")
        await self.page.fill('[formcontrolname="password"]', NLGI_AURA_PASSWORD)
        nlgi_aura_logger.debug(f"After filling Password: {NLGI_AURA_PASSWORD}")  
        await asyncio.sleep(MED_SLEEP)  
        nlgi_aura_logger.debug("Email and Password entered") 

        # Click login
        await self.page.click('button:has-text("Login")')
        
        nlgi_aura_logger.debug("Login Button Clicked")
        await asyncio.sleep(MED_SLEEP * 2) 
        await self.page.wait_for_load_state('networkidle')
        
        # Verify login success by checking for the presence of "Create new quote" button or dashboard elements
        try:
            # Wait for the main dashboard to load with "Create new quote" button
            await self.page.wait_for_selector('text="Create new quote"', timeout=90000)
            nlgi_aura_logger.debug("Login Success - Dashboard loaded with 'Create new quote' button visible")
        except Exception as e:
            nlgi_aura_logger.error(f"Login verification failed - Dashboard not loaded properly: {e}")
            
            # Check if we're still on login page (login failed)
            if await self.page.locator('[formcontrolname="email"]').is_visible():
                nlgi_aura_logger.error("Login failed - Still on login page")
                raise Exception("Login failed - credentials might be incorrect or page didn't redirect")
            
            # Check current URL for debugging
            current_url = self.page.url
            nlgi_aura_logger.error(f"Login verification failed - Current URL: {current_url}")
            raise Exception(f"Login verification failed - Expected dashboard but got URL: {current_url}")

    async def navigate(self):
        """Navigate to NLGI Aura login page (compatibility method)"""
        # This method exists for compatibility but actual navigation is done in _perform_login
        pass

