# src/pages/takaful/takafulmain.py
import asyncio
import asyncio
from playwright.async_api import Playwright
from src.pages.qatar.login_page import LoginPage

from src.pages.qatar.categories_p1.category_1_p1 import Category1Page_p1
from src.pages.qatar.categories_p1.category_2_p1 import Category2Page_p1
from src.pages.qatar.categories_p1.category_3_p1 import Category3Page_p1

from src.pages.qatar.categories.category_1_page import Category1Page
from src.pages.qatar.categories.category_2_page import Category2Page
from src.pages.qatar.categories.category_3_page import Category3Page

from src.pages.qatar.categories_NAS.category_1_page import Category1PageNAS
from src.pages.qatar.categories_NAS.category_2_page import Category2PageNAS
from src.pages.qatar.categories_NAS.category_3_page import Category3PageNAS

from src.pages.qatar.quotation_page import QuotationPage
from src.pages.qatar.download_page import DownloadPage
from src.services.excel_service.read_excel import read_excel
from src.utils.load_yaml import AURA_GENERATED_CENSUS_DIR, MAX_SLEEP

#from src.utils.logger import logger
from src.utils.logger import qatar_logger

import os


async def login_qatar(playwright: Playwright, referral_id):
    qatar_logger.info("Starting Qatar Takaful process")

    # Read Excel data
    df1, df2 = read_excel('QATAR INSURANCE CO', referral_id)

    portal_name = "QATAR INSURANCE CO"

    if df1.empty:
        qatar_logger.error("No data found in sheet 1")
        raise Exception("No data found in sheet 1")

    if df2.empty:
        # qatar_logger.error("Empty company data found for Qatar")
        return

    # Get unique categories dynamically
    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    qatar_logger.info(f"Number of categories found: {no_of_categories}")

    # Dynamically create category dataframes
    category_dataframes = {}
    for i, category in enumerate(unique_categories_list):
        category_dataframes[f"cat{i+1}"] = df2[df2['Category'] == category]

    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context(accept_downloads=True)
    context.set_default_timeout(60000)

    # Enable tracing
    await context.tracing.start(screenshots=True, snapshots=True)

    page = await context.new_page()

    try:
        # Login to the Takaful portal
        login_page = LoginPage(page)
        await login_page.login()
        qatar_logger.debug("Login Completed")

        # Create a new quotation
        quotation_page = QuotationPage(page)
        await quotation_page.create_quotation(df1, category_dataframes["cat1"], no_of_categories, portal_name)
        qatar_logger.debug("Quotation Created")

        # Fill category pages based on the number of categories
        if no_of_categories >= 1:
            category_a_page_p1 = Category1Page_p1(page)
            await category_a_page_p1.fill_category_1_p1(df1, category_dataframes["cat1"], portal_name)
            qatar_logger.debug("Category 1 (P1) Filled")
            await asyncio.sleep(2)

        if no_of_categories >= 2:
            category_b_page_p1 = Category2Page_p1(page)
            await category_b_page_p1.fill_category_2_p1(df1, category_dataframes["cat2"], category_dataframes["cat1"], portal_name)
            qatar_logger.debug("Category 2 (P1) Filled")

        if no_of_categories >= 3:
            category_c_page_p1 = Category3Page_p1(page)
            await category_c_page_p1.fill_category_3_p1(df1, category_dataframes["cat3"], category_dataframes["cat1"], category_dataframes["cat2"])
            qatar_logger.debug("Category 3 (P1) Filled")

        try:
            # Upload the Census File
            await page.locator("#fileClass").set_input_files(os.path.join(AURA_GENERATED_CENSUS_DIR, "aura_map.xlsx"), timeout=80000)
            await asyncio.sleep(2)
            qatar_logger.info("Census File Uploaded")

            # Wait for the page to load
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(1)

        except Exception as e:
            qatar_logger.error(f"Error occured while uploading census - {e}")
            print(f"Error occured while uploading census - {e}")
            return

        # Check if the modal is visible
        modal_visible = await page.locator("ngb-modal-window").is_visible()

        if modal_visible:
            qatar_logger.info("Modal is displayed")
            # Wait for the Cancel button to be visible
            await page.locator("button.cancel-buttons.medium.px-3").wait_for()
            # Click the Cancel button
            await page.locator("button.cancel-buttons.medium.px-3").click()
            qatar_logger.info("Clicked the Cancel button")
        else:
            qatar_logger.info("Modal is not displayed")

        # Proceed to the next step
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(1)
        await page.get_by_role("button", name="Proceed").click()
        qatar_logger.debug("Clicked the Proceed button")
        await asyncio.sleep(10)

        # Fill NAS or Medical categories based on TPA value
        TPA_Value = str(category_dataframes["cat1"]['TPA'].iloc[0])
        qatar_logger.info(f"TPA in main: {TPA_Value}")

        region = str(category_dataframes["cat1"]['Region'].iloc[0])
        network = str(category_dataframes["cat1"]['Network'].iloc[0])


        try:
            if TPA_Value == "NAS":
                # SME NAS category fill
                if no_of_categories >= 1:
                    category_a_page_nas = Category1PageNAS(page)
                    await category_a_page_nas.fill_category_1(category_dataframes["cat1"],region, TPA_Value, network, portal_name)
                    qatar_logger.debug("NAS Category 1 Filled")

                if no_of_categories >= 2:
                    category_b_page_nas = Category2PageNAS(page)
                    await category_b_page_nas.fill_category_2(category_dataframes["cat2"], region,  TPA_Value, network, portal_name)
                    qatar_logger.debug("NAS Category 2 Filled")

                if no_of_categories >= 3:
                    category_c_page_nas = Category3PageNAS(page)
                    await category_c_page_nas.fill_category_3(category_dataframes["cat3"])
                    qatar_logger.debug("NAS Category 3 Filled")

            else:
                # SME Medical category fill
                if no_of_categories >= 1:
                    category_a_page = Category1Page(page)
                    await category_a_page.fill_category_1(df1, category_dataframes["cat1"])
                    qatar_logger.debug("Medical Category 1 Filled")

                if no_of_categories >= 2:
                    category_b_page = Category2Page(page)
                    await category_b_page.fill_category_2(df1, category_dataframes["cat2"])
                    qatar_logger.debug("Medical Category 2 Filled")

                if no_of_categories >= 3:
                    category_c_page = Category3Page(page)
                    await category_c_page.fill_category_3(df1, category_dataframes["cat3"])
                    qatar_logger.debug("Medical Category 3 Filled")

            await asyncio.sleep(0.1)

        except Exception as e:
            qatar_logger.error(f"An error occurred while filling categories: {e}")

        # # Download the quotation
        # download_page = DownloadPage(page, QATAR_QUOTATION_DIR)
        # await download_page.download_pdf()
        # qatar_logger.debug("Download PDF Completed")

        # # Save trace and screenshot
        # custom_dir = SCREENSHOTS_DIR
        # os.makedirs(custom_dir, exist_ok=True)

        # trace_path = os.path.join(custom_dir, 'custom_trace.zip')
        # screenshot_path = os.path.join(custom_dir, 'custom_screenshot.png')

        # await context.tracing.stop(path=trace_path)
        # qatar_logger.info(f"Trace saved to: {trace_path}")

        # await page.screenshot(path=screenshot_path)
        # qatar_logger.info(f"Screenshot saved to: {screenshot_path}")

    except Exception as e:
        qatar_logger.error(f"Error encountered: {e}")

    finally:
        # Close the browser context and browser
        await context.close()
        await browser.close()