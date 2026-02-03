"""
ADNIC Authentication Module

Handles:
1. Browser-based login to ADNIC portal
2. Session establishment via census file upload
3. Provides authenticated page context for API calls

Unlike Takaful (JWT token), ADNIC uses session cookies that require:
- Login via browser
- Form submission with census file to get valid memid
- Maintain browser context for API calls
"""

from patchright.async_api import Playwright, Page, BrowserContext
from src.pages.adnic.login_page import LoginPage
from src.utils.logger import adnic_logger
from src.utils.load_yaml import ADNIC_GENERATED_CENSUS_DIR
import asyncio
import os


class ADNICAuth:
    """
    Handles ADNIC authentication and session establishment.
    
    ADNIC requires browser-based authentication:
    1. Login with credentials
    2. Fill company registration form
    3. Upload census file (creates memid for session)
    4. Navigate to ProductDetails page
    
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
        Perform browser login to ADNIC portal.
        
        Returns:
            bool: True if login successful
        """
        print("\n🔐 Step 1: Logging into ADNIC portal...")
        
        try:
            args = ["--disable-blink-features=AutomationControlled"]
            self.browser = await self.playwright.chromium.launch(headless=False, args=args)
            self.context = await self.browser.new_context()
            self.context.set_default_timeout(60000)
            self.page = await self.context.new_page()
            
            # Handle new pages/popups
            new_page = None
            def handle_page(new_p):
                nonlocal new_page
                print(f"   🔔 New page detected: {new_p.url}")
                new_page = new_p
            
            self.context.on("page", handle_page)
            
            # Perform login
            login_page = LoginPage(self.page)
            await login_page.login()
            
            # If new page opened, switch to it
            if new_page:
                print(f"   ⚠️ Login opened new page, switching...")
                await self.page.close()
                self.page = new_page
            
            adnic_logger.info("✓ Login successful")
            print("   ✓ Login successful!")
            print(f"   Current URL: {self.page.url}")
            
            return True
            
        except Exception as e:
            adnic_logger.error(f"Login failed: {e}")
            print(f"   ❌ Login failed: {e}")
            return False
    
    async def fill_company_form(self) -> bool:
        """
        Fill the company registration form with dummy data (Step 2).
        """
        print("📝 Step 2: Filling company registration form...")
        
        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(0.5)
            
            if "CompanyRegistration" not in self.page.url:
                print(f"   ⚠️ Not on registration page")
                return False
            
            # Fill form fields rapidly
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_CompanyName"]').fill("API Extraction Test Company")
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_buisnessNature"]').select_option(label="Other Services & Activities")
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_City"]').select_option("Dubai")
            await asyncio.sleep(0.8)  # Wait for location field to be ready after city selection
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_location"]').fill("Dubai")
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_contactperson"]').fill("Test Contact")
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_ContactNumber"]').fill("0501234567")
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_email"]').fill("test@test.com")
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_NewRenew"]').select_option("New")
            print("   ✓ Form fields filled")
            
            # Click NEXT
            submit_btn = self.page.locator('//*[@id="ContentPlaceHolder1_btn_submit"]')
            await submit_btn.wait_for(state="visible", timeout=10000)
            await submit_btn.click()
            
            await self.page.wait_for_load_state('networkidle', timeout=30000)
            await asyncio.sleep(1)
            
            print(f"   ✓ Navigated to: {self.page.url}")
            return True
            
        except Exception as e:
            adnic_logger.error(f"Error filling company form: {e}")
            print(f"   ❌ Error: {e}")
            return False
    
    async def upload_census_file(self) -> bool:
        """
        Upload census file (Step 3) - REQUIRED for session memid.
        """
        print("📁 Step 3: Uploading census file...")
        
        try:
            census_path = os.path.join(ADNIC_GENERATED_CENSUS_DIR, "adnic_census.xlsx")
            
            if not os.path.exists(census_path):
                print(f"   ❌ Census file not found: {census_path}")
                return False
            
            print(f"   Using census file: {census_path}")
            
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(0.5)
            
            # Upload file
            await self.page.locator('//*[@id="ContentPlaceHolder1_fileUpload_member"]').set_input_files(census_path, timeout=80000)
            print("   ✓ File selected")
            await asyncio.sleep(0.5)
            
            # Click upload button
            await self.page.locator('//*[@id="ContentPlaceHolder1_but_uploadUpload"]').click()
            print("   ✓ Upload button clicked")
            
            # Wait for upload to complete
            await self.page.wait_for_load_state('networkidle', timeout=60000)
            await asyncio.sleep(1)
            
            # Handle any alert
            try:
                alert_panel = self.page.locator('//*[@id="ContentPlaceHolder1_pnl_Error"]/div')
                if await alert_panel.is_visible(timeout=2000):
                    await self.page.locator('//*[@id="ContentPlaceHolder1_ImageButton1"]').click()
                    print("   ⚠️ Alert closed")
            except:
                pass
            
            await asyncio.sleep(0.5)
            
            print("   ✓ Census file uploaded!")
            return True
            
        except Exception as e:
            adnic_logger.error(f"Error uploading census: {e}")
            print(f"   ❌ Error: {e}")
            return False
    
    async def process_health_questions(self) -> bool:
        """
        Process member details and health questions (Step 4).
        """
        print("🏥 Step 4: Processing member details / health questions...")
        
        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(0.5)
            
            current_url = self.page.url
            print(f"   Current URL: {current_url}")
            
            # Click NEXT on UploadMemberDetails page
            if "UploadMemberDetails" in current_url:
                print("   📋 On member details page, clicking NEXT...")
                try:
                    next_btn = self.page.locator('//*[@id="ContentPlaceHolder1_btn_submit"]')
                    await next_btn.wait_for(state="visible", timeout=10000)
                    await next_btn.click()
                    await self.page.wait_for_load_state('networkidle')
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"   ⚠️ Could not click NEXT: {e}")
            
            # Check if already on ProductDetails
            if "ProductDetails" in self.page.url:
                print("   ✓ Already on ProductDetails page")
                return True
            
            # Check for health questions
            health_questions = [
                '//*[@id="ContentPlaceHolder1_ddl_status01"]',
                '//*[@id="ContentPlaceHolder1_ddl_status02"]',
                '//*[@id="ContentPlaceHolder1_ddl_status03"]',
                '//*[@id="ContentPlaceHolder1_ddl_status04"]',
                '//*[@id="ContentPlaceHolder1_ddl_status05"]',
                '//*[@id="ContentPlaceHolder1_ddl_status06"]',
                '//*[@id="ContentPlaceHolder1_ddl_status07"]',
                '//*[@id="ContentPlaceHolder1_ddl_status08"]',
            ]
            
            first_question = self.page.locator(health_questions[0])
            has_health_questions = await first_question.is_visible(timeout=2000)
            
            if has_health_questions:
                print("   📋 Answering health questions...")
                # Answer all questions rapidly without individual sleeps
                for selector in health_questions:
                    try:
                        question = self.page.locator(selector)
                        if await question.is_visible(timeout=500):
                            await question.select_option("No")
                    except:
                        pass
                
                print("   ✓ Health questions answered")
                await self.page.locator('//*[@id="ContentPlaceHolder1_btn_submit"]').click()
                await self.page.wait_for_load_state('networkidle')
                await asyncio.sleep(1)
            else:
                print("   ✓ No health questions on this page")
            
            # Handle policy date if present
            try:
                policy_date_field = self.page.locator('//*[@id="ContentPlaceHolder1_Txt_pSdate"]')
                if await policy_date_field.is_visible(timeout=1500):
                    await policy_date_field.evaluate("el => el.removeAttribute('disabled')")
                    await policy_date_field.evaluate("el => el.removeAttribute('readonly')")
                    await policy_date_field.fill("01-Feb-2026")
                    print("   ✓ Policy date set")
            except:
                pass
            
            # Select broker commission if present
            try:
                broker_field = self.page.locator('//*[@id="ContentPlaceHolder1_brk_Mar"]')
                if await broker_field.is_visible(timeout=1000):
                    await broker_field.select_option(index=1)
                    print("   ✓ Broker commission selected")
            except:
                pass
            
            # Click submit if button is visible
            try:
                submit_btn = self.page.locator('//*[@id="ContentPlaceHolder1_btn_submit"]')
                if await submit_btn.is_visible(timeout=1000):
                    await submit_btn.click()
                    await self.page.wait_for_load_state('networkidle')
                    await asyncio.sleep(0.5)
            except:
                pass
            
            print("   ✓ Step 4 completed!")
            return True
            
        except Exception as e:
            adnic_logger.error(f"Error on health questions: {e}")
            print(f"   ❌ Error: {e}")
            return False
    
    async def navigate_to_product_details(self) -> bool:
        """
        Navigate to ProductDetails page (Step 5).
        """
        print("📄 Step 5: Navigating to ProductDetails page...")
        
        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(0.5)
            
            current_url = self.page.url
            print(f"   Current URL: {current_url}")
            
            if "ProductDetails" in current_url:
                print("   ✓ Already on ProductDetails page!")
                self._extract_memid(current_url)
                return True
            
            # Try clicking links
            category_links = [
                '//a[contains(@href, "ProductDetails")]',
                '//a[contains(text(), "Category")]',
                '//*[@id="ContentPlaceHolder1_btn_submit"]',
            ]
            
            for link in category_links:
                try:
                    if await self.page.locator(link).is_visible(timeout=1000):
                        await self.page.locator(link).click()
                        await self.page.wait_for_load_state('networkidle')
                        await asyncio.sleep(0.5)
                        break
                except:
                    continue
            
            current_url = self.page.url
            if "ProductDetails" in current_url:
                print("   ✓ On ProductDetails page!")
                self._extract_memid(current_url)
                return True
            
            # Try direct navigation
            import re
            memid_match = re.search(r'memid=(\d+)', current_url)
            memid = memid_match.group(1) if memid_match else "0"
            
            print(f"   Trying direct navigation with memid={memid}...")
            await self.page.goto(
                f"https://www.adnicinsure.com/Eng/ProductDetails.aspx?memid={memid}&Type=New",
                wait_until="networkidle", 
                timeout=60000
            )
            await asyncio.sleep(0.5)
            
            self._extract_memid(self.page.url)
            return "ProductDetails" in self.page.url
            
        except Exception as e:
            adnic_logger.error(f"Error navigating to ProductDetails: {e}")
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
        2. Fill company form
        3. Upload census file
        4. Process health questions
        5. Navigate to ProductDetails
        
        Returns:
            Page: Authenticated Playwright page ready for API calls
        """
        # Step 1: Login
        if not await self.login():
            raise Exception("Login failed")
        
        # Step 2: Fill company form
        await self.fill_company_form()
        
        # Step 3: Upload census
        await self.upload_census_file()
        
        # Step 4: Health questions
        await self.process_health_questions()
        
        # Step 5: Navigate to ProductDetails
        if not await self.navigate_to_product_details():
            raise Exception("Failed to reach ProductDetails page")
        
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
