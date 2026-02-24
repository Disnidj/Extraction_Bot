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


async def login_adnic_api(playwright: Playwright, referral_id=None, output_dir: str = "extracted_data"):
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
        output_dir: Base output directory for extracted files
        
    Returns:
        bool: True if extraction successful
    """
    adnic_logger.info("🚀 ADNIC API Extraction Mode Started")
    
    auth = None
    
    try:
        # =====================================================
        # Step 1-5: Establish authenticated session
        # (Also extracts Business Nature during Step 2)
        # =====================================================
        auth = ADNICAuth(playwright)
        page = await auth.establish_session()
        
        # Get Business Nature options extracted during auth
        business_nature_options = auth.get_business_nature_options()
        
        # =====================================================
        # Step 6: Run API extraction
        # =====================================================
        print("\n🔌 Step 6: Starting API extraction...\n")
        
        extractor = ADNICApiExtractor(page, business_nature_options=business_nature_options)
        records = await extractor.extract_all()
        
        # =====================================================
        # Step 6.5: Validate extraction results
        # =====================================================
        is_valid, validation_errors = extractor.validate_extraction()
        
        if not is_valid:
            adnic_logger.error("❌ ADNIC extraction validation failed - marking portal as FAILED")
            print("\n" + "=" * 60)
            print("❌ ADNIC API EXTRACTION FAILED - VALIDATION ERRORS")
            print("=" * 60)
            for error in validation_errors:
                print(f"   • {error}")
            print("=" * 60)
            print("\n⚠️  Portal will NOT proceed to staging due to incomplete data extraction.")
            print("    This prevents corrupted data from overwriting valid database records.")
            
            await auth.close()
            return {
                "success": False, 
                "results": None, 
                "errors": validation_errors + ["ADNIC extraction incomplete - portal marked as FAILED"]
            }
        
        # =====================================================
        # Step 7: Save results to portal-specific folder
        # Formatter creates: {output_dir}/adnic/adnic_extracted_YYYYMMDD_HHMMSS.txt
        # =====================================================
        formatter = ADNICFormatter(output_dir=output_dir)
        output_path = formatter.write_records(records)
        
        # =====================================================
        # Step 8: Cleanup
        # =====================================================
        await auth.close()
        
        adnic_logger.info(f"✅ ADNIC API Extraction Complete! {len(records)} records saved to {output_path}")
        return {"success": True, "results": {"records": len(records)}, "errors": []}
        
    except Exception as e:
        adnic_logger.error(f"❌ ADNIC API extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "results": None, "errors": [f"ADNIC API extraction failed: {str(e)}"]}
        
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
