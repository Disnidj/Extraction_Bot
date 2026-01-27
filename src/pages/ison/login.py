import asyncio
from twocaptcha import TwoCaptcha
import aiofiles
from src.utils.load_yaml import ISON_EMAIL,ISON_PASSWORD
# from src.utils.support_functions import screenshot_and_compare

class Login:
    def __init__(self, page):
        self.page = page

    async def perform_login(self):
        try:
            await self.page.goto("https://ison.dubins.ae/")
            await self.page.wait_for_load_state('networkidle')

            await self.page.locator("#txt_userName").fill(ISON_EMAIL)
            await self.page.locator("#txt_password").fill(ISON_PASSWORD)

            captcha_image = await self.page.locator("#img").screenshot()

            # Asynchronously write the screenshot to a file
            async with aiofiles.open('captcha.png', 'wb') as file:
                await file.write(captcha_image)

            # Initialize TwoCaptcha solver
            solver = TwoCaptcha('7da6201c72dca5a9798203eec1d6bb66')

            # Solve the CAPTCHA using the file
            result = await asyncio.to_thread(solver.normal, 'captcha.png')
            captcha_code = result['code']
            print("Captcha Code :", captcha_code)

            await self.page.locator("#txt_captcha").fill(captcha_code)
            await self.page.locator("#btn_proceed").wait_for(state="visible")
            await self.page.locator("#btn_proceed").click()

            await asyncio.sleep(3)

            if await self.page.locator('//*[@id="navbarSupportedContent"]/ul/ul[4]').is_visible():
                print("Login successful!")
                await asyncio.sleep(10)
                # await screenshot_and_compare(self.page, "ison", "ISON_1")
                return True
            else:
                print("Retrying CAPTCHA...")
                await asyncio.sleep(1)
                return False

        except Exception as e:
            print(f"Failed to capture or read CAPTCHA: {e}")
            await asyncio.sleep(3)
