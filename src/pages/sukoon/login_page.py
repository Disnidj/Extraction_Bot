import asyncio
from src.utils.capcha_solver import solve_captcha
from src.utils.load_yaml import SUKOON_EMAIL, SUKOON_PASSWORD,MIN_SLEEP, MAX_SLEEP
from src.utils.logger import sukoon_logger
# from src.services.email_service.send_error_email import send_error_email


class LoginPage:
    def __init__(self, page):
        self.page = page

    async def login(self):
        await self.page.goto("https://smeonline.sukoon.com/login.aspx")
        await self.page.wait_for_load_state('networkidle')

        # Enter login credentials
        await self.page.locator("#txtUsernameEntry").fill(SUKOON_EMAIL)
        await asyncio.sleep(MIN_SLEEP)
        await self.page.locator("#txtPasswordEntry").fill(SUKOON_PASSWORD)
        await asyncio.sleep(MIN_SLEEP)
        
        # Click sign-in button
        await self.page.get_by_role("button", name="Sign in").click()
        sukoon_logger.debug("Clicked on Sign in Button")
        await self.page.wait_for_load_state('networkidle')

        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(MAX_SLEEP)

        if await self.page.get_by_role("link", name="CREATE", exact=True).is_visible():
            sukoon_logger.debug("Logged in successfully")
            return True
        
        # else:
        #     sukoon_logger.error("An error occurred during the login process")

        #     screenshot_path = f"{SCREENSHOTS_DIR}/login_error.png"
        #     await self.page.screenshot(path=screenshot_path)
        #     print(f"Screenshot saved at {screenshot_path}")
            
        #     insurance_name = "SUKOON"
        #     saved_msg = f"Stopped process due to an error"
            
        #     send_error_email(screenshot_path ,insurance_name, saved_msg)

        #     return False