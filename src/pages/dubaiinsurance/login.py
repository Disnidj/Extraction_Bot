import asyncio
from twocaptcha import TwoCaptcha
from src.utils.load_yaml import DUBAIINSURANCE_USERNAME, DUBAIINSURANCE_PASSWORD, TWO_CAPTCHA_API_KEY
import aiofiles
from src.utils.logger import dubaiinsurance_logger as logger


class Login:
    def __init__(self, page):
        self.page = page

    async def perform_login(self):
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Login attempt {attempt + 1}")
                
                # Navigate to login page
                await self.page.goto("https://dubaicare.dubins.ae/")
                await self.page.wait_for_load_state('networkidle')
                
                # Click login button
                await self.page.locator("#btn_quote").click()
                await asyncio.sleep(2)

                # Fill credentials
                await self.page.locator("#txt_uname").fill(DUBAIINSURANCE_USERNAME)
                await asyncio.sleep(1)  # Wait after username
                
                await self.page.locator("#txt_pwd").fill(DUBAIINSURANCE_PASSWORD)
                await asyncio.sleep(1)  # Wait after password

                # Handle CAPTCHA
                captcha_image = await self.page.locator("#img").screenshot()
                async with aiofiles.open('captcha.png', 'wb') as file:
                    await file.write(captcha_image)

                solver = TwoCaptcha(TWO_CAPTCHA_API_KEY)
                result = await asyncio.to_thread(solver.normal, 'captcha.png')
                captcha_code = result['code']
                
                print(f"Captcha Code: {captcha_code}")
                logger.info(f"Captcha Code: {captcha_code}")

                # Fill CAPTCHA and wait for it to be properly entered
                await self.page.locator("#txt_captcha").clear()  # Clear first
                await asyncio.sleep(0.5)
                
                await self.page.locator("#txt_captcha").fill(captcha_code)
                await asyncio.sleep(2)  # Wait for CAPTCHA to be fully entered
                
                # Verify CAPTCHA was entered correctly
                entered_value = await self.page.locator("#txt_captcha").input_value()
                if entered_value != captcha_code:
                    logger.warning(f"CAPTCHA mismatch: entered {entered_value}, expected {captcha_code}")
                    continue
                
                logger.info(f"CAPTCHA entered successfully: {entered_value}")

                # Submit login
                await self.page.locator("#btn_signin").click()
                logger.info("Clicked Sign In")

                # Wait longer for page to process login
                await asyncio.sleep(8)
                await self.page.wait_for_load_state('networkidle', timeout=15000)

                # Check for successful login
                if await self.is_login_successful():
                    print("Login successful!")
                    logger.info("Login successful!")
                    return True
                else:
                    logger.info(f"Login attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Login attempt {attempt + 1} error: {e}")
                await asyncio.sleep(3)

        logger.error("All login attempts failed")
        return False

    async def is_login_successful(self):
        """Check if login was successful"""
        try:
            # Check if we're still on login page (login failed)
            if await self.page.locator("#txt_uname").is_visible(timeout=3000):
                logger.info("Login failed: Still on login page")
                return False
            
            # Check for success indicators
            success_selectors = [
                "iframe[name=\"content\"]",
                "#MyIframe1",
                "text=SME Quotation",
                "text=Dashboard",
                "text=Quotation"
            ]
            
            for selector in success_selectors:
                try:
                    if await self.page.locator(selector).is_visible(timeout=3000):
                        logger.info(f"Login success: Found {selector}")
                        return True
                except:
                    continue
            
            # Check URL change
            current_url = self.page.url
            if current_url != "https://dubaicare.dubins.ae/" and "login" not in current_url.lower():
                logger.info(f"Login success: URL changed to {current_url}")
                return True
                
            logger.info("Login check: No success indicators found")
            return False
            
        except Exception as e:
            logger.error(f"Error checking login success: {e}")
            return False