import asyncio
from src.utils.capcha_solver import solve_captcha
from src.utils.load_yaml import ORIENT_EMIAL, ORIENT_PASSWORD,MAX_SLEEP
from src.utils.logger import orient_logger
# from src.services.email_service.send_error_email import send_error_email


class LoginPage:
    def __init__(self, page):
        self.page = page

    async def login(self):
        # Navigate to the login page
        await self.page.goto("https://quotator360.com/",timeout=60000)

        # wait untill fully load self.page
        await self.page.wait_for_load_state('networkidle')
        
        orient_logger.debug("Login Page Loaded")

        # Enter email and password
        await self.page.fill('input[name="Input.Email"]', ORIENT_EMIAL)
        await asyncio.sleep(1)
        
        orient_logger.debug("Email Filled ")
        
        await self.page.fill('input[name="Input.Password"]', ORIENT_PASSWORD)
        
        orient_logger.debug("Password Filled ")

        # Extract CAPTCHA site key from the self.page
        captcha_sitekey = await self.page.get_attribute('.g-recaptcha', 'data-sitekey')
        self.page_url = "https://auth.quotator360.com/" 

        # Solve CAPTCHA using 2Captcha
        captcha_solution = await solve_captcha(captcha_sitekey, self.page_url)

        # Inject the solved CAPTCHA into the self.page's hidden g-recaptcha-response input
        await self.page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{captcha_solution}";')
        
        orient_logger.debug("Captcha Solved ")

        # Submit the login form
        await self.page.click('button:has-text("Sign me in")')

        # Wait for the self.page to load completely
        await self.page.wait_for_load_state('networkidle')
        
        orient_logger.debug("Login Completed")
        await asyncio.sleep(MAX_SLEEP)

        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(MAX_SLEEP)
        # await asyncio.sleep(1000)

        if await self.page.locator('//*[@id="sidebar"]').is_visible():
            orient_logger.debug("Logged in successfully")
            return True
        
        # else:
        #     orient_logger.error("An error occurred during the login process")

        #     screenshot_path = f"{SCREENSHOTS_DIR}/login_error.png"
        #     await self.page.screenshot(path=screenshot_path)
        #     print(f"Screenshot saved at {screenshot_path}")
            
        #     insurance_name = "ORIENT"
        #     saved_msg = f"Stopped process due to an error"
            
            # send_error_email(screenshot_path ,insurance_name, saved_msg)

            return False