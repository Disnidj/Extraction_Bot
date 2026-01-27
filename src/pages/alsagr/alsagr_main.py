from patchright.async_api import Playwright
from src.pages.alsagr.login_page import LoginPage
from src.pages.alsagr.quotation_page import QuotationPage
from src.pages.alsagr.process_page import ProcessPage
from src.pages.alsagr.categories.category_1_page import Category1Page
from src.pages.alsagr.categories.category_2_page import Category2Page
from src.pages.alsagr.categories.category_3_page import Category3Page
from src.services.excel_service.read_excel import read_excel
from src.utils.logger import alsagr_logger
from src.utils.load_yaml import MED_SLEEP, MAX_SLEEP
import time


# Main function to login to the NLG portal
""" 

*** This is the standard function to initialize to the company portal (this sample case NLG company) entry, 
you can customize this function based on your requirement. follow this structure for every company portal. 
If you have specific requirements and decide to change the structure, you need to inform us before starting the development. ***

"""

async def login_alsagr(playwright: Playwright, referral_id):
    
    # Define portal name
    portal_name = "AL SAGR INSURANCE COMPANY"
    
    # Get the pandas dataframes from the Excel file
    # *** customize this function parameter 1 based on your company Unique name in this sample code it's 'NLGIC COMPANY' ***
    df1, df2 = read_excel('AL SAGR INSURANCE COMPANY', referral_id)

    # Check if the dataframes are empty
    if df1.empty:
        print("No data found sheet1")
        alsagr_logger.error("No data found sheet1")
        raise Exception("No data found sheet1")

    if df2.empty:
        print("Empty company data ALSAGR")
        # alsagr_logger.error("Empty company data ALSAGR")
        return

    # Get the unique categories from the dataframe
    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    if no_of_categories == 0:
        print("No categories found")
        alsagr_logger.error("No categories found")
        raise Exception("No categories found")

    # Get the category 1 dataframe for each category
    cat1 = df2[df2['Category'] == unique_categories_list[0]]
    alsagr_logger.debug(f"Unique categories: {unique_categories_list}")

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
    await process_page.fill_process_form(df1, cat1, portal_name)

    # Fill the category 1 form
    category_1_page = Category1Page(page)
    if not await category_1_page.fill_category_1(cat1):
        alsagr_logger.error("Failed to fill Category A")
        return

    alsagr_logger.debug("Category A Filled")

    # Fill the category 2 form if there are more than 1 category
    if no_of_categories > 1:
        category_2_page = Category2Page(page)
        cat2 = df2[df2['Category'] == unique_categories_list[1]]
        if not await category_2_page.fill_category_2(cat2):
            alsagr_logger.error("Failed to fill Category B")
            return
        alsagr_logger.debug("Category B Filled")

    # Fill the category 3 form if there are more than 2 categories
    if no_of_categories > 2:
        category_3_page = Category3Page(page)
        cat3 = df2[df2['Category'] == unique_categories_list[2]]
        if not await category_3_page.fill_category_3(cat3):
            alsagr_logger.error("Failed to fill Category C")
            return
        alsagr_logger.debug("Category C Filled")

    # ---------------------------benefit structure page, filling categories plans-------------------------------------
    time.sleep(MED_SLEEP)
    await page.wait_for_load_state('networkidle')
    # Click Save button
    alsagr_logger.debug("Clicking save button")
    # await page.get_by_role("button", name="Ɠ Save").click()
    await page.locator("//div[@id='tooltip-container2']//button[@title='Save']").click()
    alsagr_logger.debug("Clicked save button")
    # //*[@id="tooltip-container2"]/button
    time.sleep(MED_SLEEP)
    #  Error Handling for save
    await page.wait_for_load_state('networkidle')
    if await page.locator("//html/body/div[4]/div/div/div/div/div[2]/div/button").is_visible():
        await page.locator("//html/body/div[4]/div/div/div/div/div[2]/div/button").click()
        alsagr_logger.debug("Error Handling 1")
    else:
        await page.get_by_role("button", name="Next m").click()
        alsagr_logger.debug("move next")
        time.sleep(MED_SLEEP)

    # Click next button
    await page.wait_for_load_state('networkidle')
    await page.locator("//button[normalize-space()='Next']").click()
    time.sleep(MED_SLEEP)
    #--------------------------------------------groupquotationmedicalform------------------------------------------------------
    # Click next button
    await page.locator("//button[normalize-space()='Next']").click()
    time.sleep(MED_SLEEP)
        
    #-------------------------Validation error(s) Save Plans Benefits First In BenefitStructure Page.(POPUP WINDOW)------------------
    # Error handling
    await page.wait_for_load_state('networkidle')
    alsagr_logger.debug("Error Handling 2")
    time.sleep(MAX_SLEEP)
    time.sleep(MAX_SLEEP)
    time.sleep(MAX_SLEEP)
    if await  page.get_by_text("Message").is_visible():
        await page.wait_for_load_state('networkidle')
        await page.locator("//button[normalize-space()='Close']").click()
        alsagr_logger.debug("Message visible")
    else:
        await page.get_by_label("Second group").get_by_role("button", name="").click()
        alsagr_logger.debug("Second group")
        time.sleep(MED_SLEEP)
   

    # download the quotation
    quotation_page = QuotationPage(page)
    alsagr_logger.debug("Downloading quotation (Alsagr)")
    await quotation_page.download_quotation()
    alsagr_logger.debug("Download completed")

    # Close the browser context and browser
    await context.close()
    await browser.close()
    alsagr_logger.debug("Alsagr process completed")
