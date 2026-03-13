"""
Liva Insurance Authentication Module

Handles browser-based login and session establishment for Liva Insurance portal.
Based on the NLG portal login flow since the portal is the same system (rebranded).

Flow:
1. Launch browser & navigate to portal
2. Login with credentials (captcha solving)
3. Select SME + Region → Submit
4. Fill company registration form with dummy data
5. Upload census file
6. Answer health questions
7. Navigate to CATENH2.aspx (Product Details page)
8. Return authenticated page for API calls
"""

from patchright.async_api import Playwright, Page, BrowserContext
from src.utils.load_yaml import IS_HEADLESS, LIVA_INSURANCE_USERNAME, LIVA_INSURANCE_PASSWORD, LIVA_INSURANCE_GENERATED_CENSUS_DIR
from src.utils.logger import liva_insurance_logger
from src.utils.capcha_solver import solve_captcha
from .mapping import PORTAL_LOGIN_URL
import asyncio
import os


class LivaInsuranceAuth:
    """
    Handles Liva Insurance authentication and session establishment.

    The portal is the same system as the old NLGIC portal (rebranded to Liva Insurance).
    Uses browser-based authentication:
    1. Login with credentials + captcha
    2. Select SME product type + region
    3. Fill company registration form
    4. Upload census file
    5. Navigate through health questions
    6. Reach the Product Details (CATENH2) page

    The page context maintains cookies required for API calls.
    """

    def __init__(self, playwright: Playwright):
        self.playwright = playwright
        self.browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.memid: str = None


    async def login(self) -> bool:
        """
        Perform browser login to Liva Insurance portal.
        Uses same login mechanism as NLG (captcha solving).
        """
        print("\n🔐 Step 1: Logging into Liva Insurance portal...")

        try:
            args = ["--disable-blink-features=AutomationControlled"]
            self.browser = await self.playwright.chromium.launch(headless=IS_HEADLESS, args=args)
            self.context = await self.browser.new_context()
            self.context.set_default_timeout(60000)
            self.page = await self.context.new_page()

            await self.page.goto(PORTAL_LOGIN_URL, timeout=60000)
            liva_insurance_logger.debug("Browser opened, navigated to login page")

            # Enter credentials
            await self.page.fill('input[name="UserName"]', LIVA_INSURANCE_USERNAME)
            await asyncio.sleep(1)
            await self.page.fill('input[name="Password"]', LIVA_INSURANCE_PASSWORD)
            liva_insurance_logger.debug("Username and password entered")

            # Solve CAPTCHA if present
            try:
                captcha_element = self.page.locator('.g-recaptcha')
                if await captcha_element.is_visible(timeout=3000):
                    captcha_sitekey = await captcha_element.get_attribute('data-sitekey')
                    captcha_solution = await solve_captcha(captcha_sitekey, PORTAL_LOGIN_URL)
                    await self.page.evaluate(
                        f'document.getElementById("g-recaptcha-response").innerHTML = "{captcha_solution}";'
                    )
                    liva_insurance_logger.debug("Captcha solved")
            except Exception as e:
                liva_insurance_logger.debug(f"No captcha or captcha handling skipped: {e}")

            # Submit login form
            await self.page.click('input[name="btnLogIn"]')
            liva_insurance_logger.debug("Login button clicked")
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)

            liva_insurance_logger.info("✓ Login successful")
            print("   ✓ Login successful!")
            print(f"   Current URL: {self.page.url}")

            return True

        except Exception as e:
            liva_insurance_logger.error(f"Login failed: {e}")
            print(f"   ❌ Login failed: {e}")
            return False

    async def select_sme_and_region(self) -> bool:
        """
        Step 2: Select SME product type and Region (Dubai).
        Page 1 of the portal flow.
        """
        print("📋 Step 2: Selecting SME and Region...")

        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            # Click SME button
            sme_button = self.page.locator("#ContentBoady1_btn_sme")
            if await sme_button.is_visible(timeout=10000):
                await sme_button.hover()
                await sme_button.click()
                liva_insurance_logger.debug("SME button clicked")
            else:
                liva_insurance_logger.debug("SME button not found, trying alternative...")
                # Try clicking SME by text
                await self.page.click('text=SME')

            await asyncio.sleep(2)

            # Select Region = Dubai
            region_dropdown = self.page.locator("#ContentBoady1_ddl_region")
            if await region_dropdown.is_visible(timeout=5000):
                await region_dropdown.select_option("Dubai")
                liva_insurance_logger.debug("Region 'Dubai' selected")
            await asyncio.sleep(1)

            # Click SUBMIT
            await self.page.get_by_role("button", name="SUBMIT").click()
            liva_insurance_logger.debug("SUBMIT button clicked")

            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)

            print("   ✓ SME and Region selected")
            print(f"   Current URL: {self.page.url}")
            return True

        except Exception as e:
            liva_insurance_logger.error(f"Error selecting SME/Region: {e}")
            print(f"   ❌ Error: {e}")
            return False

    async def fill_company_form(self) -> bool:
        """
        Step 3: Fill company registration form with dummy data.
        """
        print("📝 Step 3: Filling company registration form...")

        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(1)

            # Fill form fields
            # Company Name
            await self.page.get_by_placeholder("Company Name").fill("API Extraction Test Company")
            await asyncio.sleep(0.5)

            await self.page.locator("#ContentBoady1_ddl_buisnessNature").select_option(
                label="Other Services & Activities"
            )
            liva_insurance_logger.debug("Business Nature dropdown selected")
            await asyncio.sleep(0.5)

            # City dropdown
            try:
                city_dropdown = self.page.locator("#ContentBoady1_ddl_City")
                if await city_dropdown.is_visible(timeout=2000):
                    await city_dropdown.select_option("Dubai")
                    liva_insurance_logger.debug("City selected")
                    await asyncio.sleep(0.5)
            except:
                pass

            # Location field
            try:
                location_field = self.page.get_by_placeholder("Location")
                if await location_field.is_visible(timeout=2000):
                    await location_field.fill("Dubai")
                    await asyncio.sleep(0.5)
            except:
                pass

            # Broker Contact Person
            await self.page.get_by_placeholder("Contact Person Name").fill("Test Contact")
            await asyncio.sleep(0.5)

            # Contact Number
            await self.page.get_by_placeholder("Contact Number").fill("0561234567")
            await asyncio.sleep(0.5)

            # Email
            await self.page.get_by_placeholder("E-Mail").fill("test@test.com")
            await asyncio.sleep(0.5)

            # Are you the holding broker? = No
            try:
                holding_broker = self.page.locator("#ContentBoady1_ddl_holdingBroker")
                if await holding_broker.is_visible(timeout=2000):
                    await holding_broker.select_option("No")
                    await asyncio.sleep(0.5)
            except:
                pass

            liva_insurance_logger.info("All form fields filled successfully")
            print("   ✓ Form fields filled")

            # Click Proceed
            await self.page.get_by_role("button", name="Proceed >>>").click()
            liva_insurance_logger.debug("Proceed button clicked")

            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            print(f"   ✓ Navigated to: {self.page.url}")
            return True

        except Exception as e:
            liva_insurance_logger.error(f"Error filling company form: {e}")
            print(f"   ❌ Error: {e}")
            return False

    async def upload_census_file(self) -> bool:
        """
        Step 4: Upload census file (required for session memid generation).
        """
        print("📁 Step 4: Uploading census file...")

        try:
            census_path = os.path.join(LIVA_INSURANCE_GENERATED_CENSUS_DIR, "MemberUpload.xlsx")

            if not os.path.exists(census_path):
                print(f"   ❌ Census file not found: {census_path}")
                return False

            print(f"   Using census file: {census_path}")

            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(1)

            # Upload file
            await self.page.locator("#ContentBoady1_fileUpload_member").set_input_files(
                census_path, timeout=80000
            )
            print("   ✓ File selected")
            await asyncio.sleep(1)

            # Click Upload button
            await self.page.get_by_role("button", name="Upload").click()
            print("   ✓ Upload button clicked")

            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)

            # Handle any alert
            try:
                alert_panel = self.page.locator("#ContentBoady1_pnl_Error > div")
                if await alert_panel.is_visible(timeout=2000):
                    await self.page.locator("#ContentBoady1_ImageButton1").click()
                    print("   ⚠️ Alert closed")
                    await asyncio.sleep(1)
            except:
                pass

            print("   ✓ Census file uploaded!")
            return True

        except Exception as e:
            liva_insurance_logger.error(f"Error uploading census: {e}")
            print(f"   ❌ Error: {e}")
            return False

    async def process_health_questions(self) -> bool:
        """
        Step 5: Answer health/medical questions with 'No' and proceed.
        """
        print("🏥 Step 5: Processing health questions...")

        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            # Health question selectors (same as NLG portal)
            health_questions = [
                "#ContentBoady1_ddl_above65",
                "#ContentBoady1_ddl_status03",
                "#ContentBoady1_ddl_status04",
                "#ContentBoady1_ddl_status02",
                "#ContentBoady1_ddl_status05",
                "#ContentBoady1_ddl_status01",
                "#ContentBoady1_ddl_status08",
                "#ContentBoady1_ddl_status06",
                "#ContentBoady1_ddl_status07",
                "#ContentBoady1_ddl_ailment",
            ]

            answered_count = 0
            for selector in health_questions:
                try:
                    await self.page.locator(selector).select_option("No")
                    answered_count += 1
                    await asyncio.sleep(0.5)
                except:
                    pass

            liva_insurance_logger.info(f"Health questions answered: {answered_count}")
            print(f"   ✓ Answered {answered_count} health questions with 'No'")

            # Click Next
            await self.page.get_by_role("button", name="Next").click()
            liva_insurance_logger.debug("Next button clicked")

            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)

            print(f"   ✓ Current URL: {self.page.url}")
            return True

        except Exception as e:
            liva_insurance_logger.error(f"Error on health questions: {e}")
            print(f"   ❌ Error: {e}")
            return False

    async def navigate_to_product_details(self) -> bool:
        """
        Step 6: Ensure we're on the CATENH2 (Product Details) page.
        """
        print("📄 Step 6: Navigating to Product Details page...")

        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(1)

            current_url = self.page.url
            print(f"   Current URL: {current_url}")

            if "CATENH2" in current_url or "ProductDetails" in current_url:
                print("   ✓ Already on Product Details page!")
                self._extract_memid(current_url)
                return True

            # Try clicking category/product links
            category_links = [
                '//a[contains(@href, "CATENH2")]',
                '//a[contains(@href, "ProductDetails")]',
                '//a[contains(text(), "Category")]',
            ]

            for link in category_links:
                try:
                    if await self.page.locator(link).is_visible(timeout=1000):
                        await self.page.locator(link).click()
                        await self.page.wait_for_load_state('networkidle')
                        await asyncio.sleep(1)
                        break
                except:
                    continue

            current_url = self.page.url
            if "CATENH2" in current_url:
                print("   ✓ On Product Details page!")
                self._extract_memid(current_url)
                return True

            # Try submit button if still not on the right page
            try:
                submit_btn = self.page.locator("#ContentBoady1_btn_submit")
                if await submit_btn.is_visible(timeout=2000):
                    await submit_btn.click()
                    await self.page.wait_for_load_state('networkidle')
                    await asyncio.sleep(2)
            except:
                pass

            current_url = self.page.url
            self._extract_memid(current_url)

            if "CATENH2" in current_url:
                print("   ✓ On Product Details page!")
                return True

            print(f"   ⚠️ Final URL: {current_url}")
            return "CATENH2" in current_url or "SMECategories" in current_url

        except Exception as e:
            liva_insurance_logger.error(f"Error navigating to Product Details: {e}")
            print(f"   ❌ Error: {e}")
            return False

    def _extract_memid(self, url: str):
        """Extract memid from URL."""
        import re
        match = re.search(r'memid=(\d+)', url)
        if match:
            self.memid = match.group(1)
            print(f"   📌 Session memid: {self.memid}")

    async def establish_session(self) -> Page:
        """
        Complete authentication flow and return authenticated page.

        Full flow:
        1. Login
        2. Select SME + Region
        3. Fill company form
        4. Upload census file
        5. Process health questions
        6. Navigate to Product Details page

        Returns:
            Page: Authenticated Playwright page ready for API calls
        """
        # Step 1: Login
        if not await self.login():
            raise Exception("Login failed")

        # Step 2: Select SME and Region
        if not await self.select_sme_and_region():
            raise Exception("Failed to select SME and Region")

        # Step 3: Fill company form
        if not await self.fill_company_form():
            raise Exception("Failed to fill company form")

        # Step 4: Upload census
        if not await self.upload_census_file():
            raise Exception("Failed to upload census file")

        # Step 5: Health questions
        await self.process_health_questions()

        # Step 6: Navigate to Product Details
        if not await self.navigate_to_product_details():
            raise Exception("Failed to reach Product Details page")

        print(f"\n   🌐 Final URL: {self.page.url}")
        return self.page

    async def close(self):
        """Close browser and cleanup."""
        print("\n🌐 Closing browser...")
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except:
            pass
