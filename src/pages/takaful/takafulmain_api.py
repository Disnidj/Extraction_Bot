"""
Takaful API-based Dropdown Extractor
Main entry point for extracting all dropdown values using API calls.
"""

import asyncio
from playwright.async_api import Playwright
from src.pages.takaful.login_page import LoginPage
from src.pages.takaful.api import TakafulAuthToken, TakafulAPIExtractor, TakafulFormatter
from src.utils.logger import takaful_logger


async def login_and_get_token(playwright: Playwright):
    """
    Login to Takaful portal and extract auth token.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        TakafulAuthToken: Auth object with token set, or None on failure
    """
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        # Login using existing LoginPage
        login_page = LoginPage(page)
        await login_page.login()
        takaful_logger.debug("Login completed")
        
        # Wait for dashboard to ensure login is complete
        await page.wait_for_selector('text="Create new quote"', timeout=30000)
        
        # Extract token
        auth = TakafulAuthToken()
        token = await auth.extract_token_from_browser(page)
        
        if token:
            takaful_logger.debug(f"Token extracted successfully (length: {len(token)})")
            return auth
        else:
            takaful_logger.error("Failed to extract token")
            print("\n❌ Failed to extract token")
            return None
            
    finally:
        await browser.close()


async def run_takaful_api_extraction(playwright: Playwright):
    """
    Main function to run Takaful API-based extraction.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        dict: Extraction results or None on failure
    """
    # Step 1: Login and get token
    print("\n🔐 Logging in to Takaful portal...")
    auth = await login_and_get_token(playwright)
    
    if not auth:
        takaful_logger.error("Cannot proceed without auth token")
        return None
    
    print("✅ Login successful, token obtained")
    
    # Step 2: Extract all benefits
    print("\n" + "=" * 60)
    print("🔄 EXTRACTING BENEFIT DROPDOWNS")
    print("=" * 60)
    
    extractor = TakafulAPIExtractor(auth)
    results = await extractor.extract_all_benefits()
    
    # Step 3: Save JSON results
    json_file = extractor.save_results()
    
    # Step 4: Print extraction summary
    extractor.print_summary()
    
    # Step 5: Format to text file
    print("\n" + "=" * 60)
    print("📝 FORMATTING OUTPUT")
    print("=" * 60)
    
    formatter = TakafulFormatter(results)
    text_file = formatter.format_and_save()
    formatter.print_summary()
    
    print("\n" + "=" * 60)
    print("📁 OUTPUT FILES")
    print("=" * 60)
    print(f"   JSON: {json_file}")
    print(f"   TEXT: {text_file}")
    
    return results


# Allow running this file directly
if __name__ == "__main__":
    from playwright.async_api import async_playwright
    
    async def main():
        print("\n" + "=" * 60)
        print("🔐 TAKAFUL BENEFIT EXTRACTION")
        print("=" * 60)
        print("📍 Target: Dubai only")
        print("📍 TPAs: Aafiya, Mednet, Nas, Nextcare")
        print("📍 Excluded: Aafiya Ebp")
        print("=" * 60)
        
        async with async_playwright() as playwright:
            results = await run_takaful_api_extraction(playwright)
            
            if results:
                print("\n✅ Extraction completed successfully!")
            else:
                print("\n❌ Extraction failed")
    
    asyncio.run(main())
