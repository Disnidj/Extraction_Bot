import asyncio
from playwright.async_api import async_playwright
import subprocess
from datetime import datetime

# --- Imports for portals and census mapping ---
from src.pages.takaful.takafulmain import login_takaful
from src.pages.medgulf.medgulf_main import login_medgulf
from src.pages.alittihad_alwatani.ai_ittihad_ai_watani_main import login_ai_ittihad_ai_watani
from src.pages.adnic.adnic_main import login_adnic
from src.pages.alsagr.alsagr_main import login_alsagr
from src.pages.gig.gig_main import login_gig
from src.pages.dubaiinsurance.dubaiInsurance_main import login_dubaiInsurance
from src.pages.sukoon.sukoon_main import login_sukoon
from src.pages.orient.orient_main import login_orient
from src.pages.dni.dni_main import login_dni
from src.pages.qatar.qatar_main import login_qatar
from src.pages.ison.ison_main import login_ison
from src.pages.fidelity.fidelity_main import login_fidelity
from src.pages.nlg.nlg_main import login_nlg
from src.pages.wataniatakaful.watania_takafulmain import login_wataniatakaful
from src.pages.daman.damanmain import login_daman
from src.pages.rak.rak_main import login_rak
from src.pages.maxHealth.maxHealth_main import login_maxHealth

# --- Imports for API-based extraction ---
from src.pages.adnic.adnicmain_api import login_adnic_api
from src.pages.takaful.takafulmain_api import run_takaful_api_extraction
from src.pages.qatar.qatar_main_api import run_qatar_api_extraction
from src.pages.sukoon.sukoonmain_api import login_sukoon_api
from src.utils.logger import set_current_request_id, issues_logger, logger, main_execution_logger, clear_all_logs
from src.utils.clear_folder import clear_files
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_service.read_cloud_requests import process_next_pending_request
from src.services.excel_service.nlg_census_map import nlg_map_census_data
from src.services.excel_service.aura_census_map import aura_map_census_data
from src.services.excel_service.sukoon_census_map import sukoon_map_census_data
from src.services.excel_service.dubai_census_map import dubai_map_census_data
from src.services.excel_service.union_census_map import union_map_census_data
from src.services.excel_service.alsagr_census_map import alsagr_map_census_data
from src.services.excel_service.adnic_census_map import adnic_map_census_data
from src.services.excel_service.gig_census_map import gig_map_census_data
from src.services.excel_service.iq_census_map import iq_map_census_data
from src.services.excel_service.daman_census_map import daman_map_census_data
from src.utils.load_yaml import MAX_RETRIES, set_extracted_data_file
# from src.services.company_selector import get_company_selection, filter_portal_list
from src.services.company_selector_updated import get_company_selection, filter_portal_list
# Configurable parameter for parallel execution
MAX_PARALLEL_PORTALS = 3

# Portal definitions for parallel execution
PORTAL_GROUPS = {
    "main_portals": [
        {"function": login_medgulf, "name": "Medgulf"},
        {"function": login_takaful, "name": "Takaful"},
        {"function": login_orient, "name": "Orient"},
        {"function": login_ai_ittihad_ai_watani, "name": "Alittihad_Alwatani"},
        {"function": login_adnic, "name": "ADNIC"},
        {"function": login_alsagr, "name": "ALSAGR"},
        {"function": login_gig, "name": "GIG"},
        {"function": login_dubaiInsurance, "name": "Dubaiinsurance"},
        {"function": login_sukoon, "name": "Sukoon"},
        {"function": login_dni, "name": "DNI"},
        {"function": login_qatar, "name": "QATAR"},
        {"function": login_ison, "name": "ISON"},
        {"function": login_wataniatakaful, "name": "Wataniatakaful"},
        {"function": login_nlg, "name": "NLG"},
        {"function": login_fidelity, "name": "Fidelity"},
        {"function": login_daman, "name": "Daman"},
        {"function": login_rak, "name": "RAK"},
        {"function": login_maxHealth, "name": "MaxHealth"},
    ]
}

# API extraction portal definitions
# Portals with direct API extraction capability (no database/census required)
API_PORTAL_GROUPS = {
    "api_portals": [
        {"function": login_adnic_api, "name": "ADNIC"},
        {"function": run_takaful_api_extraction, "name": "Takaful"},
        {"function": run_qatar_api_extraction, "name": "QATAR"},
        {"function": login_sukoon_api, "name": "Sukoon"},
    ]
}

# Census mapping functions list
CENSUS_FUNCTIONS = [
    nlg_map_census_data, aura_map_census_data, sukoon_map_census_data,
    dubai_map_census_data, union_map_census_data, alsagr_map_census_data,
    adnic_map_census_data, gig_map_census_data, iq_map_census_data,
    daman_map_census_data
]

async def run_census_mapping():
    """Execute all census mapping functions."""
    for func in CENSUS_FUNCTIONS:
        try:
            func('default')
            print(f"Successfully executed {func.__name__}")
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")

async def login_portal_with_semaphore(sem, portal, playwright, results, portal_timings, env='default'):
    """Run a single portal login with semaphore control and timing tracking."""
    portal_name = portal["name"]
    async with sem:
        # Record start time
        start_time = datetime.now()
        portal_timings[portal_name] = {'start': start_time, 'end': None, 'duration': None}
        
        print(f"Started login for {portal_name}")
        main_execution_logger.info(f"🚀 Portal '{portal_name}' - Started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            result = await portal["function"](playwright, env)
            results[portal_name] = result
        except Exception as e:
            print(f"Error in {portal_name}: {e}")
            main_execution_logger.error(f"❌ Portal '{portal_name}' - Error: {e}")
            results[portal_name] = False
        
        # Record end time and calculate duration
        end_time = datetime.now()
        duration = end_time - start_time
        portal_timings[portal_name]['end'] = end_time
        portal_timings[portal_name]['duration'] = duration
        
        print(f"Completed login for {portal_name}")
        main_execution_logger.info(
            f"✅ Portal '{portal_name}' - Completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Duration: {duration.total_seconds():.2f}s ({int(duration.total_seconds() // 60)}m {int(duration.total_seconds() % 60)}s)"
        )

async def run_portals_with_concurrency_limit(portals, playwright, env='default'):
    """Run all portals with a concurrency limit and return results with timings."""
    sem = asyncio.Semaphore(MAX_PARALLEL_PORTALS)
    results = {}
    portal_timings = {}
    tasks = [asyncio.create_task(login_portal_with_semaphore(sem, portal, playwright, results, portal_timings, env)) for portal in portals]
    await asyncio.gather(*tasks)
    return results, portal_timings

def final_update_status(req_id, new_status):
    """Opens a dedicated connection to perform the final status update."""
    db = None
    try:
        db = MySQLDatabase(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
        if db.connect():
            from src.services.db_service.read_cloud_requests import update_request_status
            update_request_status(db, req_id, new_status)
    except Exception as e:
        print(f"An error occurred during final status update: {e!r}")
    finally:
        if db and db.is_connected():
            db.disconnect()

async def run_value_comparison():
    """Execute the value comparison service after extraction is completed."""
    try:
        print("\n🔄 Starting value comparison process...")
        
        # Run the value comparison service
        result = subprocess.run([
            "python", "-m", "src.services.value_comparison_service.value_comparison_main"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Value comparison completed successfully!")
        print(f"Output: {result.stdout}")
        
        if result.stderr:
            print(f"Warnings: {result.stderr}")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Value comparison failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        print(f"Standard output: {e.stdout}")
        return False
    except Exception as e:
        print(f"❌ Error running value comparison: {e}")
        return False


def get_extraction_mode():
    """
    Ask user to select extraction mode.
    
    Returns:
        str: 'standard' for regular extraction, 'api' for API-based extraction
    """
    print("\n" + "=" * 70)
    print("📋 SELECT EXTRACTION MODE")
    print("=" * 70)
    print("\n1. Standard Extraction (requires database + census data)")
    print("   → Processes pending requests from database")
    print("   → Uses real census data for quotation extraction")
    print("")
    print("2. API Extraction (no database required)")
    print("   → Extracts ALL dropdown values directly from portal APIs")
    # print("   → Available portals: ADNIC, Takaful, Qatar")
    print("=" * 70)
    
    while True:
        choice = input("\nEnter mode (1 or 2): ").strip()
        if choice == '1':
            return 'standard'
        elif choice == '2':
            return 'api'
        else:
            print("Invalid choice. Please enter 1 or 2.")


async def run_api_extraction_mode(playwright, selected_companies):
    """
    Run API-based extraction mode with timing tracking.
    
    Args:
        playwright: Playwright instance
        selected_companies: List of selected company names
    """
    # Filter to portals with API extraction available
    api_portals = API_PORTAL_GROUPS["api_portals"]
    api_portal_names = [p["name"] for p in api_portals]
    
    # Map selected companies to portal names
    from src.services.company_selector_updated import COMPANY_TO_FUNCTION_MAPPING
    selected_portal_names = [COMPANY_TO_FUNCTION_MAPPING.get(c, c) for c in selected_companies]
    
    # Find matching API portals
    matching_portals = [p for p in api_portals if p["name"] in selected_portal_names]
    unavailable = [n for n in selected_portal_names if n not in api_portal_names]
    
    if unavailable:
        print(f"\n⚠️  No API extraction implemented yet for: {', '.join(unavailable)}")
        print("   These will be skipped.")
    
    if not matching_portals:
        print("\n❌ None of the selected portals have API extraction implemented.")
        print(f"   Available API portals: {', '.join(api_portal_names)}")
        return
    
    print(f"\n✅ Will extract from: {', '.join([p['name'] for p in matching_portals])}")
    
    # Confirm
    confirm = input("\n▶️  Press Enter to start API extraction (or 'q' to quit): ").strip().lower()
    if confirm == 'q':
        print("👋 Cancelled.")
        return
    
    # Record overall start time
    overall_start_time = datetime.now()
    main_execution_logger.info(f"\n{'='*70}")
    main_execution_logger.info(f"🚀 API EXTRACTION FLOW STARTED")
    main_execution_logger.info(f"Start Time: {overall_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_execution_logger.info(f"Portals to process: {', '.join([p['name'] for p in matching_portals])}")
    main_execution_logger.info(f"{'='*70}")
    
    # Note: Each portal creates its own output folder and file
    # e.g., extracted_data/adnic/adnic_extracted_20260128_132144.txt
    #       extracted_data/takaful/takaful_extracted_20260128_133022.txt
    
    portal_timings = {}
    
    # Run extraction for each portal
    for portal in matching_portals:
        print(f"\n{'=' * 60}")
        print(f"🔄 Starting API extraction: {portal['name']}")
        print(f"{'=' * 60}")
        
        portal_start = datetime.now()
        portal_timings[portal['name']] = {'start': portal_start, 'end': None, 'duration': None}
        main_execution_logger.info(f"🚀 Portal '{portal['name']}' - Started at {portal_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            success = await portal["function"](playwright)
            portal_end = datetime.now()
            portal_duration = portal_end - portal_start
            portal_timings[portal['name']]['end'] = portal_end
            portal_timings[portal['name']]['duration'] = portal_duration
            
            if success:
                print(f"\n✅ {portal['name']} extraction completed!")
                main_execution_logger.info(
                    f"✅ Portal '{portal['name']}' - Completed at {portal_end.strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"Duration: {portal_duration.total_seconds():.2f}s ({int(portal_duration.total_seconds() // 60)}m {int(portal_duration.total_seconds() % 60)}s)"
                )
            else:
                print(f"\n❌ {portal['name']} extraction failed!")
                main_execution_logger.error(
                    f"❌ Portal '{portal['name']}' - Failed at {portal_end.strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"Duration: {portal_duration.total_seconds():.2f}s"
                )
        except Exception as e:
            portal_end = datetime.now()
            portal_duration = portal_end - portal_start
            portal_timings[portal['name']]['end'] = portal_end
            portal_timings[portal['name']]['duration'] = portal_duration
            
            print(f"\n❌ Error during {portal['name']} extraction: {e}")
            main_execution_logger.error(
                f"❌ Portal '{portal['name']}' - Error at {portal_end.strftime('%Y-%m-%d %H:%M:%S')}: {e} | "
                f"Duration: {portal_duration.total_seconds():.2f}s"
            )
            import traceback
            traceback.print_exc()
    
    # Calculate overall duration
    overall_end_time = datetime.now()
    overall_duration = overall_end_time - overall_start_time
    
    # Log summary
    print("\n" + "=" * 70)
    print("✅ API EXTRACTION COMPLETE")
    print("=" * 70)
    
    main_execution_logger.info(f"\n{'='*70}")
    main_execution_logger.info(f"📊 API EXTRACTION SUMMARY")
    main_execution_logger.info(f"{'='*70}")
    main_execution_logger.info(f"Overall End Time: {overall_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_execution_logger.info(f"Total Duration: {overall_duration.total_seconds():.2f}s ({int(overall_duration.total_seconds() // 60)}m {int(overall_duration.total_seconds() % 60)}s)")
    main_execution_logger.info(f"\n📋 Portal-wise Timing:")
    
    for portal_name, timing in portal_timings.items():
        if timing['duration']:
            main_execution_logger.info(
                f"  • {portal_name}: {timing['duration'].total_seconds():.2f}s "
                f"({int(timing['duration'].total_seconds() // 60)}m {int(timing['duration'].total_seconds() % 60)}s) | "
                f"{timing['start'].strftime('%H:%M:%S')} → {timing['end'].strftime('%H:%M:%S')}"
            )
    main_execution_logger.info(f"{'='*70}\n")

    
if __name__ == "__main__":
    async def main():
        # Clear all log files before starting new run
        print("\n" + "=" * 70)
        print("🧹 CLEARING LOG FILES")
        print("=" * 70)
        clear_all_logs()
        
        # Ask for extraction mode
        extraction_mode = get_extraction_mode()
        
        # Interactive company selection
        selected_companies = get_company_selection()
        
        if not selected_companies:
            print("\n❌ No companies selected. Exiting.")
            return

        async with async_playwright() as playwright:
            
            # =====================================================
            # API EXTRACTION MODE
            # =====================================================
            if extraction_mode == 'api':
                print("\n" + "=" * 70)
                print("🔌 API EXTRACTION MODE")
                print("=" * 70)
                await run_api_extraction_mode(playwright, selected_companies)
                return
            
            # =====================================================
            # STANDARD EXTRACTION MODE
            # =====================================================
            print("\n" + "=" * 70)
            print("📊 STANDARD EXTRACTION MODE")
            print("=" * 70)

            # Filter portals based on selection
            filtered_portals = filter_portal_list(PORTAL_GROUPS["main_portals"], selected_companies)
            print(f"\n🎯 Processing {len(selected_companies)} selected companies: {', '.join(selected_companies)}")
            print(f"   → Mapped to {len(filtered_portals)} portal functions: {', '.join([p['name'] for p in filtered_portals])}")

            USE_PARALLEL_EXECUTION = True

            while True:
                await clear_files()

                processed_req_id = process_next_pending_request()

                if not processed_req_id:
                    for attempt in range(0, MAX_RETRIES): # Start from 1 as we already had attempt 0
                        print(f"No pending requests found. Retrying in 20 seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                        await asyncio.sleep(20)
                        
                        processed_req_id = process_next_pending_request()
                        if processed_req_id:
                            break  # Success, a request was found and processed
                
                # Set the current request ID for logging context
                if processed_req_id:
                    set_current_request_id(processed_req_id)
                    # Log request start in Issues.log for tracking
                    logger.info(f"🚀 Starting processing for Request {processed_req_id}")
                    issues_logger.warning(f"🚀 Starting processing for Request {processed_req_id}")
                
                set_extracted_data_file()
                await run_census_mapping()

                if not processed_req_id:
                    print(f"No pending requests found after {MAX_RETRIES} attempts. Exiting extraction process.")
                    break

                if USE_PARALLEL_EXECUTION:
                    print(f"Starting portals with parallel execution (max concurrency: {MAX_PARALLEL_PORTALS})...")
                    
                    # Record request start time
                    request_start_time = datetime.now()
                    main_execution_logger.info(f"\n{'='*70}")
                    main_execution_logger.info(f"🚀 REQUEST {processed_req_id} PROCESSING STARTED")
                    main_execution_logger.info(f"Start Time: {request_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    main_execution_logger.info(f"Portals to process: {', '.join([p['name'] for p in filtered_portals])}")
                    main_execution_logger.info(f"{'='*70}")
                    
                    portal_results, portal_timings = await run_portals_with_concurrency_limit(
                        filtered_portals, playwright, 'default'
                    )
                    
                    # Record request end time
                    request_end_time = datetime.now()
                    request_duration = request_end_time - request_start_time
                    
                    failed_portals = [name for name, success in portal_results.items() if not success]
                    successful_portals = [name for name, success in portal_results.items() if success]
                    print(f"Successfully logged in portals: {', '.join(successful_portals) if successful_portals else 'None'}")
                    print(f"Failed portals: {', '.join(failed_portals) if failed_portals else 'None'}")
                    
                    # Log request summary
                    main_execution_logger.info(f"\n{'='*70}")
                    main_execution_logger.info(f"📊 REQUEST {processed_req_id} PROCESSING SUMMARY")
                    main_execution_logger.info(f"{'='*70}")
                    main_execution_logger.info(f"End Time: {request_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    main_execution_logger.info(f"Total Duration: {request_duration.total_seconds():.2f}s ({int(request_duration.total_seconds() // 60)}m {int(request_duration.total_seconds() % 60)}s)")
                    main_execution_logger.info(f"\n📋 Portal-wise Timing:")
                    
                    for portal_name, timing in portal_timings.items():
                        if timing['duration']:
                            status_icon = "✅" if portal_results.get(portal_name) else "❌"
                            main_execution_logger.info(
                                f"  {status_icon} {portal_name}: {timing['duration'].total_seconds():.2f}s "
                                f"({int(timing['duration'].total_seconds() // 60)}m {int(timing['duration'].total_seconds() % 60)}s) | "
                                f"{timing['start'].strftime('%H:%M:%S')} → {timing['end'].strftime('%H:%M:%S')}"
                            )
                    
                    main_execution_logger.info(f"\n✅ Successful: {len(successful_portals)}/{len(filtered_portals)} portals")
                    if successful_portals:
                        main_execution_logger.info(f"   {', '.join(successful_portals)}")
                    if failed_portals:
                        main_execution_logger.info(f"❌ Failed: {', '.join(failed_portals)}")
                    main_execution_logger.info(f"{'='*70}\n")
                
                # --- CORRECTED FINAL STATUS UPDATE ---
                print(f"\nUpdating status to 'Completed' for Req_Id {processed_req_id}...")
                final_update_status(processed_req_id, "Completed")
                
                # Log completion status in Issues.log for tracking
                logger.info(f"✅ Request {processed_req_id} processing completed successfully")
                issues_logger.warning(f"✅ Request {processed_req_id} processing completed successfully")

                print(f"\n--- Cycle for Req_Id {processed_req_id} finished. Checking for the next request... ---")

        # --- NEW: Run value comparison after all pending requests are completed ---
        print(f"\n📊 All portal extractions completed. Starting value comparison process...")
        comparison_success = await run_value_comparison()
        
        if comparison_success:
            print("✅ Value comparison process completed successfully")
        else:
            print("⚠️ Value comparison process encountered issues, but continuing...")


    asyncio.run(main())

