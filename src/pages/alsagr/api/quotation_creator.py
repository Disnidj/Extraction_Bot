"""
Al Sagr Quotation Creator

Handles creating a new quotation by filling the form fields.
This is a refactored version of the form filling logic from process_page.py,
designed to work with the API extraction flow.

Flow:
1. Navigate to SME → Quotation Information
2. Click "Add New Quotation"
3. Fill form with default/provided values
4. Save quotation (gets quotationId)
5. Navigate to Benefit Structure page

Key Difference from Old Code:
- Old code used census Excel data
- This uses minimal default values or provided input
- After quotation creation, uses API extraction instead of manual category filling
"""

import asyncio
import os
import time
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from src.utils.logger import alsagr_logger
from src.utils.load_yaml import MED_SLEEP, MAX_SLEEP, ALSAGR_TEMPLATES_DIR


# Default values for quotation creation
DEFAULT_QUOTATION_VALUES = {
    "branch": "RAS AL KHAIMAH",
    "client_type": "New Client",
    "product_type": "SME",
    "insured_type": "Private Firms",
    "tpa": "NEXT CARE MANAGEMENT LLC",
    "nature_of_group": "Others",  # Common business type
    "company_name": "API Test Company",
    "company_cr_number": "123456789",
    "email": "apicomp@gmail.com",
    "trade_license_number": "987654321",
}


class AlSagrQuotationCreator:
    """
    Creates a new quotation in Al Sagr portal for API extraction.
    
    This is a hybrid approach that uses Playwright to fill forms
    and then API extraction for benefit values.
    """
    
    def __init__(self, page, values: Dict[str, Any] = None):
        """
        Initialize quotation creator.
        
        Args:
            page: Playwright page object
            values: Optional dict of form values (uses defaults if not provided)
        """
        self.page = page
        self.values = values or {}
        self.quotation_id = None
        
    def _get_value(self, key: str, default: Any = None) -> Any:
        """Get value from provided values or use default."""
        if key in self.values:
            return self.values[key]
        return DEFAULT_QUOTATION_VALUES.get(key, default)
    
    async def navigate_to_quotation_form(self) -> bool:
        """
        Navigate to the New Quotation form.
        
        Steps:
        1. Click mobile menu button
        2. Click Medical Portal link
        3. Click SME/Group/EBP B2B link
        4. Click Quotation Information link
        5. Click Add New Quotation button
        
        Returns:
            bool: True if navigation successful
        """
        try:
            alsagr_logger.info("Navigating to quotation form...")
            print("\n📋 Navigating to quotation form...")
            
            # Wait for page to be ready
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # 1. Click mobile menu button
            print("   → Clicking menu button...")
            await self.page.locator("button.button-menu-mobile").click()
            await asyncio.sleep(MAX_SLEEP)
            
            # 2. Click Medical Portal link
            print("   → Opening Medical Portal...")
            await self.page.locator('a[href="#sys-295"]').click()
            await asyncio.sleep(MAX_SLEEP)
            
            # 3. Click SME/Group/EBP B2B link
            print("   → Opening SME/Group/EBP B2B...")
            await self.page.locator('a[href="#mod-318"]').click()
            await asyncio.sleep(MAX_SLEEP)
            
            # 4. Click Quotation Information
            print("   → Opening Quotation Information...")
            await self.page.locator('(//a[text()="Quotation Information"])[1]').click()
            await asyncio.sleep(MAX_SLEEP)
            await self.page.wait_for_load_state('networkidle')
            
            # 5. Click Add New Quotation button
            print("   → Clicking Add New Quotation...")
            await self.page.locator('button[title="Add New Quotation"]').click()
            await asyncio.sleep(MAX_SLEEP)
            await self.page.wait_for_load_state('networkidle')
            
            alsagr_logger.info("Navigation to quotation form successful")
            print("   ✓ Reached quotation form")
            return True
            
        except Exception as e:
            alsagr_logger.error(f"Navigation failed: {e}")
            print(f"   ❌ Navigation failed: {e}")
            return False
    
    async def fill_basic_info(self) -> bool:
        """
        Fill basic quotation information (Branch, Client Type, Product Type).
        
        Returns:
            bool: True if successful
        """
        try:
            print("\n📝 Filling basic quotation info...")
            
            # Branch
            branch = self._get_value("branch")
            print(f"   → Branch: {branch}")
            await self.page.locator("#CollapseQuoteInformation #branch").select_option(branch)
            await asyncio.sleep(MED_SLEEP)
            await self.page.wait_for_load_state('networkidle')
            
            # Client Type
            client_type = self._get_value("client_type")
            print(f"   → Client Type: {client_type}")
            await self.page.locator("#client").select_option(client_type)
            await asyncio.sleep(MED_SLEEP)
            
            # Product Type
            product_type = self._get_value("product_type")
            print(f"   → Product Type: {product_type}")
            await self.page.locator("#CollapseQuoteInformation #productType").select_option(product_type)
            await asyncio.sleep(MED_SLEEP)
            
            # Click Add Prospect Button
            print("   → Clicking Add Prospect...")
            await self.page.get_by_role("button", name="Add Prospect").click()
            
            # Wait for spinner/loading to complete
            await asyncio.sleep(MAX_SLEEP)
            try:
                await self.page.wait_for_load_state('networkidle', timeout=15000)
            except Exception:
                alsagr_logger.debug("Network idle timeout after Add Prospect - continuing")
            await asyncio.sleep(MAX_SLEEP)  # Extra wait for form to fully load
            
            print("   ✓ Basic info filled")
            
            return True
            
        except Exception as e:
            alsagr_logger.error(f"Failed to fill basic info: {e}")
            print(f"   ❌ Failed: {e}")
            return False
    
    async def fill_insured_info(self) -> bool:
        """
        Fill insured/company information.
        
        Returns:
            bool: True if successful
        """
        try:
            print("\n📝 Filling insured information...")
            await asyncio.sleep(MAX_SLEEP)
            
            # Insured Type
            insured_type = self._get_value("insured_type")
            print(f"   → Insured Type: {insured_type}")
            await self.page.locator("#insuredType").select_option(insured_type)
            await asyncio.sleep(MED_SLEEP)
            await self.page.wait_for_load_state('networkidle')
            
            # Company CR Number
            cr_number = str(self._get_value("company_cr_number"))
            print(f"   → CR Number: {cr_number}")
            await self.page.locator("#companyCRNumber").fill(cr_number)
            await asyncio.sleep(MED_SLEEP)
            
            # Company Name
            company_name = self._get_value("company_name")
            print(f"   → Company Name: {company_name}")
            await self.page.locator("#fullName").fill(company_name)
            await asyncio.sleep(MED_SLEEP)
            
            # Email
            email = self._get_value("email")
            print(f"   → Email: {email}")
            await self.page.locator("#policyEmail").fill(email)
            await asyncio.sleep(MED_SLEEP)
            
            # Trade License Number
            trade_license = str(self._get_value("trade_license_number"))
            print(f"   → Trade License: {trade_license}")
            await self.page.locator("#tradeLicenseNo").fill(trade_license)
            await asyncio.sleep(MED_SLEEP)
            
            # Trade License Expiry Date (default: 1 year from now)
            expiry_date = self._get_value("trade_license_expiry_date")
            if not expiry_date:
                expiry_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            elif isinstance(expiry_date, str) and '/' in expiry_date:
                expiry_date = datetime.strptime(expiry_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            print(f"   → Trade License Expiry: {expiry_date}")
            await self.page.locator("#tradeLicenseExpiryDate").fill(expiry_date)
            await asyncio.sleep(MED_SLEEP)
            
            # Wait for any spinners after filling all fields
            print("   → Waiting for form to process...")
            await asyncio.sleep(MAX_SLEEP)
            try:
                await self.page.wait_for_load_state('networkidle', timeout=10000)
            except Exception:
                pass
            await asyncio.sleep(MAX_SLEEP)
            
            # Click Save Button
            await self.page.locator("//*[@id='CollapseCustomerInfo']/div[2]/button").click()
            print("   ✓ Insured info saved")
            
            # Wait for spinner/loading to complete
            await asyncio.sleep(MAX_SLEEP)
            try:
                await self.page.wait_for_load_state('networkidle', timeout=15000)
            except Exception:
                alsagr_logger.debug("Network idle timeout after insured info save - continuing")
            await asyncio.sleep(MAX_SLEEP)  # Extra wait for form update
            
            # Click Pop-up Window Ok Button
            try:
                await self.page.get_by_role("button", name="Ok S").click()
                await asyncio.sleep(MED_SLEEP)
            except Exception:
                pass  # OK button might not appear
            
            return True
            
        except Exception as e:
            alsagr_logger.error(f"Failed to fill insured info: {e}")
            print(f"   ❌ Failed: {e}")
            return False
    
    async def fill_quotation_details(self) -> bool:
        """
        Fill quotation details (TPA, Nature of Group, Dates).
        
        Returns:
            bool: True if successful
        """
        try:
            print("\n📝 Filling quotation details...")
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(MED_SLEEP)
            
            # TPA
            tpa = self._get_value("tpa")
            print(f"   → TPA: {tpa}")
            await self.page.locator("#CollapseQuoteInformation #tpa").select_option(tpa)
            await asyncio.sleep(MED_SLEEP)
            await self.page.wait_for_load_state('networkidle')
            
            # Nature of Group
            nature_of_group = self._get_value("nature_of_group")
            print(f"   → Nature of Group: {nature_of_group}")
            await self.page.locator("#natureOfGroup").select_option(nature_of_group)
            await asyncio.sleep(MED_SLEEP)
            await self.page.wait_for_load_state('networkidle')
            
            # Effective Date (default: tomorrow)
            effective_date = self._get_value("effective_date")
            if not effective_date:
                effective_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            elif isinstance(effective_date, str) and '/' in effective_date:
                effective_date = datetime.strptime(effective_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            print(f"   → Effective Date: {effective_date}")
            await self.page.locator("#effectiveDate").fill(effective_date)
            await asyncio.sleep(MED_SLEEP)
            
            # Agree to terms
            await self.page.locator("#agreeTerms").click()
            print("   ✓ Agreed to terms")
            await asyncio.sleep(MED_SLEEP)
            
            # Click Yes Button
            try:
                await self.page.get_by_role("button", name="Yes S").click()
                await asyncio.sleep(MED_SLEEP)
            except Exception:
                pass
            
            print("   ✓ Quotation details filled")
            return True
            
        except Exception as e:
            alsagr_logger.error(f"Failed to fill quotation details: {e}")
            print(f"   ❌ Failed: {e}")
            return False
    
    async def save_quotation(self) -> Optional[int]:
        """
        Save the quotation and extract quotation ID.
        
        Uses network interception to capture the quotationId from API response.
        The save action triggers API calls that return/contain the quotationId.
        
        Returns:
            int: Quotation ID if successful, None otherwise
        """
        try:
            print("\n💾 Saving quotation...")
            
            # Set up response listener to capture quotationId
            captured_quotation_id = None
            all_responses = []  # Log all API responses for debugging
            
            async def capture_response(response):
                nonlocal captured_quotation_id
                try:
                    url_lower = response.url.lower()
                    # Check for various API patterns that might contain/return quotationId
                    save_patterns = ['save', 'create', 'insert', 'quotation', 'quote']
                    if any(p in url_lower for p in save_patterns) and response.status in [200, 201]:
                        content_type = response.headers.get('content-type', '')
                        if 'json' in content_type:
                            try:
                                data = await response.json()
                                all_responses.append({'url': response.url, 'data': str(data)[:200]})
                                
                                def extract_id_from_dict(d, source=""):
                                    """Extract quotationId from dict, handling different key formats."""
                                    # Check various key formats (case-insensitive)
                                    for key in d.keys():
                                        key_lower = key.lower()
                                        if key_lower in ['quotationid', 'quotation_id', 'quotatioN_ID'.lower()]:
                                            val = d[key]
                                            if val and isinstance(val, int) and val > 0:
                                                alsagr_logger.info(f"Captured quotationId from {source}: {val}")
                                                return val
                                    return None
                                
                                # Handle different response formats
                                if isinstance(data, dict):
                                    # Direct quotationId in response
                                    new_id = extract_id_from_dict(data, response.url)
                                    if new_id:
                                        captured_quotation_id = new_id
                                    # Nested in result property
                                    elif 'result' in data and isinstance(data['result'], dict):
                                        new_id = extract_id_from_dict(data['result'], f"{response.url} result")
                                        if new_id:
                                            captured_quotation_id = new_id
                                    # Nested in data property
                                    elif 'data' in data and isinstance(data['data'], dict):
                                        new_id = extract_id_from_dict(data['data'], f"{response.url} data")
                                        if new_id:
                                            captured_quotation_id = new_id
                                # Response is just the numeric ID
                                elif isinstance(data, int) and data > 0:
                                    captured_quotation_id = data
                                    alsagr_logger.info(f"Captured quotationId (int response): {captured_quotation_id}")
                            except Exception as e:
                                alsagr_logger.debug(f"Could not parse response: {e}")
                except Exception:
                    pass
            
            # Subscribe to responses
            self.page.on('response', capture_response)
            
            # Click Save Button
            alsagr_logger.debug("Clicking Save button...")
            try:
                save_btn = self.page.locator('//button[@title="Save"]')
                await save_btn.wait_for(state='visible', timeout=10000)
                await save_btn.click()
                alsagr_logger.debug("Save button clicked successfully")
            except Exception as e:
                alsagr_logger.error(f"Failed to click Save button: {e}")
                # Try alternative selector
                try:
                    await self.page.locator('button:has-text("Save")').click()
                    alsagr_logger.debug("Clicked Save via text selector")
                except Exception as e2:
                    alsagr_logger.error(f"Alternative Save click also failed: {e2}")
            
            # Wait for loading spinner to appear and disappear
            alsagr_logger.debug("Waiting for save operation to complete...")
            await asyncio.sleep(2)  # Let spinner appear
            
            # Wait for page navigation (URL will change to include quoteId)
            try:
                # Wait for URL to change (indicates save completed and redirected)
                await self.page.wait_for_function(
                    "() => window.location.href.includes('quoteId=')",
                    timeout=60000  # 60 seconds for slow saves
                )
                alsagr_logger.debug(f"Page navigated after save: {self.page.url}")
            except Exception as e:
                alsagr_logger.warning(f"URL didn't change after save: {e}")
            
            # Wait for network to settle after navigation
            await asyncio.sleep(MAX_SLEEP)
            try:
                await self.page.wait_for_load_state('networkidle', timeout=30000)
            except Exception:
                alsagr_logger.debug("Network idle timeout - continuing anyway")
            
            # Extra wait for API responses to be captured
            await asyncio.sleep(5)
            
            # Unsubscribe from response listener
            self.page.remove_listener('response', capture_response)
            
            # Log captured responses for debugging
            if all_responses:
                alsagr_logger.debug(f"Captured {len(all_responses)} API responses during save")
                for r in all_responses:
                    alsagr_logger.debug(f"  - {r['url']}: {r['data']}")
            else:
                alsagr_logger.warning("No API responses captured during save! Check if save actually triggered.")
                alsagr_logger.debug(f"Current URL after save attempt: {self.page.url}")
            
            # Click Pop-up Window Ok Button - try multiple selectors
            # Wait for success popup to appear
            popup_clicked = False
            alsagr_logger.debug("Looking for success popup...")
            
            # Try to find popup with "Successfully Saved" message first
            try:
                # Wait for success message to appear
                success_msg = self.page.locator('text=/Successfully Saved/i')
                await success_msg.wait_for(state='visible', timeout=10000)
                alsagr_logger.debug("Success popup appeared")
                await asyncio.sleep(1)  # Let popup fully render
            except Exception:
                alsagr_logger.debug("No success message popup found")
            
            # Try different OK button selectors
            for popup_selector in [
                'button:has-text("Ok")',
                'button:has-text("OK")',  
                'button.swal2-confirm',
                '.swal2-confirm',
                'button[class*="ok" i]',
                'button[class*="confirm" i]'
            ]:
                try:
                    popup_btn = self.page.locator(popup_selector).first
                    if await popup_btn.is_visible(timeout=3000):
                        await popup_btn.click()
                        popup_clicked = True
                        alsagr_logger.debug(f"Clicked popup with selector: {popup_selector}")
                        await asyncio.sleep(MED_SLEEP)
                        break
                except Exception:
                    continue
            
            if not popup_clicked:
                alsagr_logger.debug("No popup found to click - may have auto-closed")
            
            # Wait for page to stabilize after popup
            await asyncio.sleep(MAX_SLEEP)
            
            # Check if we captured quotationId from network
            if captured_quotation_id:
                self.quotation_id = captured_quotation_id
                print(f"   ✓ Quotation saved! ID: {captured_quotation_id}")
                alsagr_logger.info(f"Quotation created with ID: {captured_quotation_id}")
                return captured_quotation_id
            
            # If not captured from network, try other methods
            quotation_id = await self._extract_quotation_id()
            
            if quotation_id:
                self.quotation_id = quotation_id
                print(f"   ✓ Quotation saved! ID: {quotation_id}")
                alsagr_logger.info(f"Quotation created with ID: {quotation_id}")
                return quotation_id
            
            # Last resort: Try to navigate to quotation and extract ID
            quotation_id = await self._navigate_and_extract_id()
            
            if quotation_id:
                self.quotation_id = quotation_id
                print(f"   ✓ Quotation saved! ID: {quotation_id}")
                alsagr_logger.info(f"Quotation created with ID: {quotation_id}")
                return quotation_id
            
            print("   ⚠️ Quotation saved but couldn't extract ID")
            alsagr_logger.warning("Quotation saved but couldn't extract ID")
            return None
                
        except Exception as e:
            alsagr_logger.error(f"Failed to save quotation: {e}")
            print(f"   ❌ Failed: {e}")
            return None
    
    async def _navigate_and_extract_id(self) -> Optional[int]:
        """
        Navigate to the quotation and extract ID by intercepting GetQuoteInformation API.
        
        After save, the URL shows quotation NUMBER (e.g., Q/592026/070553), not ID.
        When we click on the quotation, the page calls GetQuoteInformation API.
        We intercept that response to get the numeric quotationId.
        
        Returns:
            int: Quotation ID if found, None otherwise
        """
        try:
            print("   🔍 Navigating to quotation to extract ID...")
            await asyncio.sleep(2)
            
            current_url = self.page.url
            alsagr_logger.debug(f"Current URL: {current_url}")
            
            # Set up response listener to capture quotationId from GetQuoteInformation
            captured_quotation_id = None
            
            async def capture_quote_info(response):
                nonlocal captured_quotation_id
                try:
                    # Intercept GetQuoteInformation API response
                    if 'GetQuoteInformation' in response.url and response.status == 200:
                        data = await response.json()
                        if isinstance(data, dict) and 'quotationId' in data:
                            captured_quotation_id = data['quotationId']
                            alsagr_logger.info(f"Captured quotationId from GetQuoteInformation: {captured_quotation_id}")
                except Exception:
                    pass
            
            # Subscribe to responses
            self.page.on('response', capture_quote_info)
            
            # If we're on the search page with a quoteId, click first result
            if 'quotationsearch' in current_url.lower() or 'quoteId' in current_url:
                await self.page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                # Try to click on the first quotation row to trigger GetQuoteInformation API
                try:
                    first_row = self.page.locator("table tbody tr").first
                    if await first_row.count() > 0:
                        print("   → Clicking quotation row to load details...")
                        await first_row.click()
                        await asyncio.sleep(MAX_SLEEP)
                        await self.page.wait_for_load_state('networkidle')
                        await asyncio.sleep(2)  # Wait for API response
                        
                        # Check if we captured the ID
                        if captured_quotation_id:
                            self.page.remove_listener('response', capture_quote_info)
                            return captured_quotation_id
                        
                        # Try clicking Edit/View button which should call GetQuoteInformation
                        try:
                            edit_btn = self.page.locator("button[title*='Edit'], a[title*='Edit'], button[title*='View'], button:has-text('Edit')").first
                            if await edit_btn.is_visible():
                                print("   → Clicking Edit button...")
                                await edit_btn.click()
                                await asyncio.sleep(MAX_SLEEP)
                                await self.page.wait_for_load_state('networkidle')
                                await asyncio.sleep(2)
                                
                                if captured_quotation_id:
                                    self.page.remove_listener('response', capture_quote_info)
                                    return captured_quotation_id
                        except Exception:
                            pass
                except Exception as e:
                    alsagr_logger.debug(f"Could not click quotation row: {e}")
            
            # Unsubscribe
            self.page.remove_listener('response', capture_quote_info)
            
            # If still not found, check URL for quotationId pattern
            new_url = self.page.url
            match = re.search(r'quotationId[=:](\d+)', new_url, re.IGNORECASE)
            if match:
                return int(match.group(1))
            
            # Try localStorage/sessionStorage
            quotation_id = await self.page.evaluate("""
                () => {
                    const keys = ['quotationId', 'currentQuotationId', 'quotation_id', 'selectedQuotationId'];
                    for (const key of keys) {
                        let val = localStorage.getItem(key) || sessionStorage.getItem(key);
                        if (val && !isNaN(parseInt(val))) {
                            return parseInt(val);
                        }
                    }
                    return null;
                }
            """)
            
            if quotation_id:
                alsagr_logger.info(f"Found quotationId in storage: {quotation_id}")
                return quotation_id
            
            return None
            
        except Exception as e:
            alsagr_logger.debug(f"Could not navigate and extract ID: {e}")
            return None
    
    async def _extract_quotation_id(self) -> Optional[int]:
        """
        Extract quotation ID from various sources.
        
        Tries:
        1. URL parameters
        2. localStorage
        3. Page content/state
        4. API intercept
        
        Returns:
            int: Quotation ID if found, None otherwise
        """
        try:
            await asyncio.sleep(2)
            
            # Try URL
            current_url = self.page.url
            alsagr_logger.debug(f"Current URL: {current_url}")
            
            # Try various URL patterns
            patterns = [
                r'quotationId[=:](\d+)',
                r'quotation[=:](\d+)',
                r'/quotation/(\d+)',
                r'qid[=:](\d+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, current_url, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            
            # Try JavaScript evaluation
            quotation_id = await self.page.evaluate("""
                () => {
                    // Try localStorage
                    const keys = ['quotationId', 'currentQuotationId', 'quotation_id', 'qId'];
                    for (const key of keys) {
                        const val = localStorage.getItem(key);
                        if (val && !isNaN(parseInt(val))) {
                            return parseInt(val);
                        }
                    }
                    
                    // Try URL parameters
                    const urlParams = new URLSearchParams(window.location.search);
                    for (const key of keys) {
                        const val = urlParams.get(key);
                        if (val && !isNaN(parseInt(val))) {
                            return parseInt(val);
                        }
                    }
                    
                    // Try Angular state
                    if (window.__QUOTATION_ID__) return window.__QUOTATION_ID__;
                    
                    // Try finding in page content
                    const pageText = document.body.innerText;
                    const qMatch = pageText.match(/Q\\/\\d{6}\\/(\\d+)/);
                    if (qMatch) {
                        // This is quotation number, not ID - need different approach
                    }
                    
                    return null;
                }
            """)
            
            if quotation_id:
                return int(quotation_id)
            
            return None
            
        except Exception as e:
            alsagr_logger.debug(f"Could not extract quotation ID: {e}")
            return None
    
    async def upload_census_data(self) -> bool:
        """
        Upload census data to the quotation.
        
        This is REQUIRED for benefit structure to have data.
        Without census, the API returns empty benefit structure.
        
        Returns:
            bool: True if successful
        """
        try:
            print("\n📋 Uploading census data...")
            
            # Click Next Button to go to Census Data page
            await self.page.get_by_role("button", name="Next m").click()
            await asyncio.sleep(MAX_SLEEP)
            await self.page.wait_for_load_state('networkidle')
            print("   → Reached Census Data page")
            
            # Click Upload Button (button with icon "2")
            try:
                upload_btn = self.page.get_by_role("button", name="2")
                await upload_btn.wait_for(state='visible', timeout=10000)
                await upload_btn.click()
                alsagr_logger.debug("Clicked Upload Button")
                await asyncio.sleep(MED_SLEEP)
            except Exception:
                # Try alternative selector
                await self.page.locator('button.btn-warning').first.click()
                await asyncio.sleep(MED_SLEEP)
            
            # Set file to upload
            file_path = os.path.join(ALSAGR_TEMPLATES_DIR, "MemberUpload.xlsx")
            print(f"   → Uploading: {file_path}")
            
            if not os.path.exists(file_path):
                alsagr_logger.error(f"Census file not found: {file_path}")
                print(f"   ❌ File not found: {file_path}")
                return False
            
            await self.page.get_by_label("Select Excel File:").set_input_files(file_path)
            alsagr_logger.debug("File selected")
            await asyncio.sleep(MED_SLEEP)
            
            # Click Upload Button
            await self.page.get_by_role("button", name="Upload").click()
            alsagr_logger.debug("Clicked Upload button")
            await asyncio.sleep(MAX_SLEEP)
            
            # Wait for upload to complete
            try:
                await self.page.wait_for_load_state('networkidle', timeout=30000)
            except Exception:
                pass
            await asyncio.sleep(MAX_SLEEP)
            
            # Click Proceed button
            try:
                proceed_btn = self.page.get_by_text("Proceed")
                if await proceed_btn.is_visible(timeout=10000):
                    await proceed_btn.click()
                    alsagr_logger.debug("Clicked Proceed button")
                    await asyncio.sleep(MAX_SLEEP)
            except Exception as e:
                alsagr_logger.debug(f"No Proceed button found: {e}")
            
            print("   ✓ Census data uploaded")
            return True
            
        except Exception as e:
            alsagr_logger.error(f"Failed to upload census data: {e}")
            print(f"   ❌ Failed: {e}")
            return False
    
    async def navigate_to_benefit_structure(self) -> bool:
        """
        Navigate to the Benefit Structure page after uploading census.
        
        Returns:
            bool: True if successful
        """
        try:
            print("\n📋 Navigating to Benefit Structure...")
            
            # Click Next Button to go to Benefit Structure
            await self.page.get_by_role("button", name="Next m").click()
            await asyncio.sleep(MAX_SLEEP)
            
            # Wait for page to load
            try:
                await self.page.wait_for_load_state('networkidle', timeout=30000)
            except Exception:
                pass
            await asyncio.sleep(MAX_SLEEP)
            
            # Verify we're on the benefit structure page
            current_url = self.page.url
            if 'benefitstructure' in current_url.lower():
                print("   ✓ Reached Benefit Structure page")
                return True
            
            # If not on benefit page, try direct navigation
            if self.quotation_id:
                benefit_url = f"https://miportal.alsagrins.ae/#/groupquotationbenefitstructure?quotationId={self.quotation_id}"
                await self.page.goto(benefit_url)
                await self.page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                print("   ✓ Navigated to Benefit Structure page")
                return True
            
            print("   ✓ Reached Benefit Structure page")
            return True
            
        except Exception as e:
            alsagr_logger.error(f"Failed to navigate to benefit structure: {e}")
            print(f"   ❌ Failed: {e}")
            return False
    
    async def create_quotation(self) -> Optional[int]:
        """
        Full quotation creation flow.
        
        Returns:
            int: Quotation ID if successful, None otherwise
        """
        print("\n" + "=" * 60)
        print("📋 CREATING NEW QUOTATION")
        print("=" * 60)
        
        # Step 1: Navigate to form
        if not await self.navigate_to_quotation_form():
            return None
        
        # Step 2: Fill basic info
        if not await self.fill_basic_info():
            return None
        
        # Step 3: Fill insured info
        if not await self.fill_insured_info():
            return None
        
        # Step 4: Fill quotation details
        if not await self.fill_quotation_details():
            return None
        
        # Step 5: Save quotation
        quotation_id = await self.save_quotation()
        
        return quotation_id


async def create_quotation_with_excel(page, df1, cat1) -> Optional[int]:
    """
    Create quotation using Excel data (like old code flow).
    
    This bridges the old Excel-based flow with the new API extraction.
    
    Args:
        page: Playwright page object
        df1: DataFrame with KEY/VALUE pairs
        cat1: DataFrame with category 1 data
        
    Returns:
        int: Quotation ID if successful, None otherwise
    """
    print("\n" + "=" * 60)
    print("📋 CREATING QUOTATION FROM EXCEL DATA")
    print("=" * 60)
    
    def get_value(key: str, default: str = "") -> str:
        """Get value from df1."""
        try:
            return df1[df1['KEY'] == key]['VALUE'].values[0]
        except (IndexError, KeyError):
            return default
    
    def get_cat_value(key: str, default: str = "") -> str:
        """Get value from cat1 DataFrame."""
        try:
            return str(cat1[key].iloc[0])
        except (IndexError, KeyError):
            return default
    
    # Build values dict from Excel data
    values = {
        "branch": "SHEIKH ZAYED",  # Fixed for Al Sagr
        "client_type": "New Client" if get_value("New-Renew") == "New" else "Existing Client",
        "product_type": "SME",  # Fixed for API extraction
        "insured_type": "Government",  # Default
        "company_cr_number": get_value("Company CR Number"),
        "company_name": get_value("Company Name"),
        "email": get_value("Email"),
        "trade_license_number": get_value("Trade License Number"),
        "trade_license_expiry_date": get_value("Trade License Expiry Date"),
        "effective_date": get_value("Effective from"),
        "tpa": get_cat_value("TPA", "NEXT CARE MANAGEMENT LLC"),
        "nature_of_group": get_cat_value("Business Nature", "Manpower Supply"),
    }
    
    # Create quotation
    creator = AlSagrQuotationCreator(page, values)
    return await creator.create_quotation()
