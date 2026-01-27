# src/pages/nlg/login_page.py
import asyncio
# from src.utils.capcha_solver import solve_captcha
from src.utils.load_yaml import GIG_USERNAME, GIG_PASSWORD, MAX_SLEEP, MED_SLEEP, MIN_SLEEP
from src.utils.logger import gig_logger

# Page object for the login page
# *** This is the standard login page structure for the company portal (this sample case NLG company) entry, ***
class LoginPage:
    def __init__(self, page):
        self.page = page
        print("Login page initialized")

    async def login(self):
        await self.page.goto("https://auth.axaebpartners.com/u/login?state=hKFo2SAtQk1tVmpSd2c5VFI4UDZxNGN6am1ic2FvM1F5S2RlQqFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIFZ0ZzhOMVZmbHVCYU5BU2pyYmNmbVNlRVZQU2hBUmZSo2NpZNkgNXJlOXV2OGI1M1BRVVpnSkZteFNDVmlmRzZJMzR6NzQ", timeout=60000)

        gig_logger.debug("browser opened")

        # Enter email and password
        await self.page.fill('#username', GIG_USERNAME)
        await asyncio.sleep(MIN_SLEEP)
        await self.page.fill('#password', GIG_PASSWORD)
        await asyncio.sleep(MIN_SLEEP)
        gig_logger.debug("Email and Password entered")


        # Press the login button
        await self.page.locator("//html/body/div/main/section/div/div/div/form/div[2]/button").click()


        gig_logger.debug("pressed login button")
        await self.page.wait_for_load_state('networkidle')
