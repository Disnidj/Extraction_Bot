from patchright.async_api import Playwright
from src.pages.orient.orient_main import LoginPage
from src.utils.enums import Orient_Status
from src.services.db_service.update import update_last_check_datetime
from src.utils.load_yaml import ORIENT_QUOTATION_DIR,MAX_SLEEP
from src.services.referral_service.final_process import run_portals
from src.utils.logger import logger
import os
import time


async def go_to_iq_referrals_page(playwright: Playwright, iq_quotation_numbers):

    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context(accept_downloads=True)
    context.set_default_timeout(60000)
    page = await context.new_page()

    # Login to the Takaful portal
    login_page = LoginPage(page)
    await login_page.login()

    logger.debug("Login Completed")

    # Wait for the page to load completely
    await page.wait_for_load_state('networkidle')
    logger.debug("Portal Loaded for iq referrals")
    await page.locator('//*[@id="left-panel"]/nav/ul/li[2]/ul/li[2]/a').click()
    logger.debug("Clicked on Quotation Listing")
    await page.wait_for_selector('.dx-datagrid-table.dx-datagrid-table-fixed')
    logger.debug("quotation listing page loaded")


    for iq_quotation_number in iq_quotation_numbers:
        try:
            logger.debug(f"Searching for Quotation No: {iq_quotation_number}")
            quo_status = await page.get_by_role("row", name=iq_quotation_number).locator('[aria-colindex="8"]').text_content()

            if quo_status.startswith("Under Review"):
                print(f"Quotation No: {iq_quotation_number} is still Under Review")
                logger.info(f"Quotation No: {iq_quotation_number} is still Under Review")
                update_last_check_datetime(iq_quotation_number)

            elif quo_status.startswith("APPROVED"):
                print(f"Quotation No: {iq_quotation_number} is APPROVED")
                logger.info(f"Quotation No: {iq_quotation_number} is APPROVED")
                await download_quotation(page, iq_quotation_number)
                update_last_check_datetime(iq_quotation_number)
                await run_portals(iq_quotation_number, Orient_Status.APPROVED.value)


            elif quo_status.startswith("REJECTED"):
                print(f"Quotation No: {iq_quotation_number} is REJECTED")
                logger.info(f"Quotation No: {iq_quotation_number} is REJECTED")
                update_last_check_datetime(iq_quotation_number)
                await run_portals(iq_quotation_number, Orient_Status.REJECTED.value)

            else:
                print(f"Quotation No: {iq_quotation_number} is in an unknown state")
                logger.info(f"Quotation No: {iq_quotation_number} is in an unknown state")

        except Exception as e:
            error_message = f"Error: Quotation No: {iq_quotation_number} not found. Exception: {e}"
            print(error_message)
            logger.error(error_message)


async def download_quotation(page, iq_quotation_no):
       # --------------------- download quotation sheet --------------------- #

        # Perform the action on the row with the saved Quotation No
        await page.get_by_role("row", name=iq_quotation_no).get_by_label("Action").click()
        time.sleep(1)
        
        logger.debug("Action Button Clicked")
        
        async with page.expect_download() as download_info:
            await page.get_by_text("Download Quotation").click()
            download = await download_info.value
            logger.debug("Download Quotation Button Clicked")
        
        # Save the file to a local path
        if download:
            # Specify the local path where you want to save the file
            await download.save_as(os.path.join(ORIENT_QUOTATION_DIR, "quotation_orient.pdf"))
            logger.debug("File saved successfully")

        time.sleep(MAX_SLEEP)