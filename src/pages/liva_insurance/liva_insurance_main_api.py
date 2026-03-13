"""
Liva Insurance API-Based Extraction Entry Point

Flow:
1. Launch browser & login (using api/auth.py - based on NLG login flow)
2. Establish session (SME selection + form fill + census upload)
3. Extract dropdown values via APIs (using api/extractor.py - ADNIC pattern)
4. Format and save results (using api/formatter.py)
"""

from patchright.async_api import Playwright
from src.pages.liva_insurance.api import LivaInsuranceAuth, LivaInsuranceApiExtractor, LivaInsuranceFormatter
from src.utils.logger import liva_insurance_logger


async def run_liva_insurance_api_extraction(playwright: Playwright, referral_id=None, output_dir: str = "extracted_data"):
    """
    Liva Insurance API extraction mode - main entry point.

    Called from main.py when running API extraction mode.

    Args:
        playwright: Playwright instance
        referral_id: Optional referral ID (not used for API extraction)
        output_dir: Base output directory for extracted files

    Returns:
        dict: {"success": bool, "results": dict or None, "errors": list}
    """
    liva_insurance_logger.info("🚀 Liva Insurance API Extraction Mode Started")

    auth = None

    try:
        # =====================================================
        # Steps 1-6: Establish authenticated session
        # =====================================================
        auth = LivaInsuranceAuth(playwright)
        page = await auth.establish_session()

        # =====================================================
        # Step 7: Run API extraction
        # =====================================================
        print("\n🔌 Step 7: Starting API extraction...\n")

        extractor = LivaInsuranceApiExtractor(page)
        records = await extractor.extract_all()

        # =====================================================
        # Step 7.5: Validate extraction results
        # =====================================================
        is_valid, validation_errors = extractor.validate_extraction()

        if not is_valid:
            liva_insurance_logger.error("❌ Liva Insurance extraction validation failed")
            print("\n" + "=" * 60)
            print("❌ LIVA INSURANCE API EXTRACTION FAILED - VALIDATION ERRORS")
            print("=" * 60)
            for error in validation_errors:
                print(f"   • {error}")
            print("=" * 60)

            await auth.close()
            return {
                "success": False,
                "results": None,
                "errors": validation_errors + ["Liva Insurance extraction incomplete"]
            }

        # =====================================================
        # Step 8: Save results to portal-specific folder
        # =====================================================
        formatter = LivaInsuranceFormatter(output_dir=output_dir)
        output_path = formatter.write_records(records)

        # =====================================================
        # Step 9: Cleanup
        # =====================================================
        await auth.close()

        liva_insurance_logger.info(f"✅ Liva Insurance API Extraction Complete! {len(records)} records saved to {output_path}")
        return {"success": True, "results": {"records": len(records)}, "errors": []}

    except Exception as e:
        liva_insurance_logger.error(f"❌ Liva Insurance API extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "results": None, "errors": [f"Liva Insurance API extraction failed: {str(e)}"]}

    finally:
        if auth:
            await auth.close()


# Allow running directly
if __name__ == "__main__":
    import asyncio
    from patchright.async_api import async_playwright
    from src.utils.load_yaml import set_extracted_data_file
    from src.utils.clear_folder import clear_files

    async def main():
        print("\n" + "=" * 60)
        print("🔌 LIVA INSURANCE API EXTRACTION - Direct Run")
        print("=" * 60)

        await clear_files()
        set_extracted_data_file()

        async with async_playwright() as playwright:
            result = await run_liva_insurance_api_extraction(playwright)

            if result["success"]:
                print("\n✅ Extraction completed successfully!")
            else:
                print("\n❌ Extraction failed!")
                for error in result.get("errors", []):
                    print(f"   • {error}")

    asyncio.run(main())
