import asyncio
import os
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
from src.pages.sukoon.sukoonmain_api import run_sukoon_api_extraction
from src.pages.maxHealth.maxHealth_main_api import run_maxhealth_api_extraction
from src.pages.orient_aura.orient_aura_main_api import run_orient_aura_api_extraction
from src.pages.nlgi_aura.nlgi_aura_main_api import run_nlgi_aura_api_extraction
from src.pages.qic_healthx.qic_healthx_main_api import run_qic_healthx_api_extraction
from src.services.db_service.api_data.upload_extracted import upload_to_database
from src.utils.logger import set_current_request_id, issues_logger, logger, main_execution_logger, clear_all_logs
from src.services.extraction_report.report_generator import generate_extraction_report
from src.utils.logger import set_current_request_id, issues_logger
from src.utils.logger import set_current_request_id, logger
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
        # {"function": run_takaful_api_extraction, "name": "Takaful"},
        {"function": run_qatar_api_extraction, "name": "QATAR"},
        {"function": run_maxhealth_api_extraction, "name": "MaxHealth"},
        {"function": run_sukoon_api_extraction, "name": "Sukoon"},
        {"function": run_orient_aura_api_extraction, "name": "Orient Aura"},
        {"function": run_nlgi_aura_api_extraction, "name": "NLGI Aura"},
        # {"function": run_qic_healthx_api_extraction, "name": "QIC HealthX Exclusive"},
    ]
}

# === RETRY CONFIGURATION ===
# Automatically retry failed portals before generating report
MAX_RETRY_ATTEMPTS = 1  # Number of times to retry failed portals (0 = no retry)
RETRY_DELAY_SECONDS = 5  # Delay between retry attempts

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


async def run_api_extraction_mode(playwright, selected_companies, skip_confirmation=False):
    """
    Run API-based extraction mode with timing tracking.
    
    Args:
        playwright: Playwright instance
        selected_companies: List of selected company names
        skip_confirmation: If True, bypass the interactive confirmation prompt (used for scheduled runs)
    """
    # Filter to portals with API extraction available
    api_portals = API_PORTAL_GROUPS["api_portals"]
    api_portal_names = [p["name"] for p in api_portals]
    
    # Map selected companies to portal names (preserving order)
    from src.services.company_selector_updated import COMPANY_TO_FUNCTION_MAPPING
    selected_portal_names = [COMPANY_TO_FUNCTION_MAPPING.get(c, c) for c in selected_companies]
    
    # Create lookup for API portals
    api_portal_lookup = {p["name"]: p for p in api_portals}
    
    # Find matching API portals IN USER'S SELECTION ORDER
    matching_portals = []
    unavailable = []
    for portal_name in selected_portal_names:
        if portal_name in api_portal_lookup:
            matching_portals.append(api_portal_lookup[portal_name])
        else:
            unavailable.append(portal_name)
    
    if unavailable:
        print(f"\n⚠️  No API extraction implemented yet for: {', '.join(unavailable)}")
        print("   These will be skipped.")
    
    if not matching_portals:
        print("\n❌ None of the selected portals have API extraction implemented.")
        print(f"   Available API portals: {', '.join(api_portal_names)}")
        return
    
    # Build display name map: portal name → proper company name for logs/prints
    from src.services.company_selector_updated import FUNCTION_TO_COMPANY_MAPPING
    display_name_map = {p['name']: FUNCTION_TO_COMPANY_MAPPING.get(p['name'], p['name']) for p in matching_portals}
    
    print(f"\n✅ Will extract from:")
    for p in matching_portals:
        print(f"   • {display_name_map[p['name']]}")
    
    # Show retry configuration
    if MAX_RETRY_ATTEMPTS > 0:
        print(f"\n🔄 Auto-retry enabled: Failed portals will be retried {MAX_RETRY_ATTEMPTS} time(s)")
        print(f"   Retry delay: {RETRY_DELAY_SECONDS} seconds")
    else:
        print(f"\n⚠️  Auto-retry disabled")
    
    # Confirm
    if skip_confirmation:
        print("\n▶️  Scheduled run - skipping confirmation prompt, starting automatically...")
    else:
        confirm = input("\n▶️  Press Enter to start API extraction (or 'q' to quit): ").strip().lower()
        if confirm == 'q':
            print("👋 Cancelled.")
            return
    
    # Record overall start time
    overall_start_time = datetime.now()
    
    # Create run-specific output folder with timestamp
    run_timestamp = overall_start_time.strftime("%Y%m%d_%H%M%S")
    run_output_dir = os.path.join("extracted_data", run_timestamp)
    os.makedirs(run_output_dir, exist_ok=True)
    print(f"\n📁 Output folder: {run_output_dir}")
    
    main_execution_logger.info(f"\n{'='*70}")
    main_execution_logger.info(f"🚀 API EXTRACTION FLOW STARTED")
    main_execution_logger.info(f"Start Time: {overall_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_execution_logger.info(f"Output Folder: {run_output_dir}")
    main_execution_logger.info(f"Portals to process: {', '.join([display_name_map[p['name']] for p in matching_portals])}")
    main_execution_logger.info(f"Retry Configuration: {'Enabled' if MAX_RETRY_ATTEMPTS > 0 else 'Disabled'} (Max attempts: {MAX_RETRY_ATTEMPTS + 1}, Delay: {RETRY_DELAY_SECONDS}s)")
    main_execution_logger.info(f"{'='*70}")
    
    portal_timings = {}
    portal_results = {}  # Track success/failure for PDF report
    
    # Run extraction for each portal (FIRST ATTEMPT)
    for portal in matching_portals:
        portal_display = display_name_map.get(portal['name'], portal['name'])
        print(f"\n{'=' * 60}")
        print(f"🔄 Starting API extraction: {portal_display}")
        print(f"{'=' * 60}")
        
        portal_start = datetime.now()
        portal_timings[portal['name']] = {
            'start': portal_start, 
            'end': None, 
            'duration': None,
            'first_attempt': {'start': portal_start, 'end': None, 'duration': None},
            'retry_attempt': None
        }
        portal_results[portal['name']] = {'success': False, 'error': None, 'attempts': 1, 'retry_success': False}
        main_execution_logger.info(f"🚀 Portal '{portal_display}' - ATTEMPT 1 Started at {portal_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            result = await portal["function"](playwright, output_dir=run_output_dir)
            portal_end = datetime.now()
            portal_duration = portal_end - portal_start
            portal_timings[portal['name']]['end'] = portal_end
            portal_timings[portal['name']]['duration'] = portal_duration
            
            # Handle different return formats:
            # - New format: {"success": bool, "results": ..., "errors": [...]}
            # - Old format: truthy/falsy value or None
            if isinstance(result, dict) and "success" in result:
                # New format with explicit success flag and errors
                success = result.get("success", False)
                errors = result.get("errors", [])
                portal_results[portal['name']]['success'] = success
                if errors:
                    portal_results[portal['name']]['error'] = "; ".join(errors)
                elif not success:
                    # No specific errors but failed - try to get a generic message
                    portal_results[portal['name']]['error'] = "API extraction failed (no specific error)"
            else:
                # Old format - truthy value means success
                success = bool(result)
                portal_results[portal['name']]['success'] = success
                if not success:
                    # Check if the result is None, False, or other falsy value
                    if result is None:
                        portal_results[portal['name']]['error'] = "Login failed or authentication error"
                    elif result is False:
                        portal_results[portal['name']]['error'] = "Extraction process returned failure"
                    else:
                        portal_results[portal['name']]['error'] = "Extraction returned False"
            
            # Update first attempt timing
            portal_timings[portal['name']]['first_attempt']['end'] = portal_end
            portal_timings[portal['name']]['first_attempt']['duration'] = portal_duration
            
            if success:
                print(f"\n✅ {portal_display} extraction completed!")
                main_execution_logger.info(
                    f"✅ Portal '{portal_display}' - ATTEMPT 1 Completed at {portal_end.strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"Duration: {portal_duration.total_seconds():.2f}s ({int(portal_duration.total_seconds() // 60)}m {int(portal_duration.total_seconds() % 60)}s)"
                )
            else:
                error_msg = portal_results[portal['name']].get('error') or "Unknown extraction error"
                portal_results[portal['name']]['error'] = error_msg
                print(f"\n❌ {portal_display} extraction failed on ATTEMPT 1!")
                print(f"   Error: {error_msg}")
                main_execution_logger.error(
                    f"❌ Portal '{portal_display}' - ATTEMPT 1 Failed at {portal_end.strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"Duration: {portal_duration.total_seconds():.2f}s | Error: {error_msg}"
                )
        except Exception as e:
            portal_end = datetime.now()
            portal_duration = portal_end - portal_start
            portal_timings[portal['name']]['end'] = portal_end
            portal_timings[portal['name']]['duration'] = portal_duration
            
            # Update first attempt timing
            portal_timings[portal['name']]['first_attempt']['end'] = portal_end
            portal_timings[portal['name']]['first_attempt']['duration'] = portal_duration
            
            portal_results[portal['name']]['error'] = str(e)
            
            print(f"\n❌ Error during {portal_display} ATTEMPT 1: {e}")
            main_execution_logger.error(
                f"❌ Portal '{portal_display}' - ATTEMPT 1 Error at {portal_end.strftime('%Y-%m-%d %H:%M:%S')}: {e} | "
                f"Duration: {portal_duration.total_seconds():.2f}s"
            )
            # Log full traceback for debugging
            import traceback
            error_traceback = traceback.format_exc()
            main_execution_logger.error(f"   Traceback:\n{error_traceback}")
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
    main_execution_logger.info(f"\n📋 Portal-wise Timing (Final Results):")
    
    for portal_name, timing in portal_timings.items():
        if timing['duration']:
            result = portal_results.get(portal_name, {})
            attempts = result.get('attempts', 1)
            
            # Show overall timing
            main_execution_logger.info(
                f"  • {portal_name}: {timing['duration'].total_seconds():.2f}s "
                f"({int(timing['duration'].total_seconds() // 60)}m {int(timing['duration'].total_seconds() % 60)}s) | "
                f"{timing['start'].strftime('%H:%M:%S')} → {timing['end'].strftime('%H:%M:%S')}"
            )
            
            # If retried, show both attempts
            if attempts > 1 and timing.get('retry_attempt'):
                first_dur = timing['first_attempt']['duration'].total_seconds()
                retry_dur = timing['retry_attempt']['duration'].total_seconds()
                main_execution_logger.info(
                    f"     └─ Attempt 1: {first_dur:.2f}s | "
                    f"Attempt 2: {retry_dur:.2f}s"
                )
    
    # Log portal extraction errors if any
    failed_portals = {k: v for k, v in portal_results.items() if not v.get('success') or v.get('error')}
    if failed_portals:
        main_execution_logger.info(f"\n⚠️ PORTAL EXTRACTION ERRORS:")
        for portal_name, result in failed_portals.items():
            error_msg = result.get('error', 'Unknown error')
            attempts = result.get('attempts', 1)
            if attempts > 1:
                main_execution_logger.error(f"  ❌ {portal_name} (failed both attempts): {error_msg}")
            else:
                main_execution_logger.error(f"  ❌ {portal_name}: {error_msg}")
    
    main_execution_logger.info(f"{'='*70}\n")
    
    # ============================================================
    # AUTOMATIC RETRY FOR FAILED PORTALS
    # ============================================================
    if MAX_RETRY_ATTEMPTS > 0 and failed_portals:
        failed_portal_list = [
            portal for portal in matching_portals 
            if not portal_results.get(portal['name'], {}).get('success', False)
        ]
        
        if failed_portal_list:
            print(f"\n{'='*70}")
            print(f"🔄 RETRY ATTEMPT FOR FAILED PORTALS")
            print(f"{'='*70}")
            print(f"⚠️  {len(failed_portal_list)} portal(s) failed on first attempt")
            print(f"🔄 Will retry: {', '.join([p['name'] for p in failed_portal_list])}")
            print(f"⏳ Waiting {RETRY_DELAY_SECONDS} seconds before retry...")
            print(f"{'='*70}")
            
            main_execution_logger.info(f"\n{'='*70}")
            main_execution_logger.info(f"🔄 RETRY ATTEMPT FOR FAILED PORTALS")
            main_execution_logger.info(f"{'='*70}")
            main_execution_logger.info(f"Failed portals: {', '.join([display_name_map.get(p['name'], p['name']) for p in failed_portal_list])}")
            main_execution_logger.info(f"Retry delay: {RETRY_DELAY_SECONDS} seconds")
            
            # Wait before retry
            import asyncio
            await asyncio.sleep(RETRY_DELAY_SECONDS)
            
            # Retry each failed portal
            for portal in failed_portal_list:
                portal_display = display_name_map.get(portal['name'], portal['name'])
                print(f"\n{'='*60}")
                print(f"🔄 RETRY: {portal_display} (Attempt 2/{MAX_RETRY_ATTEMPTS + 1})")
                print(f"{'='*60}")
                
                retry_start = datetime.now()
                portal_timings[portal['name']]['retry_attempt'] = {
                    'start': retry_start,
                    'end': None,
                    'duration': None
                }
                main_execution_logger.info(f"\n🔄 Portal '{portal_display}' - ATTEMPT 2 (Retry) Started at {retry_start.strftime('%Y-%m-%d %H:%M:%S')}")
                
                try:
                    result = await portal["function"](playwright, output_dir=run_output_dir)
                    retry_end = datetime.now()
                    retry_duration = retry_end - retry_start
                    
                    # Handle different return formats
                    if isinstance(result, dict) and "success" in result:
                        success = result.get("success", False)
                        errors = result.get("errors", [])
                        if errors:
                            error_msg = "; ".join(errors)
                        elif not success:
                            error_msg = "API extraction failed (no specific error)"
                        else:
                            error_msg = None
                    else:
                        success = bool(result)
                        if not success:
                            if result is None:
                                error_msg = "Login failed or authentication error"
                            elif result is False:
                                error_msg = "Extraction process returned failure"
                            else:
                                error_msg = "Extraction returned False"
                        else:
                            error_msg = None
                    
                    # Update retry timing
                    portal_timings[portal['name']]['retry_attempt']['end'] = retry_end
                    portal_timings[portal['name']]['retry_attempt']['duration'] = retry_duration
                    
                    # Update results with retry information
                    portal_results[portal['name']]['attempts'] = 2
                    portal_results[portal['name']]['retry_success'] = success
                    
                    if success:
                        # Override the original failure with retry success
                        portal_results[portal['name']]['success'] = True
                        portal_results[portal['name']]['error'] = None
                        
                        # Update overall timing to reflect retry timing
                        portal_timings[portal['name']]['end'] = retry_end
                        portal_timings[portal['name']]['duration'] = retry_duration
                        
                        print(f"\n✅ {portal_display} ATTEMPT 2 SUCCEEDED!")
                        main_execution_logger.info(
                            f"✅ Portal '{portal_display}' - ATTEMPT 2 (Retry) SUCCEEDED at {retry_end.strftime('%Y-%m-%d %H:%M:%S')} | "
                            f"Duration: {retry_duration.total_seconds():.2f}s ({int(retry_duration.total_seconds() // 60)}m {int(retry_duration.total_seconds() % 60)}s) | "
                            f"Total attempts: 2"
                        )
                    else:
                        # Still failed after retry
                        portal_results[portal['name']]['error'] = error_msg or portal_results[portal['name']].get('error', 'Unknown error')
                        
                        print(f"\n❌ {portal_display} ATTEMPT 2 FAILED - Both attempts failed")
                        print(f"   Error: {portal_results[portal['name']]['error']}")
                        main_execution_logger.error(
                            f"❌ Portal '{portal_display}' - ATTEMPT 2 (Retry) FAILED at {retry_end.strftime('%Y-%m-%d %H:%M:%S')} | "
                            f"Duration: {retry_duration.total_seconds():.2f}s | Error: {error_msg} | "
                            f"Total attempts: 2 (both failed)"
                        )
                        
                except Exception as e:
                    retry_end = datetime.now()
                    retry_duration = retry_end - retry_start
                    
                    # Update retry timing
                    portal_timings[portal['name']]['retry_attempt']['end'] = retry_end
                    portal_timings[portal['name']]['retry_attempt']['duration'] = retry_duration
                    
                    portal_results[portal['name']]['attempts'] = 2
                    portal_results[portal['name']]['retry_success'] = False
                    portal_results[portal['name']]['error'] = str(e)
                    
                    print(f"\n❌ Error during {portal_display} ATTEMPT 2 (Retry): {e}")
                    main_execution_logger.error(
                        f"❌ Portal '{portal_display}' - ATTEMPT 2 (Retry) Error at {retry_end.strftime('%Y-%m-%d %H:%M:%S')}: {e} | "
                        f"Duration: {retry_duration.total_seconds():.2f}s | Total attempts: 2"
                    )
                    import traceback
                    error_traceback = traceback.format_exc()
                    main_execution_logger.error(f"   Traceback:\n{error_traceback}")
            
            # Log retry summary
            print(f"\n{'='*70}")
            print(f"🔄 RETRY SUMMARY")
            print(f"{'='*70}")
            
            retry_success_count = sum(
                1 for p in failed_portal_list 
                if portal_results.get(p['name'], {}).get('retry_success', False)
            )
            retry_failed_count = len(failed_portal_list) - retry_success_count
            
            print(f"✅ Succeeded after retry: {retry_success_count}")
            print(f"❌ Still failed: {retry_failed_count}")
            print(f"{'='*70}\n")
            
            main_execution_logger.info(f"\n{'='*70}")
            main_execution_logger.info(f"🔄 RETRY SUMMARY")
            main_execution_logger.info(f"{'='*70}")
            main_execution_logger.info(f"Portals retried: {len(failed_portal_list)}")
            main_execution_logger.info(f"Succeeded after retry (Attempt 2): {retry_success_count}")
            main_execution_logger.info(f"Still failed after retry: {retry_failed_count}")
            
            # List which portals succeeded on retry
            if retry_success_count > 0:
                retry_success_portals = [
                    display_name_map.get(p['name'], p['name']) for p in failed_portal_list 
                    if portal_results.get(p['name'], {}).get('retry_success', False)
                ]
                main_execution_logger.info(f"\n✅ Succeeded on Attempt 2: {', '.join(retry_success_portals)}")
            
            # List which portals still failed
            if retry_failed_count > 0:
                still_failed_portals = [
                    display_name_map.get(p['name'], p['name']) for p in failed_portal_list 
                    if not portal_results.get(p['name'], {}).get('retry_success', False)
                ]
                main_execution_logger.info(f"❌ Failed on both attempts: {', '.join(still_failed_portals)}")
            
            main_execution_logger.info(f"{'='*70}\n")

    # Upload extracted data to database
    print("\n" + "=" * 70)
    print("📤 DATABASE UPLOAD")
    print("=" * 70)
    
    db_upload_start = datetime.now()
    success, rows_changed, upload_msg, deletion_details, mapping_details, change_report = upload_to_database(run_output_dir)
    db_upload_end = datetime.now()
    db_upload_duration = db_upload_end - db_upload_start
    
    # Calculate actual staging row count (total rows uploaded to staging)
    staging_row_count = 0
    if change_report:
        staging_row_count = (
            len(change_report.new_records) + 
            len(change_report.modified_records) + 
            len(change_report.deleted_records) + 
            change_report.unchanged_count
        )
    
    if success:
        print(f"✅ Database upload complete: {rows_changed} changes applied")
        
        main_execution_logger.info(f"\n{'='*70}")
        main_execution_logger.info(f"📤 DATABASE UPLOAD SUMMARY")
        main_execution_logger.info(f"{'='*70}")
        main_execution_logger.info(f"   Status: SUCCESS")
        main_execution_logger.info(f"   Total changes: {rows_changed}")
        main_execution_logger.info(f"   Duration: {db_upload_duration.total_seconds():.2f}s ({int(db_upload_duration.total_seconds() // 60)}m {int(db_upload_duration.total_seconds() % 60)}s)")
        main_execution_logger.info(f"   Start: {db_upload_start.strftime('%H:%M:%S')} → End: {db_upload_end.strftime('%H:%M:%S')}")
        
        # Log change report details if available
        if change_report:
            main_execution_logger.info(f"\n   📊 CHANGE REPORT (Run ID: {change_report.run_id}):")
            main_execution_logger.info(f"      • New records: {len(change_report.new_records)}")
            main_execution_logger.info(f"      • Modified records: {len(change_report.modified_records)}")
            main_execution_logger.info(f"      • Deleted records: {len(change_report.deleted_records)}")
            main_execution_logger.info(f"      • Unchanged records: {change_report.unchanged_count}")
            
            # Log full backup file if created
            if hasattr(change_report, 'full_backup_file') and change_report.full_backup_file:
                backup_filename = os.path.basename(change_report.full_backup_file)
                main_execution_logger.info(f"\n   💾 FULL TABLE BACKUP:")
                main_execution_logger.info(f"      • File: {backup_filename}")
                main_execution_logger.info(f"      • Location: {change_report.full_backup_file}")
                main_execution_logger.info(f"      • Purpose: Complete disaster recovery backup")
            
            # Log changes by portal
            changes_by_company = change_report.get_changes_by_company()
            if changes_by_company:
                main_execution_logger.info(f"\n   📋 CHANGES BY PORTAL:")
                for company, data in changes_by_company.items():
                    total = len(data['new']) + len(data['modified']) + len(data['deleted'])
                    main_execution_logger.info(f"      • {company}: {total} changes")
                    if data['new']:
                        main_execution_logger.info(f"         - New: {len(data['new'])}")
                    if data['modified']:
                        main_execution_logger.info(f"         - Modified: {len(data['modified'])}")
                    if data['deleted']:
                        main_execution_logger.info(f"         - Deleted: {len(data['deleted'])}")
                    # Log dropdown names
                    if deletion_details and company in deletion_details:
                        dropdown_names = deletion_details[company].get('dropdown_names', [])
                        if dropdown_names:
                            main_execution_logger.info(f"         - Dropdowns: {', '.join(dropdown_names)}")
        
        # Log mapping details per portal
        if mapping_details and mapping_details.get('applied_mappings'):
            main_execution_logger.info(f"\n   🔄 Dropdown Mappings Applied by Portal:")
            for company, mappings in mapping_details['applied_mappings'].items():
                if mappings:
                    main_execution_logger.info(f"      • {company} ({len(mappings)} mappings):")
                    for portal_name, db_name in sorted(mappings.items()):
                        main_execution_logger.info(f"         - {portal_name} → {db_name}")
        
        main_execution_logger.info(f"{'='*70}\n")
    else:
        print(f"❌ Database upload failed: {upload_msg}")
        main_execution_logger.error(f"\n{'='*70}")
        main_execution_logger.error(f"📤 DATABASE UPLOAD SUMMARY")
        main_execution_logger.error(f"{'='*70}")
        main_execution_logger.error(f"   Status: FAILED")
        main_execution_logger.error(f"   Error: {upload_msg}")
        main_execution_logger.error(f"   Duration: {db_upload_duration.total_seconds():.2f}s")
        main_execution_logger.error(f"{'='*70}\n")

    # ============================================================
    # FINAL SUMMARY: Complete Process Duration
    # ============================================================
    complete_process_end = datetime.now()
    total_process_duration = complete_process_end - overall_start_time
    total_seconds = total_process_duration.total_seconds()
    total_minutes = int(total_seconds // 60)
    total_remaining_seconds = int(total_seconds % 60)
    
    main_execution_logger.info(f"\n{'='*70}")
    main_execution_logger.info(f"🏁 COMPLETE PROCESS SUMMARY")
    main_execution_logger.info(f"{'='*70}")
    main_execution_logger.info(f"   Total Start Time: {overall_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_execution_logger.info(f"   Total End Time: {complete_process_end.strftime('%Y-%m-%d %H:%M:%S')}")
    main_execution_logger.info(f"   ")
    main_execution_logger.info(f"   API Extraction: {overall_duration.total_seconds():.2f}s")
    main_execution_logger.info(f"   Database Upload: {db_upload_duration.total_seconds():.2f}s")
    main_execution_logger.info(f"   {'─'*66}")
    main_execution_logger.info(f"   TOTAL DURATION: {total_seconds:.2f}s ({total_minutes}m {total_remaining_seconds}s)")
    main_execution_logger.info(f"{'='*70}\n")
    
    print(f"\n{'='*70}")
    print(f"🏁 COMPLETE PROCESS FINISHED")
    print(f"   Total Duration: {total_minutes}m {total_remaining_seconds}s")
    print(f"{'='*70}\n")

    # ============================================================
    # GENERATE PDF REPORT
    # ============================================================
    print("\n" + "=" * 70)
    print("📄 PDF REPORT GENERATION")
    print("=" * 70)
    
    try:
        pdf_path = generate_extraction_report(
            run_timestamp=run_timestamp,
            overall_start_time=overall_start_time,
            overall_end_time=overall_end_time,
            portal_timings=portal_timings,
            portal_results=portal_results,
            db_upload_success=success,
            db_rows_inserted=staging_row_count,  # Total rows uploaded to staging
            db_upload_duration=db_upload_duration.total_seconds(),
            db_upload_start=db_upload_start,
            db_upload_end=db_upload_end,
            total_duration=total_seconds,
            output_folder=run_output_dir,
            portals_processed=[p['name'] for p in matching_portals],
            deletion_details=deletion_details,
            mapping_details=mapping_details,
            change_report=change_report
        )
        print(f"✅ PDF Report generated: {pdf_path}")
        main_execution_logger.info(f"\n{'='*70}")
        main_execution_logger.info(f"📄 PDF REPORT GENERATED")
        main_execution_logger.info(f"{'='*70}")
        main_execution_logger.info(f"   Report Path: {pdf_path}")
        main_execution_logger.info(f"{'='*70}\n")
        
        # ============================================================
        # SEND EMAIL NOTIFICATION
        # ============================================================
        from src.utils.load_yaml import (
            EXTRACTION_NOTIFICATIONS_ENABLED,
            NOTIFICATION_RECIPIENTS_TO,
            NOTIFICATION_RECIPIENTS_CC,
            OUTLOOK_CLIENT_ID,
            OUTLOOK_TENANT_ID,
            OUTLOOK_TOKEN_CACHE_PATH
        )
        from src.services.email_notifications.extraction_notifier import send_extraction_success_notification
        
        if EXTRACTION_NOTIFICATIONS_ENABLED:
            print("\n" + "=" * 70)
            print("📧 EMAIL NOTIFICATION")
            print("=" * 70)
            
            try:
                # Set environment variables for the mailer
                os.environ['OUTLOOK_CLIENT_ID'] = OUTLOOK_CLIENT_ID
                os.environ['OUTLOOK_TENANT_ID'] = OUTLOOK_TENANT_ID
                os.environ['OUTLOOK_TOKEN_CACHE'] = OUTLOOK_TOKEN_CACHE_PATH
                
                email_sent = await send_extraction_success_notification(
                    run_timestamp=run_timestamp,
                    overall_start_time=overall_start_time,
                    overall_end_time=overall_end_time,
                    portal_results=portal_results,
                    portal_timings=portal_timings,
                    db_upload_success=success,
                    db_rows_inserted=staging_row_count,  # Total rows uploaded to staging
                    db_upload_duration=db_upload_duration.total_seconds(),
                    total_duration=total_seconds,
                    portals_processed=[p['name'] for p in matching_portals],
                    pdf_report_path=pdf_path,
                    recipients_to=NOTIFICATION_RECIPIENTS_TO,
                    recipients_cc=NOTIFICATION_RECIPIENTS_CC,
                    logger=main_execution_logger,
                    change_report=change_report,
                )
                
                if email_sent:
                    print(f"✅ Email notification sent successfully")
                    print(f"   TO: {', '.join(NOTIFICATION_RECIPIENTS_TO)}")
                    print(f"   CC: {', '.join(NOTIFICATION_RECIPIENTS_CC)}")
                    main_execution_logger.info(f"✅ Email notification sent successfully")
                else:
                    print(f"⚠️ Email notification failed")
                    main_execution_logger.warning(f"⚠️ Email notification failed")
                    
            except Exception as email_error:
                print(f"❌ Failed to send email notification: {email_error}")
                main_execution_logger.error(f"❌ Email notification error: {email_error}")
                import traceback
                main_execution_logger.error(f"   Traceback:\n{traceback.format_exc()}")
                # Don't raise - email failure shouldn't stop the process
        else:
            print("\n📧 Email notifications are disabled in config.yaml")
            main_execution_logger.info("📧 Email notifications are disabled")
            
    except Exception as e:
        print(f"❌ Failed to generate PDF report: {e}")
        main_execution_logger.error(f"❌ PDF Report generation failed: {e}")
        import traceback
        main_execution_logger.error(f"   Traceback:\n{traceback.format_exc()}")

    
if __name__ == "__main__":
    async def main():
        # Clear all log files before starting new run
        print("\n" + "=" * 70)
        print("🧹 CLEARING LOG FILES")
        print("=" * 70)
        clear_all_logs()
        
        # Ask for extraction mode
        extraction_mode = get_extraction_mode()
        
        # For API mode, derive available companies dynamically from active API_PORTAL_GROUPS
        # This means commenting a portal in API_PORTAL_GROUPS automatically hides it from the menu
        available_api_companies = None
        if extraction_mode == 'api':
            from src.services.company_selector_updated import FUNCTION_TO_COMPANY_MAPPING
            available_api_companies = [
                FUNCTION_TO_COMPANY_MAPPING.get(p["name"], p["name"])
                for p in API_PORTAL_GROUPS["api_portals"]
            ]
        
        # Interactive company selection (filtered by mode)
        selected_companies = get_company_selection(mode=extraction_mode, available_api_companies=available_api_companies)
        
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

