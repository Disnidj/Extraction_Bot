# src/pages/nlg/login_page.py
import asyncio
# from src.utils.capcha_solver import solve_captcha
from src.utils.load_yaml import FIDELITY_USERNAME, FIDELITY_PASSWORD, MAX_SLEEP, MED_SLEEP, MIN_SLEEP
from src.utils.logger import fidelity_logger

# Page object for the login page
# *** This is the standard login page structure for the company portal (this sample case NLG company) entry, ***
class LoginPage:
    def __init__(self, page):
        self.page = page
        print("Login page initialized")

    async def login(self):
        await self.page.goto("https://smehealth.aurainsure.tech/13/fidelity/login", timeout=60000)

        fidelity_logger.debug("browser opened")

        # Enter email and password
        await self.page.fill('[formcontrolname="email"]', FIDELITY_USERNAME)  
        await asyncio.sleep(MED_SLEEP)  
        await self.page.fill('[formcontrolname="password"]', FIDELITY_PASSWORD)  
        await asyncio.sleep(MED_SLEEP)  
        fidelity_logger.debug("Email and Password entered")  

        # # Submit the login form
        # Click login-in button
        await self.page.get_by_role("button", name="Login", exact=True).click()
        fidelity_logger.debug("pressed login button")
        await self.page.wait_for_load_state('networkidle')