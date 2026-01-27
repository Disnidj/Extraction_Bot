from patchright.async_api import Playwright
from src.pages.gig.login_page import LoginPage
from src.pages.gig.quotation_page import QuotationPage
from src.pages.gig.process_page import ProcessPage
from src.pages.gig.categories.category_1_page import Category1Page
from src.pages.gig.categories.category_2_page import Category2Page
from src.pages.gig.categories.category_3_page import Category3Page
from src.services.excel_service.read_excel import read_excel
from src.utils.logger import gig_logger
from src.utils.load_yaml import MED_SLEEP, MAX_SLEEP
import asyncio


# Main function to login to the NLG portal
""" 

*** This is the standard function to initialize to the company portal (this sample case NLG company) entry, 
you can customize this function based on your requirement. follow this structure for every company portal. 
If you have specific requirements and decide to change the structure, you need to inform us before starting the development. ***

"""

async def login_gig(playwright: Playwright, referral_id):
    
    # Define portal name
    portal_name = "GIG Insurance"
    
    # Get the pandas dataframes from the Excel file
    # *** customize this function parameter 1 based on your company Unique name in this sample code it's 'NLGIC COMPANY' ***
    df1, df2 = read_excel('GIG Insurance', referral_id)
    # print(df2)

    # Check if the dataframes are empty
    if df1.empty:
        print("No data found sheet1")
        gig_logger.error("No data found sheet1")
        raise Exception("No data found sheet1")

    if df2.empty:
        print("Empty company data GIG")
        # gig_logger.error("Empty company data GIG")
        return

    # Get the unique categories from the dataframe
    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    if no_of_categories == 0:
        print("No categories found")
        gig_logger.error("No categories found")
        raise Exception("No categories found")

    # Get the category 1 dataframe for each category
    cat1 = df2[df2['Category'] == unique_categories_list[0]]
    gig_logger.debug(f"Unique categories: {unique_categories_list}")

    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    # browser = await playwright.chromium.launch(channel="chrome",headless=False, args=args)
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
    await process_page.fill_process_form(df1, cat1, portal_name)

    # Fill the category 1 form
    category_1_page = Category1Page(page)
    gig_logger.debug('Category 1 Starting')
    await category_1_page.fill_category_1(cat1)
    gig_logger.debug('Catogory 1 Filled')

    # Fill the category 2 form if there are more than 1 category
    if no_of_categories > 1:
        gig_logger.debug('Category 2 Starting')
        category_2_page = Category2Page(page)

        cat2 = df2[df2['Category'] == unique_categories_list[1]]
        await category_2_page.fill_category_2(cat2)
        gig_logger.debug("Category 2 Filled")

    # # Fill the category 3 form if there are more than 2 categories
    # if no_of_categories > 2:
    #     category_3_page = Category3Page(page)
    #     gig_logger.debug('Category 3 Starting')
    #     cat3 = df2[df2['Category'] == unique_categories_list[2]]
    #     await category_3_page.fill_category_3(cat3)
    #     gig_logger.debug('Category 3 Filled')

   
   
   

    # download the quotation
    quotation_page = QuotationPage(page)
    await quotation_page.download_quotation()

    # Close the browser context and browser
    await context.close()
    await browser.close()
    gig_logger.debug("GIG process completed")
