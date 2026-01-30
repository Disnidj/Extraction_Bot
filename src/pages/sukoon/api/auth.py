"""
Sukoon Authentication Module

Handles:
1. Browser-based login to Sukoon portal
2. Session establishment via census file upload
3. Provides authenticated page context for API calls

Sukoon requires session cookies + F5 security tokens:
- ASP.NET_SessionId for session tracking
- TS... cookies from F5 BIG-IP WAF
- Census must be uploaded for valid API responses
"""

from patchright.async_api import Playwright, Page, BrowserContext
from src.pages.sukoon.login_page import LoginPage
from src.utils.logger import sukoon_logger
from src.utils.load_yaml import SUKOON_GENERATED_CENSUS_DIR
import asyncio
import os


class SukoonAuth:
    """
    Handles Sukoon authentication and session establishment.
    
    Flow:
    1. Login with credentials
    2. Click CREATE to start new quote
    3. Fill company form with dummy data
    4. Upload census file
    5. Navigate to GenerateQuotes page (where API works)
    
    The page context maintains cookies required for API calls.
    """
    
    def __init__(self, playwright: Playwright):
        self.playwright = playwright
        self.browser = None
        self.context: BrowserContext = None
        self.page: Page = None
    
    async def login(self) -> bool:
        """
        Perform browser login to Sukoon portal.
        
        Returns:
            bool: True if login successful
        """
        print("\n🔐 Step 1: Logging into Sukoon portal...")
        
        try:
            args = ["--disable-blink-features=AutomationControlled"]
            self.browser = await self.playwright.chromium.launch(headless=False, args=args)
            self.context = await self.browser.new_context()
            self.context.set_default_timeout(60000)
            self.page = await self.context.new_page()
            
            # Use existing LoginPage
            login_page = LoginPage(self.page)
            login_result = await login_page.login()
            
            # Check if login was successful
            if login_result is False:
                print("   ❌ Login failed")
                return False
            
            # Verify login by checking for CREATE button
            try:
                create_btn = self.page.get_by_role("link", name="CREATE", exact=True)
                if await create_btn.is_visible(timeout=10000):
                    sukoon_logger.info("✓ Login successful - CREATE button visible")
                    print("   ✓ Login successful!")
                    return True
            except:
                pass
            
            sukoon_logger.info("✓ Login completed")
            print("   ✓ Login completed!")
            print(f"   Current URL: {self.page.url}")
            return True
            
        except Exception as e:
            sukoon_logger.error(f"Login failed: {e}")
            print(f"   ❌ Login failed: {e}")
            return False
    
    async def start_new_quote(self) -> bool:
        """
        Click CREATE to start new quote flow.
        """
        print("\n📝 Step 2: Starting new quote...")
        
        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(0.5)
            
            # Check if already on the company form or later stage
            if "GenerateQuotes" in self.page.url:
                print("   ✓ Already on GenerateQuotes page")
                return True
            
            # Click CREATE button
            create_btn = self.page.get_by_role("link", name="CREATE", exact=True)
            if await create_btn.is_visible(timeout=3000):
                await create_btn.click()
                sukoon_logger.debug("Clicked on Create Button")
                await self.page.wait_for_load_state('networkidle')
                await asyncio.sleep(0.5)
            
            print("   ✓ New quote started")
            print(f"   Current URL: {self.page.url}")
            return True
            
        except Exception as e:
            sukoon_logger.error(f"Error starting quote: {e}")
            print(f"   ⚠️ Note: {e}")
            return True  # Continue anyway
    
    async def fill_company_form(self, region: str = "Dubai") -> bool:
        """
        Fill company form with dummy data.
        
        Selectors from process_page.py:
        - Company Name: #ContentPlaceHolder1_txtCompanyName
        - Nature of Business: #ContentPlaceHolder1_divNatureOfBusiness -> //span[text()='value']
        - Region: #ContentPlaceHolder1_divRegion -> //span[text()='value']
        - Plan Options: #ContentPlaceHolder1_divProduct -> link role
        - Is Previous Insured: #ContentPlaceHolder1_divVirgin -> link "No" nth(4)
        """
        print("\n📝 Step 3: Filling company form...")
        
        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(0.5)
            
            # Fill Company Name quickly
            company_name_field = self.page.locator("#ContentPlaceHolder1_txtCompanyName")
            if await company_name_field.is_visible(timeout=3000):
                await company_name_field.fill("API Extraction Test Company")
                print("   ✓ Company name filled")
            else:
                print("   ⚠️ Company name field not visible - may already be filled")
            
            # Nature of Business - custom dropdown
            try:
                await self.page.locator("#ContentPlaceHolder1_divNatureOfBusiness").get_by_text("Please Select").first.click()
                await self.page.locator("//span[text()='Retail Sales']").click()
                print("   ✓ Business nature: Retail Sales")
            except Exception as e:
                print(f"   ⚠️ Business nature already set or error: {str(e)[:40]}")
            
            # Region - custom dropdown
            try:
                await self.page.locator("#ContentPlaceHolder1_divRegion").get_by_text("Please Select").first.click()
                await self.page.locator(f"//span[text()='{region}']").click()
                print(f"   ✓ Region: {region}")
            except Exception as e:
                print(f"   ⚠️ Region already set or error: {str(e)[:40]}")
            
            # Plan Options - custom dropdown (use link role like process_page.py)
            try:
                await self.page.locator("#ContentPlaceHolder1_divProduct").get_by_text("Please Select").first.click()
                await self.page.get_by_role("link", name="SME Medical Healthcare").click()
                print("   ✓ Plan: SME Medical Healthcare")
            except Exception as e:
                print(f"   ⚠️ Plan already set or error: {str(e)[:40]}")
            
            # Is Previous Insured - use nth(4) like process_page.py
            try:
                await self.page.locator("#ContentPlaceHolder1_divVirgin").get_by_text("Please Select").first.click()
                await self.page.get_by_role("link", name="No", exact=True).nth(4).click()
                print("   ✓ Previous insured: No")
            except Exception as e:
                print(f"   ⚠️ Previous insured already set or error: {str(e)[:40]}")
            
            # Short pause for stability
            await asyncio.sleep(0.5)
            print("   ✓ Company form completed!")
            return True
            
        except Exception as e:
            sukoon_logger.error(f"Error filling company form: {e}")
            print(f"   ❌ Error: {e}")
            return False
    
    async def upload_census_file(self) -> bool:
        """
        Upload census file - REQUIRED for valid API responses.
        
        Selector from process_page.py:
        - File input: #ContentPlaceHolder1_uploadFile
        - Upload button: button name="Upload"
        """
        print("\n📁 Step 4: Uploading census file...")
        
        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(0.5)
            
            # Look for census file
            census_path = os.path.join(SUKOON_GENERATED_CENSUS_DIR, "sukoon_census.xlsx")
            
            if not os.path.exists(census_path):
                print(f"   ⚠️ Census file not found: {census_path}")
                print("   → Continuing without census (API may return limited data)")
                return True  # Continue anyway
            
            print(f"   Using census file: {census_path}")
            
            # Upload file using exact selector from process_page.py
            file_input = self.page.locator("#ContentPlaceHolder1_uploadFile")
            if await file_input.is_visible(timeout=3000):
                await file_input.set_input_files(census_path)
                print("   ✓ File selected")
                await asyncio.sleep(0.5)
                
                # Click Upload button
                upload_btn = self.page.get_by_role("button", name="Upload")
                if await upload_btn.is_visible(timeout=2000):
                    await upload_btn.click()
                    print("   ✓ Upload button clicked")
                    await self.page.wait_for_load_state('networkidle', timeout=60000)
                    await asyncio.sleep(1)
            else:
                print("   ⚠️ File upload field not visible")
            
            print("   ✓ Census upload step completed!")
            return True
            
        except Exception as e:
            sukoon_logger.error(f"Error uploading census: {e}")
            print(f"   ❌ Error: {e}")
            return False
    
    async def navigate_to_generate_quotes(self) -> bool:
        """
        Navigate to the GenerateQuotes page where PopulateDDL works.
        """
        print("\n📄 Step 5: Navigating to GenerateQuotes page...")
        
        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(0.5)
            
            current_url = self.page.url
            print(f"   Current URL: {current_url}")
            
            if "GenerateQuotes" in current_url:
                print("   ✓ Already on GenerateQuotes page!")
                return True
            
            # Try clicking NEXT/Continue button to proceed
            try:
                next_btn = self.page.locator('//input[contains(@value, "Next")]').first
                if await next_btn.is_visible(timeout=1000):
                    await next_btn.click()
                    await self.page.wait_for_load_state('networkidle')
                    await asyncio.sleep(0.5)
                    print("   ✓ Clicked Next")
            except:
                pass
            
            # Check again
            if "GenerateQuotes" in self.page.url:
                print("   ✓ Navigated to GenerateQuotes page!")
                return True
            
            # Try direct navigation if we have the right context
            try:
                await self.page.goto(
                    "https://smeonline.sukoon.com/GenerateQuotes.aspx",
                    wait_until="networkidle",
                    timeout=30000
                )
                await asyncio.sleep(0.5)
                
                if "GenerateQuotes" in self.page.url:
                    print("   ✓ Direct navigation to GenerateQuotes successful!")
                    return True
            except Exception as e:
                print(f"   ⚠️ Direct navigation failed: {e}")
            
            print(f"   Current URL: {self.page.url}")
            return True  # Continue anyway
            
        except Exception as e:
            sukoon_logger.error(f"Error navigating: {e}")
            print(f"   ❌ Error: {e}")
            return False
    
    async def establish_session(self, region: str = "Dubai") -> Page:
        """
        Complete authentication flow and return authenticated page.
        
        Full flow:
        1. Login
        2. Start new quote
        3. Fill company form
        4. Upload census
        5. Navigate to GenerateQuotes
        
        Returns:
            Page: Authenticated Playwright page ready for API calls
        """
        # Step 1: Login
        if not await self.login():
            raise Exception("Login failed")
        
        # Step 2: Start new quote
        await self.start_new_quote()
        
        # Step 3: Fill company form
        await self.fill_company_form(region)
        
        # Step 4: Upload census (optional but recommended)
        await self.upload_census_file()
        
        # Step 5: Navigate to GenerateQuotes
        await self.navigate_to_generate_quotes()
        
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
