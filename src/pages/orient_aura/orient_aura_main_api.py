"""
Orient Aura API-based Dropdown Extractor
Main entry point for extracting all dropdown values using API calls.

This follows the same pattern as Takaful and Qatar API extractions.
"""

import asyncio
from playwright.async_api import Playwright, async_playwright
from src.pages.orient_aura.login_page import LoginPage
from src.pages.orient_aura.api import OrientAuraAuthToken, OrientAuraAPIExtractor, OrientAuraFormatter
from src.utils.logger import orient_aura_logger


async def login_and_get_token(playwright: Playwright):
    """
    Login to Orient Aura portal and extract auth token.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        OrientAuraAuthToken: Auth object with token set, or None on failure
    """
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        # Login using LoginPage with retry logic (handles 90s timeout internally)
        login_page = LoginPage(page)
        await login_page.login()
        orient_aura_logger.debug("Login completed")
        
        # Extract token
        auth = OrientAuraAuthToken()
        token = await auth.extract_token_from_browser(page)
        
        if token:
            orient_aura_logger.debug(f"Token extracted successfully (length: {len(token)})")
            return auth
        else:
            orient_aura_logger.error("Failed to extract token")
            print("\n❌ Failed to extract token")
            return None
            
    finally:
        await browser.close()


async def run_orient_aura_api_extraction(playwright: Playwright, output_dir: str = "extracted_data"):
    """
    Main function to run Orient Aura API-based extraction.
    
    Args:
        playwright: Playwright instance
        output_dir: Base output directory for extracted files
        
    Returns:
        dict: Extraction results or None on failure
    """
    # Step 1: Login and get token
    print("\n🔐 Logging in to Orient Aura portal...")
    auth = await login_and_get_token(playwright)
    
    if not auth:
        orient_aura_logger.error("Cannot proceed without auth token")
        return {"success": False, "results": None, "errors": ["Login failed - could not authenticate or extract token"]}
    
    print("✅ Login successful, token obtained")
    print(f"   Token length: {len(auth.token)} characters")
    print(f"   Region: Dubai only (like Takaful/Qatar/ADNIC)")
    
    # Step 2: Extract all benefits
    print("\n" + "=" * 60)
    print("🔄 EXTRACTING BENEFIT DROPDOWNS")
    print("=" * 60)
    
    extractor = OrientAuraAPIExtractor(auth)
    results = await extractor.extract_all_benefits()
    
    # Step 3: Save JSON results
    json_file = extractor.save_results(output_dir=output_dir)
    
    # Step 4: Print extraction summary
    extractor.print_summary()
    
    # Step 5: Format to text file
    print("\n" + "=" * 60)
    print("📝 FORMATTING OUTPUT")
    print("=" * 60)
    
    formatter = OrientAuraFormatter(results)
    text_file = formatter.format_and_save(output_dir=output_dir)
    formatter.print_summary()
    
    print("\n" + "=" * 60)
    print("📁 OUTPUT FILES")
    print("=" * 60)
    print(f"   JSON: {json_file}")
    print(f"   TEXT: {text_file}")
    
    # Check for errors during extraction
    errors = results.get("errors", [])
    if errors:
        print("\n" + "=" * 60)
        print("⚠️ EXTRACTION ERRORS")
        print("=" * 60)
        for error in errors:
            print(f"   ❌ {error}")
        orient_aura_logger.error(f"Extraction completed with {len(errors)} error(s): {errors}")
        print("\n❌ Orient Aura extraction completed with errors!")
        return {"success": False, "results": results, "errors": errors}
    
    print("\n✅ Orient Aura extraction completed!")
    return {"success": True, "results": results, "errors": []}


async def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("🏢 ORIENT AURA - API EXTRACTION")
    print("=" * 60)
    print("📍 Extracting all Groups, Emirates, TPAs, Plans, and Benefits")
    print("=" * 60)
    
    async with async_playwright() as playwright:
        result = await run_orient_aura_api_extraction(playwright)
        
        if result:
            print("\n✅ Orient Aura API extraction completed successfully!")
        else:
            print("\n❌ Orient Aura API extraction failed")


# Allow running this file directly
if __name__ == "__main__":
    asyncio.run(main())
