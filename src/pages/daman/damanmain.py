# src/pages/daman/damanmain.py
import asyncio
import asyncio
import pandas
from playwright.async_api import Playwright
from src.pages.daman.login_page import LoginPage
from src.pages.daman.categories.category_1_page import Category1Page
from src.pages.daman.categories.category_2_page import Category2Page
from src.pages.daman.categories.category_3_page import Category3Page
from src.pages.daman.quotation_page import QuotationPage
from src.pages.daman.download_page import DownloadPage
from src.services.excel_service.read_excel import read_excel
# from src.utils.load_yaml import DAMAN_QUOTATION_DIR, SCREENSHOTS_DIR, ATTACHMENTS_SAVE_DIR
from src.utils.load_yaml import ATTACHMENTS_SAVE_DIR
from src.utils.logger import daman_logger
import os


async def login_daman(playwright: Playwright, referral_id):
    daman_logger.info("Starting Daman process")
    portal_name = 'Daman Insurance'


    # Read Excel data
    df1, df2 = read_excel(portal_name, referral_id)

    if df1.empty:
        daman_logger.error("No data found in sheet 1")
        raise Exception("No data found in sheet 1")

    if df2.empty:
        # daman_logger.error("No data found for Daman")
        return

    # Get unique categories dynamically
    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    daman_logger.debug(f"Number of categories found: {no_of_categories}")

    # Dynamically create category dataframes
    category_dataframes = {}
    for i, category in enumerate(unique_categories_list):
        category_dataframes[f"cat{i+1}"] = df2[df2['Category'] == category]

    # Extract Salary Types for validation
    excel_data_df = pandas.read_excel(os.path.join(ATTACHMENTS_SAVE_DIR, "MemberUpload.xlsx"), sheet_name='Sheet1')
    category_salary_mapping = excel_data_df.set_index('Category')['Salary Type'].to_dict()

    # Print the extracted mapping
    daman_logger.debug(f"Category Salary Mapping: {category_salary_mapping}")

    # Access specific salary type for each category dynamically
    salary_types = {}
    for i, category in enumerate(unique_categories_list):
        salary_types[f"salary_{category}"] = category_salary_mapping.get(category, 'Not Available')

    # Print salary types for debugging
    for category, salary in salary_types.items():
        daman_logger.debug(f"Salary Type for {category}: {salary}")

    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context(accept_downloads=True)
    context.set_default_timeout(20000)

    # Enable tracing
    await context.tracing.start(screenshots=True, snapshots=True)

    page = await context.new_page()

    # Login to the Daman portal
    login_page = LoginPage(page)
    await login_page.login()
    # login_successful = await login_page.login()
    # if not login_successful:
    #     daman_logger.error('Login failed.........')
    #     print("Login failed.........")
        # await context.close()
        # await browser.close()
        # return True

    # Extract region, tpa, and network from df1/df2
    region = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0]).strip()
    tpa = str(df2['TPA'].iloc[0]).strip()
    network = str(df2['Network'].iloc[0]).strip()

    # Create a new quotation
    quotation_page = QuotationPage(page)
    process_page = await quotation_page.create_quotation(
        df1,
        category_dataframes.get("cat1", None),
        category_dataframes.get("cat2", None),
        category_dataframes.get("cat3", None),
        no_of_categories,
        salary_types.get("salary_A", "Not Available"),
        salary_types.get("salary_B", "Not Available"),
        salary_types.get("salary_C", "Not Available"),
        region,
        tpa,
        network,
        portal_name
    )

    if process_page != True:
        daman_logger.error("Failed to Fill the Quotation Page")
        return
    daman_logger.info("The Quotation Page Filled")

    # Download the quotation
    download_page = DownloadPage(page)
    daman_logger.debug("Starting download process")    
    await download_page.download()
    daman_logger.info("Quotation download completed")


    # Close the browser context and browser
    await context.close()
    await browser.close()