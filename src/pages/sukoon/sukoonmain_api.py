"""
Sukoon API-Based Extraction Entry Point

This module provides the main entry point for Sukoon API extraction.
Follows the same pattern as ADNIC's adnicmain_api.py and Takaful's takafulmain_api.py.

Sukoon uses a "Mega API" pattern:
- Single endpoint: PopulateDDL
- One call returns ALL options for a given indemnityId
- Much simpler than ADNIC's 14-endpoint cascading system

Flow:
1. Launch browser & login (using api/auth.py)
2. Establish session (form fill + optional census upload)
3. Extract dropdown values via PopulateDDL API (using api/extractor.py)
4. Format and save results (using api/formatter.py)

Usage:
    Can be called from main.py or run directly:
    python -m src.pages.sukoon.sukoonmain_api
"""

from patchright.async_api import Playwright
from src.pages.sukoon.api import SukoonAuth, SukoonApiExtractor, SukoonFormatter
from src.utils.logger import sukoon_logger


async def login_sukoon_api(playwright: Playwright, referral_id=None, output_dir: str = "extracted_data"):
    """
    Sukoon API extraction mode - main entry point.
    
    This function is called from main.py when running API extraction mode.
    Follows the same pattern as ADNIC's login_adnic_api.
    
    Flow:
    1. Establish authenticated session via browser
    2. Extract ALL dropdown combinations via PopulateDDL API
    3. Save results to extracted_data/sukoon/
    
    Args:
        playwright: Playwright instance
        referral_id: Optional referral ID (not used for API extraction)
        output_dir: Base output directory for extracted files
        
    Returns:
        bool: True if extraction successful
    """
    sukoon_logger.info("🚀 Sukoon API Extraction Mode Started")
    print("\n" + "=" * 60)
    print("🔌 SUKOON API EXTRACTION MODE")
    print("=" * 60)
    print("📌 Using Mega API pattern (PopulateDDL)")
    print("📌 Single API returns all options per indemnity level")
    print("=" * 60)
    
    auth = None
    
    try:
        # =====================================================
        # Step 1-5: Establish authenticated session
        # =====================================================
        auth = SukoonAuth(playwright)
        page = await auth.establish_session(region="Dubai")
        
        # =====================================================
        # Step 6: Run API extraction
        # =====================================================
        print("\n🔌 Step 6: Starting API extraction...\n")
        
        # Get Business Nature options extracted during auth flow
        business_nature_options = auth.get_business_nature_options()
        
        extractor = SukoonApiExtractor(page, business_nature_options=business_nature_options)
        records = await extractor.extract_all(regions=["Dubai"])
        
        # =====================================================
        # Step 7: Save results to portal-specific folder
        # Formatter creates: {output_dir}/sukoon/sukoon_extracted_YYYYMMDD_HHMMSS.txt
        # =====================================================
        formatter = SukoonFormatter(output_dir=output_dir)
        output_path = formatter.write_records(records)
        
        # Also save as JSON for structured access
        formatter.write_json(records)
        
        # =====================================================
        # Step 8: Cleanup
        # =====================================================
        await auth.close()
        
        sukoon_logger.info(f"✅ Sukoon API Extraction Complete! {len(records)} records saved to {output_path}")
        print(f"\n✅ Sukoon API Extraction Complete!")
        print(f"   Records saved: {len(records)}")
        print(f"   Output file: {output_path}")
        
        return {"success": True, "results": {"records": len(records)}, "errors": []}
        
    except Exception as e:
        sukoon_logger.error(f"❌ Sukoon API extraction failed: {e}")
        print(f"\n❌ Sukoon API extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "results": None, "errors": [f"Sukoon API extraction failed: {str(e)}"]}
        
    finally:
        if auth:
            await auth.close()


async def run_sukoon_api_extraction(playwright: Playwright, referral_id=None, output_dir: str = "extracted_data"):
    """
    Alias for login_sukoon_api for consistency with other portals.
    """
    return await login_sukoon_api(playwright, referral_id, output_dir=output_dir)


# Allow running directly
if __name__ == "__main__":
    import asyncio
    from patchright.async_api import async_playwright
    
    async def main():
        print("\n" + "=" * 60)
        print("🔌 SUKOON API EXTRACTION - Direct Run")
        print("=" * 60)
        
        async with async_playwright() as playwright:
            success = await login_sukoon_api(playwright)
            
            if success:
                print("\n✅ Extraction completed successfully!")
            else:
                print("\n❌ Extraction failed!")
    
    asyncio.run(main())
