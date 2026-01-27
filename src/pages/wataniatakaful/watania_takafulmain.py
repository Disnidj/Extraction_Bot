import os
import pandas as pd
from playwright.async_api import Playwright
from src.pages.wataniatakaful.login_page import LoginPage
from src.utils.load_yaml import ATTACHMENTS_SAVE_DIR,AURA_GENERATED_CENSUS_DIR
from src.services.excel_service.read_excel import read_excel
import asyncio
from src.utils.logger import wataniatakaful_logger
from src.pages.wataniatakaful.form import Form
from src.pages.wataniatakaful.categories.category_1_page import Category1Page
from src.pages.wataniatakaful.categories.category_2_page import Category2Page
from src.pages.wataniatakaful.categories.category_3_page import Category3Page
from src.pages.wataniatakaful.download_page import DownloadPage


async def login_wataniatakaful(playwright: Playwright, referral_id):

    df1, df3 = read_excel('Watania Takaful', referral_id)
    portal_name = 'Watania Takaful'

    if df1.empty:
        print("No data found in sheet 1")
        raise Exception("No data found in sheet 1")

    if df3.empty:
        # print("No data found for watania")
        return

     # Update the correct path and sheet name for df2 (Medical Upload)
    file_path = os.path.join(AURA_GENERATED_CENSUS_DIR, "aura_map.xlsx")
    df2 = pd.read_excel(file_path, sheet_name="Sheet1")
    wataniatakaful_logger.debug('Updated the correct path and sheet name for df2 (Medical Upload)')

    if df1.empty:
        print("No data found in Sheet1")
        wataniatakaful_logger.debug('No data found in Sheet1')
        raise Exception("No data found in Sheet1")

    if df2.empty:
        print("No data found in Census Upload")
        wataniatakaful_logger.debug('No data found in Census Upload')
        raise Exception("No data found in Census Upload")

    # Extract unique categories from the 'Category' column
    unique_categories = df2['Category'].unique()
    
    category_mapping = {
        "Category A": "A",
        "Category B": "B",
        "Category C": "C"
    }
    mapped_categories = [category_mapping.get(category, category) for category in unique_categories]
    unique_mapped_categories = sorted(set(mapped_categories))
    
    print(f"Mapped and unique categories: {unique_mapped_categories}")

    # Get the number of unique categories
    num_categories = len(unique_mapped_categories)
    print(f"Number of unique categories: {num_categories}")

    # Launch the browser
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    context.set_default_timeout(60000)
    page = await context.new_page()

    # Login and process form
    login = LoginPage(page)
    await login.perform_login()
    
    # Verify we're in the correct state before proceeding
    try:
        # Add a small wait to ensure page is fully loaded after login
        await asyncio.sleep(2)
        wataniatakaful_logger.debug("Wataniatakaful Login Completed - Ready to proceed with form")
    except Exception as e:
        wataniatakaful_logger.error(f"Login verification failed: {e}")
        raise Exception("Login verification failed - Cannot proceed to form filling")

    await asyncio.sleep(5)
    # Instantiate formNew with df1 data and portal_name
    form = Form(page, df1, df3, portal_name)
    if not await form.fill_company_information(num_categories, df1):
        wataniatakaful_logger.error('Error in Form Page')
        return
    
    unique_categories_list = sorted(df3['Category'].unique().tolist())

    region = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0]).strip()
    tpa = str(df3['TPA'].values[0])
    plan = str(df3['Network'].values[0])


    # Process categories based on unique categories in letters
    if 'A' in unique_mapped_categories:
        cat1 = df3[df3['Category'] == unique_categories_list[0]]
        categories1 = Category1Page(page, portal_name)
        if not await categories1.fill_category_1(cat1, region, tpa, plan):
            wataniatakaful_logger.error("Failed to fill Category A")
            return

        wataniatakaful_logger.debug("Category A Filled")
        # await categories1.categories1_information(cat1)

    if 'B' in unique_mapped_categories:
        cat2 = df2[df2['Category'] == unique_categories_list[1]]
        categories2 = Category2Page(page)
        if not await categories2.fill_category_2(cat2, region, tpa, plan):
            wataniatakaful_logger.error("Failed to fill Category B")
            return

        wataniatakaful_logger.debug("Category B Filled")

        # await categories2.categories2_information(cat2)

    if 'C' in unique_mapped_categories:
        cat3 = df2[df2['Category'] == unique_categories_list[2]]
        categories3 = Category3Page(page)
        if not await categories3.fill_category_3(cat3):
            wataniatakaful_logger.error("Failed to fill Category C")
            return

        wataniatakaful_logger.debug("Category C Filled")
        # await categories3.categories3_information(cat3)

    # download the quotation
    quotation_page = DownloadPage(page)
    await quotation_page.download_pdf()

    # Close the browser context and browser
    await context.close()
    await browser.close()
    wataniatakaful_logger.debug("WATANIA TAKAFUL process completed")