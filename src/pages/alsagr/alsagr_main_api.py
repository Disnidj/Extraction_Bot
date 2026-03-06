"""
Al Sagr API-Based Extraction Entry Point

This module provides the main entry point for Al Sagr API extraction.
Follows the same pattern as other API extraction portals (Orient Aura, ADNIC, Sukoon, etc.)

HYBRID FLOW (Default):
1. Login via Playwright
2. Create quotation by filling form (like old standard extraction)
3. Get quotationId from created quotation OR intercept from API
4. Use API extraction for benefit values

DIRECT API MODE (if default_quotation_id is set):
1. Login via Playwright
2. Use configured quotation_id
3. Use API extraction for benefit values

Key Difference from Standard Extraction:
- Standard: Fill form → Fill categories → Download quotation
- API Hybrid: Fill form → Get quotationId → API extraction (faster, more reliable)

Usage:
    Can be called from main.py or run directly:
    python -m src.pages.alsagr.alsagr_main_api
"""

import asyncio
import time
import re
from patchright.async_api import Playwright, async_playwright
from src.pages.alsagr.login_page import LoginPage
from src.pages.alsagr.api import (
    AlSagrAuthToken, 
    AlSagrAPIExtractor, 
    AlSagrFormatter, 
    AlSagrQuotationCreator,
)
from src.utils.logger import alsagr_logger
from src.utils.load_yaml import IS_HEADLESS, ALSAGR_DEFAULT_QUOTATION_ID, MAX_SLEEP, MED_SLEEP


async def intercept_quotation_id(page) -> int:
    """
    Set up network interception to capture quotationId from API responses.
    
    This intercepts the API response when quotation is saved to extract the ID.
    
    Args:
        page: Playwright page object
        
    Returns:
        int: Quotation ID if found, None otherwise
    """
    quotation_id = None
    
    # Try to extract from existing page state first
    try:
        # Check localStorage
        local_data = await page.evaluate("""
            () => {
                // Check various localStorage keys
                const keys = ['quotationId', 'currentQuotationId', 'quotation_id'];
                for (const key of keys) {
                    const val = localStorage.getItem(key);
                    if (val && !isNaN(parseInt(val))) {
                        return parseInt(val);
                    }
                }
                return null;
            }
        """)
        
        if local_data:
            return local_data
            
        # Try to find in URL
        current_url = page.url
        match = re.search(r'quotationId[=:]\s*(\d+)', current_url, re.IGNORECASE)
        if match:
            return int(match.group(1))
            
        # Try to find quotation number in page and look up ID
        quotation_no = await page.evaluate("""
            () => {
                // Look for quotation number pattern in page
                const text = document.body.innerText;
                const match = text.match(/Q\\/\\d{6}\\/(\\d+)/);
                if (match) return match[0];
                
                // Try specific element
                const qNoEl = document.querySelector('#quotationNo, [name="quotationNo"]');
                if (qNoEl && qNoEl.value) return qNoEl.value;
                
                return null;
            }
        """)
        
        alsagr_logger.debug(f"Found quotation number: {quotation_no}")
        
    except Exception as e:
        alsagr_logger.debug(f"Could not intercept quotation ID: {e}")
    
    return quotation_id


async def upload_census_and_navigate(page, quotation_id: int):
    """
    Upload census data and navigate to benefit structure page.
    
    This is REQUIRED for benefit structure to have data.
    Without census, the API returns empty benefit structure.
    
    Flow (from old process_page.py):
    1. Click Next → Census Data page
    2. Click button "2" (opens file dialog)
    3. Set file via "Select Excel File:" label
    4. Click "Upload" button
    5. Click "Proceed" button
    6. Click Next → Benefit Structure page
    
    Args:
        page: Playwright page object
        quotation_id: Quotation ID
        
    Returns:
        bool: True if successful
    """
    from src.utils.load_yaml import ALSAGR_TEMPLATES_DIR
    import os
    import time
    
    try:
        print("\n📋 Uploading census data...")
        
        # Step 1: Click Next to go to Census Data page
        await page.get_by_role("button", name="Next m").click()
        alsagr_logger.debug("Clicked Next Button → Census Data page")
        time.sleep(MED_SLEEP)
        
        # Step 2: Click Upload Button (name="2" opens the file dialog area)
        await page.get_by_role("button", name="2").click()
        alsagr_logger.debug("Clicked Upload Button (2)")
        time.sleep(MED_SLEEP)
        print("   → Opened file upload dialog")
        
        # Step 3: Set file to upload
        file_path = os.path.join(ALSAGR_TEMPLATES_DIR, "MemberUpload.xlsx")
        print(f"   → Uploading: {file_path}")
        
        if not os.path.exists(file_path):
            alsagr_logger.error(f"Census file not found: {file_path}")
            print(f"   ❌ File not found: {file_path}")
            return False
        
        await page.get_by_label("Select Excel File:").set_input_files(file_path)
        alsagr_logger.debug("File selected")
        time.sleep(MED_SLEEP)
        
        # Step 4: Click Upload Button (this uploads the file)
        await page.get_by_role("button", name="Upload").click()
        alsagr_logger.debug("Clicked Upload button")
        time.sleep(MAX_SLEEP)  # Wait longer for file processing
        print("   ✓ File uploaded")
        
        # Handle duplicate rows popup BEFORE Proceed (e.g., "Row X and Row Y are duplicated")
        # This popup appears after upload and blocks the Proceed button
        try:
            popup_ok = page.locator('button:has-text("Ok")')
            if await popup_ok.is_visible(timeout=5000):
                await popup_ok.click()
                alsagr_logger.debug("Clicked Ok on duplicate rows popup")
                print("   → Dismissed duplicate rows warning")
                time.sleep(MED_SLEEP)
        except Exception:
            pass  # No popup, continue
        
        # Step 5: Click Proceed button
        await page.get_by_text("Proceed").click()
        alsagr_logger.debug("Clicked Proceed button")
        time.sleep(MED_SLEEP)
        
        print("   ✓ Census data processed")
        
        # Step 6: Click Next to go to Benefit Structure
        await page.get_by_role("button", name="Next m").click()
        alsagr_logger.debug("Clicked Next Button → Benefit Structure page")
        time.sleep(MAX_SLEEP)
        
        print("   ✓ Navigated to Benefit Structure page")
        return True
        
    except Exception as e:
        alsagr_logger.error(f"Failed to upload census and navigate: {e}")
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def navigate_to_benefit_structure(page, quotation_id: int):
    """
    Navigate to the benefit structure page for a specific quotation.
    
    This function now calls upload_census_and_navigate() to ensure
    census data is uploaded before navigating to benefit structure.
    
    Args:
        page: Playwright page object
        quotation_id: Quotation ID to navigate to
        
    Returns:
        bool: True if navigation successful
    """
    # Use the full flow that uploads census data
    return await upload_census_and_navigate(page, quotation_id)


async def run_alsagr_api_extraction_hybrid(
    playwright: Playwright, 
    quotation_values: dict = None,
    output_dir: str = "extracted_data"
):
    """
    HYBRID MODE: Create quotation + API extraction.
    
    This is the main extraction flow that:
    1. Logs in to Al Sagr portal
    2. Creates a new quotation by filling form
    3. Extracts quotation ID 
    4. Uses API extraction for benefits
    
    Args:
        playwright: Playwright instance
        quotation_values: Optional dict of form values for quotation creation
        output_dir: Base output directory for extracted files
        
    Returns:
        dict: Extraction results with success status
    """
    print("\n" + "=" * 60)
    print("🔌 AL SAGR API EXTRACTION - HYBRID MODE")
    print("=" * 60)
    print("📌 Step 1: Login to portal")
    print("📌 Step 2: Create quotation (fill form)")
    print("📌 Step 3: Extract quotation ID")
    print("📌 Step 4: API extraction for benefits")
    print("📌 Filters: TPA = NEXT CARE MANAGEMENT LLC, Visa Region = Dubai")
    print("=" * 60)
    
    browser = None
    
    
    browser = None
    
    try:
        # Step 1: Launch browser and login
        args = ["--disable-blink-features=AutomationControlled"]
        browser = await playwright.chromium.launch(headless=IS_HEADLESS, args=args)
        context = await browser.new_context()
        context.set_default_timeout(60000)
        page = await context.new_page()
        
        # Login
        print("\n🔐 Logging in to Al Sagr portal...")
        login_page = LoginPage(page)
        await login_page.login()
        alsagr_logger.info("Login completed")
        print("   ✓ Login successful")
        
        # Wait for page to stabilize
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        # Step 2: Extract auth token (needed for API calls later)
        print("\n🔑 Extracting auth token...")
        auth = AlSagrAuthToken()
        token = await auth.extract_token_from_browser(page)
        
        if not token:
            alsagr_logger.error("Failed to extract token")
            print("   ❌ Failed to extract auth token")
            return {
                "success": False, 
                "results": None, 
                "errors": ["Failed to extract auth token"]
            }
        
        print(f"   ✓ Token extracted (length: {len(token)})")
        
        # Step 3: Create quotation
        creator = AlSagrQuotationCreator(page, quotation_values)
        quotation_id = await creator.create_quotation()
        
        # If quotation_id not found from creator, try intercept
        if not quotation_id:
            print("\n🔍 Trying to extract quotation ID from page...")
            quotation_id = await intercept_quotation_id(page)
        
        # Step 4: If still no quotation_id, show error
        if not quotation_id:
            print("\n" + "=" * 60)
            print("⚠️ QUOTATION ID NOT FOUND")
            print("=" * 60)
            print("\nThe quotation was created but we couldn't extract the ID.")
            print("Please check the browser and provide the quotation ID manually.")
            print("\nOR set 'default_quotation_id' in config.yaml:")
            print("   alsagr:")
            print("     default_quotation_id: 530746  # Your quotation ID")
            print("=" * 60)
            return {
                "success": False,
                "results": None,
                "errors": ["Could not extract quotation ID from created quotation"]
            }
        
        print(f"\n✅ Quotation ready for extraction")
        print(f"   Token: {len(auth.token)} characters")
        print(f"   Quotation ID: {quotation_id}")
        
        # Step 5: Navigate to benefit structure page
        await navigate_to_benefit_structure(page, quotation_id)
        
        # Refresh token in case it changed
        token = await auth.extract_token_from_browser(page)
        
        # Step 6: Extract all benefits via API
        print("\n" + "=" * 60)
        print("🔄 EXTRACTING BENEFIT DATA VIA API")
        print("=" * 60)
        
        extractor = AlSagrAPIExtractor(auth, quotation_id=quotation_id)
        results = await extractor.extract_all_benefits()
        
        # Step 7: Save JSON results
        json_file = extractor.save_results(output_dir=output_dir)
        
        # Step 8: Validate extraction
        is_valid, validation_errors = extractor.validate_extraction()
        
        if not is_valid:
            alsagr_logger.warning(f"Extraction validation warnings: {validation_errors}")
            print("\n⚠️ Extraction validation warnings:")
            for error in validation_errors:
                print(f"   - {error}")
        
        # Step 9: Format and save to text file
        print("\n" + "=" * 60)
        print("📝 FORMATTING OUTPUT")
        print("=" * 60)
        
        formatter = AlSagrFormatter(output_dir=output_dir)
        text_file = formatter.write_records(results.get("records", []))
        formatter.print_summary()
        
        # Summary
        print("\n" + "=" * 60)
        print("📁 OUTPUT FILES")
        print("=" * 60)
        print(f"   JSON: {json_file}")
        print(f"   TEXT: {text_file}")
        
        # Check for errors
        errors = results.get("errors", [])
        if errors:
            print("\n" + "=" * 60)
            print("⚠️ EXTRACTION ERRORS")
            print("=" * 60)
            for error in errors:
                print(f"   ❌ {error}")
        
        print("\n✅ Al Sagr API extraction completed!")
        
        return {
            "success": True,
            "results": results,
            "quotation_id": quotation_id,
            "errors": errors
        }
        
    except Exception as e:
        alsagr_logger.error(f"Extraction failed: {e}")
        print(f"\n❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "results": None,
            "errors": [f"Extraction failed: {str(e)}"]
        }
        
    finally:
        # Cleanup - handle case where browser might already be closed
        if browser:
            try:
                await browser.close()
            except Exception as e:
                alsagr_logger.debug(f"Browser cleanup: {e}")


async def run_alsagr_api_extraction_direct(
    playwright: Playwright, 
    quotation_id: int,
    output_dir: str = "extracted_data"
):
    """
    DIRECT API MODE: Use existing quotation ID for extraction.
    
    This mode skips quotation creation and directly extracts benefits
    from an existing quotation ID.
    
    Args:
        playwright: Playwright instance
        quotation_id: Existing quotation ID to extract from
        output_dir: Base output directory for extracted files
        
    Returns:
        dict: Extraction results with success status
    """
    print("\n" + "=" * 60)
    print("🔌 AL SAGR API EXTRACTION - DIRECT MODE")
    print("=" * 60)
    print(f"📌 Using existing quotation ID: {quotation_id}")
    print("📌 Step 1: Login to portal")
    print("📌 Step 2: Navigate to quotation")
    print("📌 Step 3: API extraction for benefits")
    print("📌 Filters: TPA = NEXT CARE MANAGEMENT LLC, Visa Region = Dubai")
    print("=" * 60)
    
    browser = None
    
    try:
        # Step 1: Launch browser and login
        args = ["--disable-blink-features=AutomationControlled"]
        browser = await playwright.chromium.launch(headless=IS_HEADLESS, args=args)
        context = await browser.new_context()
        context.set_default_timeout(60000)
        page = await context.new_page()
        
        # Login
        print("\n🔐 Logging in to Al Sagr portal...")
        login_page = LoginPage(page)
        await login_page.login()
        alsagr_logger.info("Login completed")
        print("   ✓ Login successful")
        
        # Wait for page to stabilize
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        # Step 2: Extract auth token
        print("\n🔑 Extracting auth token...")
        auth = AlSagrAuthToken()
        token = await auth.extract_token_from_browser(page)
        
        if not token:
            alsagr_logger.error("Failed to extract token")
            print("   ❌ Failed to extract auth token")
            return {
                "success": False, 
                "results": None, 
                "errors": ["Failed to extract auth token"]
            }
        
        print(f"   ✓ Token extracted (length: {len(token)})")
        
        print(f"\n✅ Ready for extraction")
        print(f"   Token: {len(auth.token)} characters")
        print(f"   Quotation ID: {quotation_id}")
        
        # Step 3: Navigate to benefit structure page
        await navigate_to_benefit_structure(page, quotation_id)
        
        # Step 4: Extract all benefits via API
        print("\n" + "=" * 60)
        print("🔄 EXTRACTING BENEFIT DATA VIA API")
        print("=" * 60)
        
        extractor = AlSagrAPIExtractor(auth, quotation_id=quotation_id)
        results = await extractor.extract_all_benefits()
        
        # Step 5: Save JSON results
        json_file = extractor.save_results(output_dir=output_dir)
        
        # Step 6: Validate extraction
        is_valid, validation_errors = extractor.validate_extraction()
        
        if not is_valid:
            alsagr_logger.warning(f"Extraction validation warnings: {validation_errors}")
            print("\n⚠️ Extraction validation warnings:")
            for error in validation_errors:
                print(f"   - {error}")
        
        # Step 7: Format and save to text file
        print("\n" + "=" * 60)
        print("📝 FORMATTING OUTPUT")
        print("=" * 60)
        
        formatter = AlSagrFormatter(output_dir=output_dir)
        text_file = formatter.write_records(results.get("records", []))
        formatter.print_summary()
        
        # Summary
        print("\n" + "=" * 60)
        print("📁 OUTPUT FILES")
        print("=" * 60)
        print(f"   JSON: {json_file}")
        print(f"   TEXT: {text_file}")
        
        # Check for errors
        errors = results.get("errors", [])
        if errors:
            print("\n" + "=" * 60)
            print("⚠️ EXTRACTION ERRORS")
            print("=" * 60)
            for error in errors:
                print(f"   ❌ {error}")
        
        print("\n✅ Al Sagr API extraction completed!")
        
        return {
            "success": True,
            "results": results,
            "quotation_id": quotation_id,
            "errors": errors
        }
        
    except Exception as e:
        alsagr_logger.error(f"Extraction failed: {e}")
        print(f"\n❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "results": None,
            "errors": [f"Extraction failed: {str(e)}"]
        }
        
    finally:
        # Cleanup - handle case where browser might already be closed
        if browser:
            try:
                await browser.close()
            except Exception as e:
                alsagr_logger.debug(f"Browser cleanup: {e}")


async def login_alsagr_api(playwright: Playwright, referral_id=None, output_dir: str = "extracted_data"):
    """
    Entry point for main.py integration.
    
    This is the function called by main.py when running API extraction mode.
    
    Logic:
    - If default_quotation_id is configured: Use DIRECT mode
    - Otherwise: Use HYBRID mode (create quotation + API extraction)
    
    Args:
        playwright: Playwright instance
        referral_id: Optional referral ID (not used in API extraction)
        output_dir: Base output directory for extracted files
        
    Returns:
        dict: Extraction results with success status
    """
    # Check if default quotation ID is configured
    if ALSAGR_DEFAULT_QUOTATION_ID:
        alsagr_logger.info(f"Using configured quotation ID: {ALSAGR_DEFAULT_QUOTATION_ID}")
        return await run_alsagr_api_extraction_direct(
            playwright, 
            quotation_id=ALSAGR_DEFAULT_QUOTATION_ID,
            output_dir=output_dir
        )
    else:
        # Use hybrid mode: create quotation + API extraction
        alsagr_logger.info("No default quotation ID configured - using HYBRID mode")
        return await run_alsagr_api_extraction_hybrid(
            playwright,
            output_dir=output_dir
        )


async def main():
    """Main entry point for direct execution."""
    print("\n" + "=" * 60)
    print("🏢 AL SAGR - API EXTRACTION")
    print("=" * 60)
    print("📍 Extracting benefit values using API calls")
    print("=" * 60)
    
    async with async_playwright() as playwright:
        result = await login_alsagr_api(playwright)
        
        if result.get("success"):
            print("\n✅ Al Sagr API extraction completed successfully!")
        else:
            print("\n❌ Al Sagr API extraction failed")
            for error in result.get("errors", []):
                print(f"   - {error}")


# Allow running this file directly
if __name__ == "__main__":
    asyncio.run(main())
