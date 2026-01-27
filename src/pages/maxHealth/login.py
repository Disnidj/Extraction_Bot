# import patchright as playwright
from src.utils.load_yaml import MAXHEALTH_EMAIL, MAXHEALTH_PASSWORD
import asyncio
from src.utils.logger import maxhealth_logger

class Login:
    def __init__(self, page):
        self.page = page

    async def perform_login(self, df1):
        try:
            await self.page.wait_for_load_state('networkidle')
            await self.page.goto("https://portal.maxhealth.ae/auth/login")
            await self.page.wait_for_load_state('networkidle')

            # Enter login credentials
            await self.page.locator("#mui-1").fill(MAXHEALTH_EMAIL)
            maxhealth_logger.info("Email entered")
            await self.page.locator("#mui-2").fill(MAXHEALTH_PASSWORD)
            maxhealth_logger.info("Password entered")

            # Click login-in button
            await self.page.locator("#mui-3").click()

            await asyncio.sleep(5)

            next_page_element = self.page.locator("text=New Case")

            if await next_page_element.is_visible():
                maxhealth_logger.info("logged in successfully")
                return True
            else:
                maxhealth_logger.error("Error occured during log in")
                email = df1[df1['KEY'] == "Email"]['VALUE'].values[0]
                error = "Failed to log in"
                # update_error_log_table(var_req, "MaxHealth", email , error)
                # update_request_status(var_req, "Failed")
                return False

        except Exception as e:
            maxhealth_logger.error(f"log in failed - {e}")
            email = df1[df1['KEY'] == "Email"]['VALUE'].values[0]
            error = "Failed to log in"
            # update_error_log_table(var_req, "MaxHealth", email , error)
            # update_request_status(var_req, "Failed")
            return False
