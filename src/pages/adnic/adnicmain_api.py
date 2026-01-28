"""
ADNIC API-Based Extraction Entry Point

This module provides the main entry point for ADNIC API extraction.
Follows the same pattern as Takaful's takafulmain_api.py.

Flow:
1. Launch browser & login (using api/auth.py)
2. Establish session (form fill + census upload)
3. Extract dropdown values via APIs (using api/extractor.py)
4. Format and save results (using api/formatter.py)

Usage:
    Can be called from main.py or run directly:
    python -m src.pages.adnic.adnicmain_api
"""

from patchright.async_api import Playwright
from src.pages.adnic.api import ADNICAuth, ADNICApiExtractor, ADNICFormatter
from src.utils.logger import adnic_logger


async def login_adnic_api(playwright: Playwright, referral_id=None):
    """
    ADNIC API extraction mode - main entry point.
    
    This function is called from main.py when running API extraction mode.
    Follows the same pattern as Takaful's login_takaful_api.
    
    Flow:
    1. Establish authenticated session via browser
    2. Extract ALL dropdown combinations via direct API calls
    3. Save results to extracted_data file
    
    Args:
        playwright: Playwright instance
        referral_id: Optional referral ID (not used for API extraction)
        
    Returns:
        bool: True if extraction successful
    """
    adnic_logger.info("🚀 ADNIC API Extraction Mode Started")
    
    auth = None
    
    try:
        # =====================================================
        # Step 1-5: Establish authenticated session
        # =====================================================
        auth = ADNICAuth(playwright)
        page = await auth.establish_session()
        
        # =====================================================
        # Step 6: Run API extraction
        # =====================================================
        print("\n🔌 Step 6: Starting API extraction...\n")
        
        extractor = ADNICApiExtractor(page)
        records = await extractor.extract_all()
        
        # =====================================================
        # Step 7: Save results to portal-specific folder
        # Formatter creates: extracted_data/adnic/adnic_extracted_YYYYMMDD_HHMMSS.txt
        # =====================================================
        formatter = ADNICFormatter()  # No path - uses portal-specific path
        output_path = formatter.write_records(records)
        
        # =====================================================
        # Step 8: Cleanup
        # =====================================================
        await auth.close()
        
        adnic_logger.info(f"✅ ADNIC API Extraction Complete! {len(records)} records saved to {output_path}")
        return True
        
    except Exception as e:
        adnic_logger.error(f"❌ ADNIC API extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if auth:
            await auth.close()


# Allow running directly
if __name__ == "__main__":
    import asyncio
    from playwright.async_api import async_playwright
    from src.utils.load_yaml import set_extracted_data_file
    from src.utils.clear_folder import clear_files
    
    async def main():
        print("\n" + "=" * 60)
        print("🔌 ADNIC API EXTRACTION - Direct Run")
        print("=" * 60)
        
        # Setup
        await clear_files()
        set_extracted_data_file()
        
        # Run extraction
        async with async_playwright() as playwright:
            success = await login_adnic_api(playwright)
            
            if success:
                print("\n✅ Extraction completed successfully!")
            else:
                print("\n❌ Extraction failed!")
    
    asyncio.run(main())
