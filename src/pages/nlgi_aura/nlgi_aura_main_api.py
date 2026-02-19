"""
NLGI Aura API-based Dropdown Extractor
Main entry point for extracting all dropdown values using API calls.

This follows the same pattern as Takaful, Qatar, and Orient Aura API extractions.
"""

import asyncio
from playwright.async_api import Playwright, async_playwright
from src.pages.nlgi_aura.login_page import LoginPage
from src.pages.nlgi_aura.api import NLGIAuraAuthToken, NLGIAuraAPIExtractor, NLGIAuraFormatter
from src.utils.logger import nlgi_aura_logger


async def login_and_get_token(playwright: Playwright):
    """
    Login to NLGI Aura portal and extract auth token.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        NLGIAuraAuthToken: Auth object with token set, or None on failure
    """
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        # Perform login with retries (navigation happens inside)
        login_page = LoginPage(page)
        login_success = await login_page.login()
        
        if not login_success:
            nlgi_aura_logger.error("Login failed after retries")
            await browser.close()
            return None
        
        nlgi_aura_logger.info("Login completed")
        
        # Extract token using updated auth pattern (matching Orient/Qatar)
        auth = NLGIAuraAuthToken()
        token = await auth.extract_token_from_browser(page)
        
        if not token:
            nlgi_aura_logger.error("Failed to extract auth token")
            await browser.close()
            return None
        
        nlgi_aura_logger.debug(f"Token extracted successfully (length: {len(token)})")
        
        # Close browser
        await browser.close()
        
        return auth
        
    except Exception as e:
        nlgi_aura_logger.error(f"Login error: {str(e)}", exc_info=True)
        await browser.close()
        return None


async def run_nlgi_aura_api_extraction(playwright: Playwright, output_dir: str = "extracted_data"):
    """
    Main function to run NLGI Aura API-based extraction.
    
    Args:
        playwright: Playwright instance
        output_dir: Base output directory for extracted files
        
    Returns:
        dict: Extraction results or None on failure
    """
    # Step 1: Login and get token
    print("\n🔐 Logging in to NLGI Aura portal...")
    auth = await login_and_get_token(playwright)
    
    if not auth:
        nlgi_aura_logger.error("Cannot proceed without auth token")
        return None
    
    print("✅ Login successful, token obtained")
    print(f"   Token length: {len(auth.token)} characters")
    print(f"   Region: Dubai only (like Takaful/Qatar/Orient Aura)")
    
    # Step 2: Extract all benefits
    print("\n" + "=" * 60)
    print("🔄 EXTRACTING BENEFIT DROPDOWNS")
    print("=" * 60)
    
    extractor = NLGIAuraAPIExtractor(auth)
    results = await extractor.extract_all_benefits()
    
    # Step 3: Save JSON results
    json_file = extractor.save_results(output_dir=output_dir)
    
    # Step 4: Print extraction summary
    extractor.print_summary()
    
    # Step 5: Format to text file
    print("\n" + "=" * 60)
    print("📝 FORMATTING OUTPUT")
    print("=" * 60)
    
    formatter = NLGIAuraFormatter(results)
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
        nlgi_aura_logger.error(f"Extraction completed with {len(errors)} error(s): {errors}")
        print("\n❌ NLGI Aura extraction completed with errors!")
        return {"success": False, "results": results, "errors": errors}
    
    print("\n✅ NLGI Aura extraction completed!")
    return {"success": True, "results": results, "errors": []}


async def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("🏢 NLGI AURA - API EXTRACTION")
    print("=" * 60)
    print("📍 Extracting all Groups, Emirates, TPAs, Plans, and Benefits")
    print("=" * 60)
    
    async with async_playwright() as playwright:
        result = await run_nlgi_aura_api_extraction(playwright)
        
        if result:
            print("\n✅ NLGI Aura API extraction completed successfully!")
        else:
            print("\n❌ NLGI Aura API extraction failed")


# Allow running this file directly
if __name__ == "__main__":
    asyncio.run(main())
