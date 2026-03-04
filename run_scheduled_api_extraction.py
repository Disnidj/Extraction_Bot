"""
Automated Multi-Broker API Extraction Runner
Runs all API portals for all active brokers without any user interaction.
Designed for scheduled/automated execution (e.g. Windows Task Scheduler).

For manual/development use, run main.py instead.

Usage:
    python run_scheduled_api_extraction.py
    
This will:
    - Run extraction for ALL active brokers (defined in src/config/broker_config.py)
    - Extract from ALL available API portals (per broker's database mapping)
    - Upload data to each broker's staging table automatically
    - No user prompts (fully automated)
"""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

from main import run_api_extraction_mode, API_PORTAL_GROUPS
from src.utils.logger import clear_all_logs, main_execution_logger
from src.config.broker_config import get_active_broker_ids, get_broker_name
from src.services.broker_service.portal_mapper import PortalMapper


async def main():
    run_start = datetime.now()

    print("\n" + "=" * 70)
    print("   AUTOMATED MULTI-BROKER API EXTRACTION - CLEARING LOGS")
    print("=" * 70)
    clear_all_logs()

    # Get all active brokers from configuration
    active_brokers = get_active_broker_ids()
    
    if not active_brokers:
        print("\n❌ ERROR: No active brokers found in configuration!")
        print("   Check src/config/broker_config.py")
        main_execution_logger.error("No active brokers found in configuration")
        return

    # Fetch portal analysis from database
    print("\n🔍 Fetching portal mapping from database...")
    try:
        portal_mapper = PortalMapper()
        portal_analysis = portal_mapper.analyze_portal_distribution(active_brokers)
        
        all_portals = sorted(set(portal_analysis['shared'].keys()) | set(portal_analysis['unique'].keys()))
        
        # Filter to portals with API implementation
        api_portal_names = {p["name"] for p in API_PORTAL_GROUPS["api_portals"]}
        available_portals = [p for p in all_portals if p in api_portal_names]
        unavailable_portals = [p for p in all_portals if p not in api_portal_names]
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to fetch portal mappings from database!")
        print(f"   Error: {e}")
        main_execution_logger.error(f"Failed to fetch portal mappings: {e}")
        return

    print("\n" + "=" * 70)
    print("   AUTOMATED MULTI-BROKER API EXTRACTION - SCHEDULED RUN")
    print("=" * 70)
    print(f"\n  Start Time : {run_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Brokers    : {len(active_brokers)} active")
    for bid in active_brokers:
        print(f"               • Broker {bid} - {get_broker_name(bid)}")
    
    print(f"\n  Portals to Extract: {len(available_portals)} (with API implementation)")
    for portal in available_portals:
        # Check if shared or unique
        if portal in portal_analysis['shared']:
            broker_list = portal_analysis['shared'][portal]
            print(f"               • {portal} (shared: {len(broker_list)} brokers)")
        else:
            broker_id = portal_analysis['unique'][portal]
            print(f"               • {portal} (Broker {broker_id} only)")
    
    if unavailable_portals:
        print(f"\n  ⚠️  Portals to Skip: {len(unavailable_portals)} (no API implementation)")
        for portal in unavailable_portals:
            if portal in portal_analysis['shared']:
                broker_list = portal_analysis['shared'][portal]
                print(f"               • {portal} (shared: {len(broker_list)} brokers)")
            else:
                broker_id = portal_analysis['unique'][portal]
                print(f"               • {portal} (Broker {broker_id} only)")
    
    print(f"\n  Mode       : Fully automated (no prompts)")
    print("=" * 70)

    main_execution_logger.info("=" * 70)
    main_execution_logger.info("AUTOMATED MULTI-BROKER API EXTRACTION STARTED")
    main_execution_logger.info(f"Start Time : {run_start.strftime('%Y-%m-%d %H:%M:%S')}")
    main_execution_logger.info(f"Active Brokers ({len(active_brokers)}): {', '.join([f'Broker {bid} ({get_broker_name(bid)})' for bid in active_brokers])}")
    main_execution_logger.info(f"Portals to Extract ({len(available_portals)}): {', '.join(available_portals)}")
    if unavailable_portals:
        main_execution_logger.info(f"Portals to Skip ({len(unavailable_portals)}): {', '.join(unavailable_portals)}")
    main_execution_logger.info("Mode: Scheduled - Auto-confirm all prompts")
    main_execution_logger.info("=" * 70)

    async with async_playwright() as playwright:
        await run_api_extraction_mode(
            playwright,
            selected_companies=None,      # Not used in multi-broker mode
            skip_confirmation=True,       # Bypass all interactive prompts
            broker_ids=active_brokers     # Run for all active brokers
        )

    run_end = datetime.now()
    duration = run_end - run_start
    total_mins = int(duration.total_seconds() // 60)
    total_secs = int(duration.total_seconds() % 60)

    print("\n" + "=" * 70)
    print("   AUTOMATED MULTI-BROKER API EXTRACTION - COMPLETED")
    print(f"   Brokers Processed: {len(active_brokers)}")
    print(f"   Portals Extracted: {len(available_portals)}")
    if unavailable_portals:
        print(f"   Portals Skipped: {len(unavailable_portals)} (no API implementation)")
    print(f"   Total Duration: {total_mins}m {total_secs}s")
    print("=" * 70)

    main_execution_logger.info("=" * 70)
    main_execution_logger.info("AUTOMATED MULTI-BROKER API EXTRACTION COMPLETED")
    main_execution_logger.info(f"End Time       : {run_end.strftime('%Y-%m-%d %H:%M:%S')}")
    main_execution_logger.info(f"Brokers Processed: {len(active_brokers)}")
    main_execution_logger.info(f"Portals Extracted: {len(available_portals)}")
    if unavailable_portals:
        main_execution_logger.info(f"Portals Skipped: {len(unavailable_portals)} (no API implementation)")
    main_execution_logger.info(f"Total Duration : {total_mins}m {total_secs}s")
    main_execution_logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
