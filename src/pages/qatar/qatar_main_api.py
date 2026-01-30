"""
Qatar API-based Dropdown Extractor
Main entry point for extracting all dropdown values using API calls.
Uses same Aura platform as Takaful.
"""

import asyncio
from playwright.async_api import Playwright, async_playwright
from src.pages.qatar.login_page import LoginPage
from src.pages.qatar.api import QatarAuthToken, QatarAPIExtractor, QatarFormatter
from src.utils.logger import qatar_logger


async def login_and_get_token(playwright: Playwright):
    """
    Login to Qatar portal and extract auth token.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        QatarAuthToken: Auth object with token set, or None on failure
    """
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        # Login using existing LoginPage
        login_page = LoginPage(page)
        await login_page.login()
        qatar_logger.debug("Login completed")
        
        # Wait for dashboard to ensure login is complete
        await page.wait_for_selector("text=Create new quote", timeout=80000)
        qatar_logger.debug("Dashboard loaded - Create new quote button visible")
        
        # Wait a bit more to ensure token is stored
        await asyncio.sleep(2)
        
        # Debug: Print all storage keys
        all_local_keys = await page.evaluate("() => Object.keys(localStorage)")
        all_session_keys = await page.evaluate("() => Object.keys(sessionStorage)")
        print(f"\n📋 localStorage keys found: {all_local_keys}")
        print(f"📋 sessionStorage keys found: {all_session_keys}")
        qatar_logger.debug(f"localStorage keys: {all_local_keys}")
        qatar_logger.debug(f"sessionStorage keys: {all_session_keys}")
        
        # Extract token
        auth = QatarAuthToken()
        token = await auth.extract_token_from_browser(page)
        
        if token:
            qatar_logger.debug(f"Token extracted successfully (length: {len(token)})")
            return auth
        else:
            qatar_logger.error("Failed to extract token")
            print("\n❌ Failed to extract token")
            return None
            
    finally:
        await browser.close()


async def run_qatar_api_extraction(playwright: Playwright, output_dir: str = "extracted_data"):
    """
    Main function to run Qatar API-based extraction.
    
    Args:
        playwright: Playwright instance
        output_dir: Base output directory for extracted files
        
    Returns:
        dict: Extraction results or None on failure
    """
    # Step 1: Login and get token
    print("\n🔐 Logging in to Qatar Insurance portal...")
    auth = await login_and_get_token(playwright)
    
    if not auth:
        qatar_logger.error("Cannot proceed without auth token")
        return None
    
    print("✅ Login successful, token obtained")
    print(f"   Token length: {len(auth.token)} characters")
    
    # Step 2: Extract all benefits
    print("\n" + "=" * 60)
    print("🔄 EXTRACTING BENEFIT DROPDOWNS")
    print("=" * 60)
    
    extractor = QatarAPIExtractor(auth)
    results = await extractor.extract_all_benefits()
    
    # Step 3: Save JSON results
    json_file = extractor.save_results(output_dir=output_dir)
    
    # Step 4: Print extraction summary
    extractor.print_summary()
    
    # Step 5: Format to text file
    print("\n" + "=" * 60)
    print("📝 FORMATTING OUTPUT")
    print("=" * 60)
    
    formatter = QatarFormatter(results)
    text_file = formatter.format_and_save(output_dir=output_dir)
    formatter.print_summary()
    
    print("\n" + "=" * 60)
    print("📁 OUTPUT FILES")
    print("=" * 60)
    print(f"   JSON: {json_file}")
    print(f"   TEXT: {text_file}")
    
    return results


async def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("🏢 QATAR INSURANCE - API EXTRACTION")
    print("=" * 60)
    
    async with async_playwright() as playwright:
        result = await run_qatar_api_extraction(playwright)
        
        if result:
            print("\n✅ Qatar API extraction setup complete")
        else:
            print("\n❌ Qatar API extraction failed")


if __name__ == "__main__":
    asyncio.run(main())
