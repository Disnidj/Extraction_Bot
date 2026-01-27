from patchright.async_api import Playwright
from src.pages.adnic.login_page import LoginPage
from src.pages.adnic.quotation_page import QuotationPage
from src.pages.adnic.process_page import ProcessPage
from src.pages.adnic.categories.category_1_page import Category1Page
from src.pages.adnic.categories.category_2_page import Category2Page
from src.pages.adnic.categories.category_3_page import Category3Page
from src.pages.adnic.categories.category_LSB_page import CategoryLSBPage
from src.services.excel_service.read_excel import read_excel
from src.utils.logger import adnic_logger
import pandas as pd
from src.utils.load_yaml import ADNIC_GENERATED_CENSUS_DIR
import os

# Main function to login to the ADNIC portal
""" 

*** This is the standard function to initialize to the company portal (this sample case ADNIC company) entry, 
you can customize this function based on your requirement. follow this structure for every company portal. 
If you have specific requirements and decide to change the structure, you need to inform us before starting the development. ***

"""

async def login_adnic(playwright: Playwright, referral_id):

    # Define portal name
    portal_name = "ADNIC"
    
    adnic_logger.info("ADNIC login started")
    # Get the pandas dataframes from the Excel file
    # *** customize this function parameter 1 based on your company Unique name in this sample code it's 'NLGIC COMPANY' ***
    df1, df2 = read_excel('ADNIC', referral_id)

    mp_data_filepath = os.path.join(ADNIC_GENERATED_CENSUS_DIR, "adnic_census.xlsx")
    df3 = pd.read_excel(mp_data_filepath, sheet_name='Sheet1')
    unique_salarytype_list = sorted(df3['Salary Type'].unique().tolist())
    adnic_logger.info(f"Unique salary types: {unique_salarytype_list}")


    # Check if the dataframes are empty
    if df1.empty:
        print("No data found sheet1")
        adnic_logger.error("No data found sheet1")
        raise Exception("No data found sheet1")

    if df2.empty:
        print("Empty company data ADNIC")
        # adnic_logger.error("Empty company data ADNIC")
        return

    # Filter the DataFrame where the 'Salary Type' column is 'Enhanced'
    filtered_df = df3[df3['Salary Type'] == 'Enhanced']
    # Get the unique categories from the filtered DataFrame
    unique_categories_list = sorted(filtered_df['Category'].unique().tolist())
    # # Get the unique categories from the dataframe
    adnic_logger.info(f"Unique categories: {unique_categories_list}")
    
    no_of_categories = len(unique_categories_list)
    # if no_of_categories == 0:
    #     print("No categories found")
    #     logger.error("No categories found")
    #     raise Exception("No categories found")

    adnic_logger.info(f"Unique categories: {unique_categories_list}")


    all_categories_list = sorted(df2['Category'].unique().tolist())
    cat = df2[df2['Category'] == all_categories_list[0]]
    

    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context(accept_downloads=True)
    # Set the default timeout to 60 seconds
    #  *** customize this timeout based on your requirement ***
    context.set_default_timeout(60000)
    page = await context.new_page()

    # Login to the Takaful portal
    login_page = LoginPage(page)
    await login_page.login()

    # Fill the process form
    process_page = ProcessPage(page)
    await process_page.fill_process_form(df1, cat, portal_name)

    if 'LSB' in unique_salarytype_list:
        category_LSB_page = CategoryLSBPage(page)
        await category_LSB_page.fill_category_LSB()

    if 'Enhanced' in unique_salarytype_list:
        # Fill the category 1 form
        if no_of_categories == 1:
            category_1_page = Category1Page(page)
            cat1 = df2[df2['Category'] == unique_categories_list[0]]
            if not await category_1_page.fill_category_1(cat1):
                adnic_logger.error("Failed to fill Category A")
                return
            adnic_logger.debug("Category A Filled")

        # Fill the category 2 form if there are more than 1 category
        elif no_of_categories == 2:
            category_1_page = Category1Page(page)
            cat1 = df2[df2['Category'] == unique_categories_list[0]]
            category_2_page = Category2Page(page)
            cat2 = df2[df2['Category'] == unique_categories_list[1]]
            if not await category_2_page.fill_category_2(cat1, cat2):
                adnic_logger.error("Failed to fill Category B")
                return
            adnic_logger.debug("Category B Filled")


        # Fill the category 3 form if there are more than 2 categories
        if no_of_categories == 3:
            category_1_page = Category1Page(page)
            cat1 = df2[df2['Category'] == unique_categories_list[0]]
            category_2_page = Category2Page(page)
            cat2 = df2[df2['Category'] == unique_categories_list[1]]
            category_3_page = Category3Page(page)
            cat3 = df2[df2['Category'] == unique_categories_list[2]]
            if not await category_3_page.fill_category_3(cat1, cat2, cat3):
                adnic_logger.error("Failed to fill Category C")
                return
            adnic_logger.debug("Category C Filled")

    # download the quotation
    quotation_page = QuotationPage(page)
    await quotation_page.download_quotation()

    # Close the browser context and browser
    await context.close()
    await browser.close()
