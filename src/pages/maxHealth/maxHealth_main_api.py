"""
MaxHealth API-based Dropdown Extractor
Main entry point for extracting all dropdown values using API calls.
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import Playwright, async_playwright
from src.pages.maxHealth.login import Login
from src.pages.maxHealth.api import (
    MaxHealthAuthToken, 
    MaxHealthAPIClient, 
    MaxHealthExtractor,
    MaxHealthFormatter
)
from src.utils.logger import maxhealth_logger


async def login_and_get_token(playwright: Playwright):
    """
    Login to MaxHealth portal and extract auth token.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        tuple: (MaxHealthAuthToken, page) or (None, None) on failure
    """
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        # Create a minimal df1 for login (login doesn't use it much)
        import pandas as pd
        df1 = pd.DataFrame({'KEY': ['Email'], 'VALUE': ['dummy@email.com']})
        
        # Login using existing Login class
        login = Login(page)
        login_success = await login.perform_login(df1)
        
        if not login_success:
            maxhealth_logger.error("Login failed")
            print("\n❌ Login failed")
            await browser.close()
            return None, None
        
        maxhealth_logger.debug("Login completed")
        print("✅ Login successful")
        
        # Wait for token to be stored in localStorage
        await asyncio.sleep(5)
        
        # Extract token
        auth = MaxHealthAuthToken()
        token = await auth.extract_token_from_browser(page)
        
        if token:
            maxhealth_logger.debug(f"Token extracted successfully (length: {len(token)})")
            print(f"✅ Token extracted from {auth.token_type}")
            print(f"   Token length: {len(token)} characters")
            # Don't close browser yet - return page for further use
            return auth, page, browser
        else:
            maxhealth_logger.error("Failed to extract token")
            print("\n❌ Failed to extract token")
            await browser.close()
            return None, None, None
            
    except Exception as e:
        maxhealth_logger.error(f"Error during login: {e}")
        print(f"\n❌ Error: {e}")
        await browser.close()
        return None, None, None


async def run_maxhealth_api_extraction(playwright: Playwright):
    """
    Main function to run MaxHealth API-based extraction.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        dict: Extraction results or None on failure
    """
    # Step 1: Login and get token
    print("\n🔐 Logging in to MaxHealth portal...")
    result = await login_and_get_token(playwright)
    
    if result[0] is None:
        maxhealth_logger.error("Cannot proceed without auth token")
        return None
    
    auth, page, browser = result
    
    try:
        print("\n" + "=" * 60)
        print("🔄 TOKEN EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"   Token Type: {auth.token_type}")
        print(f"   Token Length: {len(auth.token)} characters")
        print(f"   Token Preview: {auth.token[:50]}...")
        
        # Step 2: Use extractor to get all data including plans
        print("\n" + "=" * 60)
        print("📡 EXTRACTING ALL DROPDOWN VALUES")
        print("=" * 60)
        
        extractor = MaxHealthExtractor(auth)
        results = await extractor.extract_all()
        
        if not results:
            print("❌ Failed to extract data")
            return None
        
        # Step 3: Save JSON results
        json_file = extractor.save_results()
        extractor.print_summary()
        
        # Step 4: Format and save to text file
        print("\n" + "=" * 60)
        print("📄 FORMATTING OUTPUT")
        print("=" * 60)
        
        formatter = MaxHealthFormatter(results)
        txt_file = formatter.format_and_save()
        formatter.print_summary()
        
        return {
            "token_extracted": True, 
            "token_length": len(auth.token),
            "token_type": auth.token_type,
            "json_file": json_file,
            "txt_file": txt_file,
            "plans_extracted": len(results.get("plans_by_combination", {}))
        }
        
    finally:
        # Close browser
        await browser.close()


async def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("🏥 MAXHEALTH - API EXTRACTION")
    print("=" * 60)
    print("📍 Portal: https://portal.maxhealth.ae")
    print("=" * 60)
    
    async with async_playwright() as playwright:
        result = await run_maxhealth_api_extraction(playwright)
        
        if result:
            print("\n" + "=" * 60)
            print("✅ MAXHEALTH EXTRACTION COMPLETE")
            print("=" * 60)
            print(f"   JSON File: {result.get('json_file', 'N/A')}")
            print(f"   TXT File: {result.get('txt_file', 'N/A')}")
            print(f"   Plans Combinations: {result.get('plans_extracted', 0)}")
        else:
            print("\n❌ MaxHealth extraction failed")


if __name__ == "__main__":
    asyncio.run(main())
