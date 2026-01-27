# src/pages/takaful/login_page.py

import asyncio
from src.utils.load_yaml import QATAR_EMAIL, QATAR_PASSWORD, MED_SLEEP

from src.utils.logger import qatar_logger

class LoginPage:
    def __init__(self, page):
        self.page = page

    async def login(self):
        # Navigate to the login page
        await self.page.goto("https://smehealth.aurainsure.tech/04/qic/login", timeout=150000)
        await self.page.wait_for_load_state('networkidle')
        
        qatar_logger.debug("Login Page Loaded")

        # Fill in email and password
        await self.page.fill('input[formcontrolname="email"]', QATAR_EMAIL)
        await asyncio.sleep(MED_SLEEP)  
        
        qatar_logger.debug("Email Filled ")
        
        await self.page.fill('input[formcontrolname="password"]', QATAR_PASSWORD)
        await asyncio.sleep(MED_SLEEP)  

        qatar_logger.debug("Password Filled ")

        # Click login
        # await self.page.click('button:has-text("Login")')
        
        # qatar_logger.debug("Login Button Clicked")
        
        # await self.page.wait_for_load_state('networkidle')
        
        # qatar_logger.debug("Login Completed")
        # Click login-in button
        await self.page.get_by_role("button", name="Login", exact=True).click()
        qatar_logger.debug("pressed login button")
        await self.page.wait_for_load_state('networkidle')