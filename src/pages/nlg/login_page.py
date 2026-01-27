# src/pages/nlg/login_page.py
import asyncio
from src.utils.capcha_solver import solve_captcha
from src.utils.load_yaml import NLG_USERNAME, NLG_PASSWORD, MAX_SLEEP, SCREENSHOTS_DIR
from src.utils.logger import nlg_logger


class LoginPage:
    def __init__(self, page):
        self.page = page

    async def login(self):
        await self.page.goto("https://partneruae.nlicgulf.com/Portal/", timeout=60000)

        nlg_logger.debug("browser opened")

        # Enter email and password
        await self.page.fill('input[name="UserName"]', NLG_USERNAME)
        await asyncio.sleep(MAX_SLEEP)
        await self.page.fill('input[name="Password"]', NLG_PASSWORD)
        nlg_logger.debug("email and password entered")

        # Solve CAPTCHA
        captcha_sitekey = await self.page.get_attribute('.g-recaptcha', 'data-sitekey')
        page_url = "https://partneruae.nlicgulf.com/Portal/"
        captcha_solution = await solve_captcha(captcha_sitekey, page_url)

        await self.page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{captcha_solution}";')

        # Submit the login form
        await self.page.click('input[name="btnLogIn"]')
        nlg_logger.debug("captcha solved and pressed login button")
        await self.page.wait_for_load_state('networkidle')

        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(MAX_SLEEP)

        if await self.page.locator("#ContentBoady1_btn_sme").is_visible():
            nlg_logger.debug("Logged in successfully")
            return True
        
        else:
            nlg_logger.error("An error occurred during the login process")

            screenshot_path = f"{SCREENSHOTS_DIR}/login_error.png"
            await self.page.screenshot(path=screenshot_path)
            print(f"Screenshot saved at {screenshot_path}")
            
            insurance_name = "NLGIC"
            saved_msg = f"Stopped process due to an error"
            
            return False

