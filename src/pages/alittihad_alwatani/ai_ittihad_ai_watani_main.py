from patchright.async_api import async_playwright

from src.pages.alittihad_alwatani.login_page import LoginPage
from src.pages.alittihad_alwatani.quotation_page import QuotationPage
from src.pages.alittihad_alwatani.process_page import ProcessPage

from src.pages.alittihad_alwatani.categories.category_1_page import Category1Page
from src.pages.alittihad_alwatani.categories.category_2_page import Category2Page
from src.pages.alittihad_alwatani.categories.category_3_page import Category3Page
from src.services.excel_service.read_excel import read_excel

from src.utils.logger import alittihad_logger
import asyncio


# Main function to login to the NLG portal
""" 

*** This is the standard function to initialize to the company portal (this sample case NLG company) entry, 
you can customize this function based on your requirement. follow this structure for every company portal. 
If you have specific requirements and decide to change the structure, you need to inform us before starting the development. ***

"""

async def login_ai_ittihad_ai_watani(playwright: async_playwright, referral_id):
    # Get the pandas dataframes from the Excel file
    # *** customize this function parameter 1 based on your company Unique name in this sample code it's 'NLGIC COMPANY' ***
    df1, df2 = read_excel('Al Ittihad Al Watani', referral_id)
    portal_name = 'Al Ittihad Al Watani'
    print("Al Ittihad Al Watani login started")
    alittihad_logger.info("Al Ittihad Al Watani login started")

    # Check if the dataframes are empty
    if df1.empty:
        print("No data found sheet1")
        alittihad_logger.error("No data found sheet1")
        raise Exception("No data found sheet1")

    if df2.empty:
        print("Empty company data Al Ittihad Al Watani")
        # alittihad_logger.error("Empty company data Al Ittihad Al Watani")
        return
    
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

    # Get the unique categories from the dataframe
    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    if no_of_categories == 0:
        print("No categories found")
        alittihad_logger.error("No categories found")
        raise Exception("No categories found")

    # Get the category 1 dataframe for each category
    cat1 = df2[df2['Category'] == unique_categories_list[0]]
    alittihad_logger.info(f"Unique categories: {unique_categories_list}")

    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context(accept_downloads=True)
    
    # Set the default timeout to 60 seconds
    #  *** customize this timeout based on your requirement ***
    context.set_default_timeout(60000)
    page = await context.new_page()

    # Login to the Al Ittihad Al Watani
    login_page = LoginPage(page)
    await login_page.login()
    
    # Verify we're in the correct state before proceeding
    try:
        # Add a small wait to ensure page is fully loaded after login
        await asyncio.sleep(2)
        alittihad_logger.info("Al Ittihad Al Watani Login Completed - Ready to proceed with process form")
    except Exception as e:
        alittihad_logger.error(f"Login verification failed: {e}")
        raise Exception("Login verification failed - Cannot proceed to process form")

    # Fill the process form
    process_page = ProcessPage(page,df1,df2)
    if not await process_page.fill_process_form(df1, cat1,num_categories, portal_name):
        alittihad_logger.error("Failed to Fill the process form")
        return
    alittihad_logger.info("The process form Filled")
    
    region = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0]).strip()
    tpa = str(cat1['TPA'].iloc[0]).strip()
    network= str(cat1['Network'].iloc[0]).strip()
    
    # Fill the category 1 form
    category_1_page = Category1Page(page)
    if not await category_1_page.fill_category_1(cat1,  region, tpa, network):
        alittihad_logger.error("Failed to fill Category A")
        return

    alittihad_logger.info("Category A Filled")

    # Fill the category 2 form if there are more than 1 category
    if no_of_categories > 1:
        category_2_page = Category2Page(page)
        cat2 = df2[df2['Category'] == unique_categories_list[1]]

        if not await category_2_page.fill_category_2(cat2, region, tpa, network):
            alittihad_logger.error("Failed to fill Category B")
            return

        alittihad_logger.info("Category B Filled")

    # Fill the category 3 form if there are more than 2 categories
    if no_of_categories > 2:
        category_3_page = Category3Page(page)
        cat3 = df2[df2['Category'] == unique_categories_list[2]]
        if not await category_3_page.fill_category_3(cat3):
            alittihad_logger.error("Failed to fill Category C")
            return

        alittihad_logger.info("Category C Filled")
        
    await asyncio.sleep(5)

    # download the quotation
    quotation_page = QuotationPage(page)
    await quotation_page.download_quotation()
    if not await quotation_page.download_quotation():
        alittihad_logger.error("Failed to download the quotation")
        return

    alittihad_logger.info("Quotation download completed")

    # Close the browser context and browser
    await context.close()
    await browser.close()
    alittihad_logger.info("Al Ittihad Al Watani process completed")
