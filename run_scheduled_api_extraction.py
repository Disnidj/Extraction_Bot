"""
Automated API Extraction Runner
Runs all API portals without any user interaction.
Designed for scheduled/automated execution (e.g. Windows Task Scheduler).

For manual/development use, run main.py instead.
"""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

from main import run_api_extraction_mode, API_PORTAL_GROUPS
from src.utils.logger import clear_all_logs, main_execution_logger
from src.services.company_selector_updated import FUNCTION_TO_COMPANY_MAPPING

# All API portals to run - derived from main.py's API_PORTAL_GROUPS
# Converted to proper company display names for consistent logging
ALL_API_PORTALS = [
    FUNCTION_TO_COMPANY_MAPPING.get(portal["name"], portal["name"])
    for portal in API_PORTAL_GROUPS["api_portals"]
]


async def main():
    run_start = datetime.now()

    print("\n" + "=" * 70)
    print("   AUTOMATED API EXTRACTION - CLEARING LOGS")
    print("=" * 70)
    clear_all_logs()

    print("\n" + "=" * 70)
    print("   AUTOMATED API EXTRACTION - SCHEDULED RUN")
    print("=" * 70)
    print(f"\n  Start Time : {run_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Portals    : {', '.join(ALL_API_PORTALS)}")
    print("=" * 70)

    main_execution_logger.info("=" * 70)
    main_execution_logger.info("AUTOMATED SCHEDULED API EXTRACTION STARTED")
    main_execution_logger.info(f"Start Time : {run_start.strftime('%Y-%m-%d %H:%M:%S')}")
    main_execution_logger.info(f"Portals    : {', '.join(ALL_API_PORTALS)}")
    main_execution_logger.info("=" * 70)

    async with async_playwright() as playwright:
        await run_api_extraction_mode(
            playwright,
            selected_companies=ALL_API_PORTALS,
            skip_confirmation=True   # <-- bypasses the interactive prompt
        )

    run_end = datetime.now()
    duration = run_end - run_start
    total_mins = int(duration.total_seconds() // 60)
    total_secs = int(duration.total_seconds() % 60)

    print("\n" + "=" * 70)
    print("   AUTOMATED API EXTRACTION - COMPLETED")
    print(f"   Total Duration: {total_mins}m {total_secs}s")
    print("=" * 70)

    main_execution_logger.info("=" * 70)
    main_execution_logger.info("AUTOMATED SCHEDULED API EXTRACTION COMPLETED")
    main_execution_logger.info(f"End Time       : {run_end.strftime('%Y-%m-%d %H:%M:%S')}")
    main_execution_logger.info(f"Total Duration : {total_mins}m {total_secs}s")
    main_execution_logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
