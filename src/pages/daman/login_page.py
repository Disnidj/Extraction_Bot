import asyncio
from src.utils.load_yaml import DAMAN_USERNAME, DAMAN_PASSWORD
from src.utils.logger import daman_logger

class LoginPage:
    def __init__(self, page):
        self.page = page

    async def login(self):
        try:
            # Navigate to Daman Health login page
            daman_logger.debug("Login page (Daman)")
            await self.page.goto("https://www.damanhealth.ae/en", timeout=300000)
            # await self.page.wait_for_load_state('networkidle')
            daman_logger.debug("Page loaded successfully.")

            # Click the login button
            await self.page.wait_for_selector(".header-login", timeout=10000)
            await self.page.click(".header-login")
            daman_logger.debug("Login button clicked.")

            # Handle new window opening issue
            async def handle_popup(popup):
                daman_logger.debug("Popup detected. Redirecting to the same page.")
                await self.page.bring_to_front()  # Bring main page to the front
                await self.page.goto(popup.url)  # Navigate in the same window instead of opening a new one

            self.page.on("popup", handle_popup)  # Detect popups and handle them

            # Click broker login link (Force navigation in the same tab)
            await self.page.evaluate('document.querySelector("a[href*=\'loadBrokerLoginForm\']").target = "_self";')
            await self.page.click("//a[contains(@href, '/eDamanApp/loadBrokerLoginForm.action')]")

            await self.page.wait_for_load_state('networkidle')
            daman_logger.debug("Broker login page opened.")

            # Log username and password for debugging (ensure it's not exposed in production logs)
            daman_logger.debug(f"Using Username: {DAMAN_USERNAME}")

            # Fill in username
            await self.page.wait_for_selector('input#userName', timeout=10000)
            await self.page.fill('input#userName', DAMAN_USERNAME)
            daman_logger.debug("Username filled.")
            await asyncio.sleep(2)

            # Fill in password
            await self.page.wait_for_selector('input#password', timeout=10000)
            await self.page.fill('input#password', DAMAN_PASSWORD)
            daman_logger.debug("Password filled.")
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            # Click login button (Corrected XPath)
            await self.page.wait_for_selector('//*[@id="form-sign-in"]/a[1]/img')
            await self.page.click('//*[@id="form-sign-in"]/a[1]/img')
            await asyncio.sleep(2)
            await self.page.wait_for_load_state('networkidle')
            daman_logger.debug("Login button clicked.")
            

            # Wait for the page to load after login
            daman_logger.debug("Login completed successfully.")
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            return True

        except Exception as e:
            daman_logger.error(f"An error occurred during login: {e}")
