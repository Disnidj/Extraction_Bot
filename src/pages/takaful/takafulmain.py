# src/pages/takaful/takafulmain.py

from playwright.async_api import Playwright
from src.pages.takaful.login_page import LoginPage
from src.pages.takaful.categories.category_1_page import Category1Page
from src.pages.takaful.categories.category_2_page import Category2Page
from src.pages.takaful.categories.category_3_page import Category3Page
from src.pages.takaful.quotation_page import QuotationPage
from src.pages.takaful.download_page import DownloadPage
from src.services.excel_service.read_excel import read_excel

from src.utils.logger import takaful_logger

import os


async def login_takaful(playwright: Playwright, referral_id):

    # Get the pandas dataframes from the Excel file
    # df1, catA, catB, catC, takaful_catA, takaful_catB, takaful_catC = read_excel('TAKAFUL EMARAT')

    df1, df2 = read_excel('TAKAFUL EMARAT', 'default')
    portal_name = 'TAKAFUL EMARAT'

    if df1.empty:
        print("No data found in sheet 1")
        raise Exception("No data found in sheet 1")

    if df2.empty:
        # print("No data found for Takaful Emarat")
        return

    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    cat1 = df2[df2['Category'] == unique_categories_list[0]]

    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context(accept_downloads=True)
    context.set_default_timeout(20000)

    # Enable tracing
    await context.tracing.start(screenshots=True, snapshots=True)

    page = await context.new_page()

    try:
        # Login to the Takaful portal
        login_page = LoginPage(page)
        await login_page.login()
        takaful_logger.debug("Takaful Login Completed")

        # Verify we're on the correct page before proceeding
        try:
            await page.wait_for_selector('text="Create new quote"', timeout=10000)
            takaful_logger.debug("Dashboard verified - Ready to create quotation")
        except Exception as e:
            takaful_logger.error(f"Dashboard verification failed: {e}")
            raise Exception("Login verification failed - Cannot proceed to quotation creation")

        # Create a new quotation        
        quotation_page = QuotationPage(page)

        takaful_logger.debug("Creating Quotation")
        if no_of_categories == 1:
            cat1 = df2[df2['Category'] == unique_categories_list[0]]
            await quotation_page.create_quotation(df1, cat1, None, None, no_of_categories,portal_name)
        elif no_of_categories == 2:
            cat1 = df2[df2['Category'] == unique_categories_list[0]]
            cat2 = df2[df2['Category'] == unique_categories_list[1]]
            await quotation_page.create_quotation(df1, cat1, cat2, None, no_of_categories,portal_name)
        elif no_of_categories == 3:
            print("3 categories")
            cat1 = df2[df2['Category'] == unique_categories_list[0]]
            cat2 = df2[df2['Category'] == unique_categories_list[1]]
            cat3 = df2[df2['Category'] == unique_categories_list[2]]
            await quotation_page.create_quotation(df1, cat1, cat2, cat3, no_of_categories,portal_name)

        takaful_logger.debug("Quotation Created")


        region = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0]).strip()
        tpa = str(cat1['TPA'].iloc[0]).strip()
        plan = str(cat1['Network'].iloc[0]).strip()

        # Fill Category A
        category_a_page = Category1Page(page)
        if not await category_a_page.fill_category_1(cat1, region, tpa, plan):
            takaful_logger.error("Failed to fill Category A")
            return

        takaful_logger.debug("Category A Filled")

        print("No of categories: ", no_of_categories)
        if no_of_categories > 1:
            category_b_page = Category2Page(page)
            cat2 = df2[df2['Category'] == unique_categories_list[1]]
            if not await category_b_page.fill_category_2(cat2, region, tpa, plan):
                takaful_logger.error("Failed to fill Category B")
                return

            takaful_logger.debug("Category B Filled")

        if no_of_categories > 2:
            category_c_page = Category3Page(page)
            cat3 = df2[df2['Category'] == unique_categories_list[2]]
            if not await category_c_page.fill_category_3(cat3):
                takaful_logger.error("Failed to fill Category C")
                return

            takaful_logger.debug("Category C Filled")

        # download the quotation
        download_page = DownloadPage(page)
        await download_page.download_pdf()

        takaful_logger.debug("Download PDF Completed")

        # Close the browser context and browser
        await context.close()
        await browser.close()

    except Exception as e:
        print(f"Error encountered: {e}")

    finally:
        # Close the browser context and browser
        await context.close()
        await browser.close()
