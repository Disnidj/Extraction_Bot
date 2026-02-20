"""
QIC HealthX Login Page Handler
Handles browser automation for QIC HealthX portal login

Portal URL: https://app-hqt.wellx.ai
"""

import asyncio
from src.utils.load_yaml import QIC_HEALTHX_EMAIL, QIC_HEALTHX_PASSWORD, MED_SLEEP
from src.utils.logger import qic_healthx_logger


class LoginPage:
    """Handles login to QIC HealthX portal"""
    
    # Login page URL
    LOGIN_URL = "https://app-hqt.wellx.ai/login"
    
    # Element selectors based on provided HTML
    SELECTORS = {
        "email": "#email",  # <input id="email">
        "password": "#password",  # <input id="password">
        "login_button": "button[type='submit']:has-text('Login')",  # Login button
        "new_quote_button": "button:has-text('New Quote')"  # Dashboard verification
    }
    
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
                qic_healthx_logger.debug("Login Completed and Verified")
                return True  # Login successful
            except Exception as e:
                retry_count += 1
                qic_healthx_logger.warning(f"Login attempt {retry_count} failed: {e}")
                
                if retry_count < max_retries:
                    qic_healthx_logger.debug(f"Retrying login (attempt {retry_count + 1}/{max_retries})")
                    await asyncio.sleep(2)  # Wait before retry
                else:
                    qic_healthx_logger.error(f"Login failed after {max_retries} attempts")
                    return False

    async def _perform_login(self):
        """Perform the actual login steps"""
        # Navigate to the login page
        qic_healthx_logger.info(f"Navigating to: {self.LOGIN_URL}")
        await self.page.goto(self.LOGIN_URL, timeout=150000)
        await self.page.wait_for_load_state('networkidle')
        
        qic_healthx_logger.debug("Login Page Loaded")
        
        # Wait for the email input to be visible
        await self.page.wait_for_selector(self.SELECTORS["email"], timeout=15000)
        qic_healthx_logger.debug("Email input found")

        # Enter email
        qic_healthx_logger.debug(f"Entering email: {QIC_HEALTHX_EMAIL}")
        await self.page.fill(self.SELECTORS["email"], QIC_HEALTHX_EMAIL)
        await asyncio.sleep(MED_SLEEP)

        # Enter password
        qic_healthx_logger.debug("Entering password")
        await self.page.fill(self.SELECTORS["password"], QIC_HEALTHX_PASSWORD)
        await asyncio.sleep(MED_SLEEP)
        
        qic_healthx_logger.debug("Email and Password entered")

        # Click login button
        await self.page.click(self.SELECTORS["login_button"])
        qic_healthx_logger.debug("Login Button Clicked")
        
        # Wait for page to load
        await asyncio.sleep(MED_SLEEP * 2)
        await self.page.wait_for_load_state('networkidle')
        
        # Verify login success by checking for dashboard elements
        try:
            # Wait for the "New Quote" button which appears on successful login
            await self.page.wait_for_selector(self.SELECTORS["new_quote_button"], timeout=45000)
            qic_healthx_logger.debug("Login Success - Dashboard loaded with 'New Quote' button visible")
        except Exception as e:
            qic_healthx_logger.error(f"Login verification failed - Dashboard not loaded properly: {e}")
            
            # Check if we're still on login page (login failed)
            if await self.page.locator(self.SELECTORS["email"]).is_visible():
                qic_healthx_logger.error("Login failed - Still on login page")
                raise Exception("Login failed - credentials might be incorrect or page didn't redirect")
            
            # Check current URL for debugging
            current_url = self.page.url
            qic_healthx_logger.error(f"Login verification failed - Current URL: {current_url}")
            raise Exception(f"Login verification failed - Expected dashboard but got URL: {current_url}")

    async def navigate(self):
        """Navigate to QIC HealthX login page (compatibility method)"""
        await self.page.goto(self.LOGIN_URL, timeout=150000)
        await self.page.wait_for_load_state('networkidle')
