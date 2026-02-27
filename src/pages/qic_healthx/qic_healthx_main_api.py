"""
QIC HealthX Exclusive API-based Dropdown Extractor
Main entry point for extracting all dropdown values using API calls.

Portal: QIC HealthX Exclusive (wellx.ai)
Filter: Dubai only
TPA: NAS
"""

import asyncio
from playwright.async_api import Playwright, async_playwright
from src.utils.load_yaml import IS_HEADLESS
from src.pages.qic_healthx.login_page import LoginPage
from src.pages.qic_healthx.api import (
    QICHealthXAuthToken, 
    QICHealthXExtractor, 
    QICHealthXFormatter
)
from src.utils.logger import qic_healthx_logger


async def login_and_get_token(playwright: Playwright):
    """
    Login to QIC HealthX portal and extract auth token.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        QICHealthXAuthToken: Auth object with token set, or None on failure
    """
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=IS_HEADLESS, args=args)
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        # Perform login with retries
        login_page = LoginPage(page)
        login_success = await login_page.login()
        
        if not login_success:
            qic_healthx_logger.error("Login failed after retries")
            await browser.close()
            return None
        
        qic_healthx_logger.info("Login completed")
        
        # Extract token using auth handler
        auth = QICHealthXAuthToken()
        token = await auth.extract_token_from_browser(page)
        
        if not token:
            qic_healthx_logger.error("Failed to extract auth token")
            await browser.close()
            return None
        
        qic_healthx_logger.debug(f"Token extracted successfully (length: {len(token)})")
        
        # Close browser
        await browser.close()
        
        return auth
        
    except Exception as e:
        qic_healthx_logger.error(f"Login error: {str(e)}", exc_info=True)
        await browser.close()
        return None


async def run_qic_healthx_api_extraction(playwright: Playwright, output_dir: str = "extracted_data"):
    """
    Main function to run QIC HealthX API-based extraction.
    
    Args:
        playwright: Playwright instance
        output_dir: Base output directory for extracted files
        
    Returns:
        dict: Extraction results or None on failure
    """
    # Step 1: Login and get token
    print("\n" + "=" * 60)
    print("🔐 STEP 1: LOGIN & TOKEN EXTRACTION")
    print("=" * 60)
    print("   Logging in to QIC HealthX portal...")
    
    auth = await login_and_get_token(playwright)
    
    if not auth:
        qic_healthx_logger.error("Cannot proceed without auth token")
        print("   ❌ Login failed - cannot proceed")
        return {"success": False, "results": None, "errors": ["Login failed - could not authenticate or extract token"]}
    
    print("   ✓ Login successful")
    print(f"   ✓ Token extracted ({len(auth.token)} characters)")
    print(f"   ✓ Region filter: Dubai only")
    print(f"   ✓ TPA: NAS")
    
    # Step 2: Extract all benefits
    print("\n" + "=" * 60)
    print("🔄 STEP 2: EXTRACTING BENEFIT DROPDOWNS")
    print("=" * 60)
    
    extractor = QICHealthXExtractor(auth)
    results = await extractor.extract_all_benefits()
    
    # Step 3: Save JSON results
    json_file = extractor.save_results(output_dir=output_dir)
    
    # Step 4: Print extraction summary
    extractor.print_summary()
    
    # Step 5: Format to output files
    print("\n" + "=" * 60)
    print("📝 STEP 3: FORMATTING OUTPUT FILES")
    print("=" * 60)
    
    formatter = QICHealthXFormatter(results)
    formatted_records = formatter.format_to_text()
    
    # Save formatted TXT (JSON lines format, matches other portals)
    txt_formatted = formatter.save_to_txt(output_dir)
    
    # Print formatting summary
    formatter.print_summary()
    
    print("\n" + "=" * 60)
    print("📁 OUTPUT FILES")
    print("=" * 60)
    print(f"   JSON: {json_file}")
    print(f"   TXT:  {txt_formatted}")
    
    # Check for errors during extraction
    errors = results.get("errors", [])
    if errors:
        print("\n" + "=" * 60)
        print("⚠️ EXTRACTION ERRORS")
        print("=" * 60)
        for error in errors:
            print(f"   ❌ {error}")
        qic_healthx_logger.error(f"Extraction completed with {len(errors)} error(s): {errors}")
        print("\n❌ QIC HealthX extraction completed with errors!")
        return {"success": False, "results": results, "errors": errors}
    
    print("\n✅ QIC HealthX extraction completed!")
    return {"success": True, "results": results, "errors": []}


async def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("🏢 QIC HEALTHX EXCLUSIVE - API EXTRACTION")
    print("=" * 60)
    print("📍 Extracting all Dubai plans and benefits")
    print("   TPA: NAS")
    print("   Region: Dubai")
    print("   Required Fields: 23 benefit dropdowns")
    print("=" * 60)
    
    async with async_playwright() as playwright:
        result = await run_qic_healthx_api_extraction(playwright)
        
        if result and result.get("success"):
            print("\n" + "=" * 60)
            print("✅ QIC HEALTHX EXTRACTION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ QIC HEALTHX EXTRACTION FAILED")
            print("=" * 60)


# Allow running this file directly
if __name__ == "__main__":
    asyncio.run(main())
