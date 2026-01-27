# src/pages/nlg/login_page.py
import asyncio
from src.utils.capcha_solver import solve_captcha
from src.utils.load_yaml import ADNIC_USERNAME, ADNIC_PASSWORD,MAX_SLEEP
from src.utils.logger import adnic_logger

# Page object for the login page
# *** This is the standard login page structure for the company portal (this sample case ADNIC company) entry, ***
class LoginPage:
    def __init__(self, page):
        self.page = page

    async def login(self):
        await self.page.goto("https://www.adnicinsure.com/index.aspx", timeout=60000)

        adnic_logger.info("browser opened")

        #group insurance
        await self.page.click('//*[@id="btn_quote"]')
        adnic_logger.info("clicked on group insurance")
        await self.page.wait_for_load_state('networkidle')

        # Enter email and password
        await self.page.fill('//*[@id="txt_uname"]', ADNIC_USERNAME)
        await asyncio.sleep(MAX_SLEEP)
        await self.page.fill('//*[@id="txt_pwd"]', ADNIC_PASSWORD)

        adnic_logger.info("Email and password entered")

        # # Solve CAPTCHA
        # captcha_sitekey = await self.page.get_attribute('.g-recaptcha', 'data-sitekey')
        # page_url = "https://partneruae.nlicgulf.com/Portal/"
        # captcha_solution = await solve_captcha(captcha_sitekey, page_url)

        # await self.page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{captcha_solution}";')

        # Submit the login form
        await self.page.click('//*[@id="btn_signin"]')
        adnic_logger.info("Sign in button clicked")
        await self.page.wait_for_load_state('networkidle')
