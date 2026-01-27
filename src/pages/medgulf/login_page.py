import asyncio
# from src.utils.capcha_solver import solve_captcha
from src.utils.load_yaml import MEDGULF_USERNAME, MEDGULF_PASSWORD, MAX_SLEEP, MED_SLEEP, MIN_SLEEP
from src.utils.logger import medgulf_logger

# Page object for the login page
# *** This is the standard login page structure for the company portal (this sample case NLG company) entry, ***
class LoginPage:
    def __init__(self, page):
        self.page = page
        print("Login page initialized")

    async def login(self):
        await self.page.goto("https://smehealth.aurainsure.tech/10/medgulf-insurer/login", timeout=60000)

        medgulf_logger.debug("browser opened")

        # Enter email and password
        await self.page.fill('[formcontrolname="email"]', MEDGULF_USERNAME)  
        await asyncio.sleep(MED_SLEEP)  
        await self.page.fill('[formcontrolname="password"]', MEDGULF_PASSWORD)  
        await asyncio.sleep(MED_SLEEP)  
        medgulf_logger.debug("Email and Password entered")  

        # # Submit the login form
        # Click login-in button
        await self.page.get_by_role("button", name="Login", exact=True).click()
        medgulf_logger.debug("pressed login button")
        await self.page.wait_for_load_state('networkidle')