# src/pages/nlg/login_page.py
import time
# from src.utils.capcha_solver import solve_captcha
from src.utils.load_yaml import ALSAGR_USERNAME, ALSAGR_PASSWORD, MAX_SLEEP, MED_SLEEP, MIN_SLEEP
from src.utils.logger import alsagr_logger

# Page object for the login page
# *** This is the standard login page structure for the company portal (this sample case NLG company) entry, ***
class LoginPage:
    def __init__(self, page):
        self.page = page
        print("Login page initialized")

    async def login(self):
        await self.page.goto("https://sso.alsagrins.ae/login", timeout=60000)

        alsagr_logger.debug("browser opened")

        # Enter email and password
        await self.page.fill('#emailaddress', ALSAGR_USERNAME)
        time.sleep(MIN_SLEEP)
        await self.page.fill('#password', ALSAGR_PASSWORD)
        time.sleep(MIN_SLEEP)
        alsagr_logger.debug("Email and Password entered")


        # Submit the login form
        # Click login-in button
        await self.page.get_by_role("button", name="Log In", exact=True).click()
        alsagr_logger.debug("pressed login button")
        await self.page.wait_for_load_state('networkidle')
