from patchright.async_api import Playwright
from src.pages.rak.login_page import LoginPage
from src.pages.rak.process_page import ProcessPage
from src.pages.rak.categories.category_1_page import Category1Page
from src.pages.rak.categories.category_2_page import Category2Page
from src.pages.rak.categories.category_3_page import Category3Page
# from src.utils.cookies import gargash_cookies
from src.pages.rak.download_page import DownloadPage
from src.services.excel_service.read_excel import read_excel
# from src.utils.portal_logger import setup_portal_logger
from src.utils.logger import rak_logger

async def login_rak(playwright: Playwright, referral_id):
    
    # Define portal name
    portal_name = "RAK INSURANCE"
    
    # Setup portal-specific logger
    # logger = setup_portal_logger("RAK", referral_id)
    
    # Get the pandas dataframes from the Excel file
    df1, df2 = read_excel('RAK INSURANCE', 'default')

    if df1.empty:
        rak_logger.error("No data found sheet1")
        raise Exception("No data found sheet1")

    if df2.empty:
        # rak_logger.error("Empty company data IQ portal - RAK INSURANCE")
        return

    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    if no_of_categories == 0:
        rak_logger.error("No categories found")
        raise Exception("No categories found")

    cat1 = df2[df2['Category'] == unique_categories_list[0]]
    rak_logger.debug(f"Unique categories: {unique_categories_list}")

    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args, channel="msedge")
    context = await browser.new_context(accept_downloads=True)
    context.set_default_timeout(180000)

    # # Set the cookie to the context
    # await context.add_cookies(gargash_cookies)
    page = await context.new_page()

    # Login to the rak portal
    login_page = LoginPage(page)
    login_successful = await login_page.login()
    if not login_successful:
        rak_logger.error("Login failed.........")
        await context.close()
        await browser.close()
        return True

    rak_logger.debug("Login Completed")
    
    # Fill the process form
    process_page = ProcessPage(page, portal_name)
    quotation_no = await process_page.fill_process_form(df1, cat1)
    if quotation_no is None:
        rak_logger.error("Failed to fill Process Form")
        return
    rak_logger.info("Process Form filled Completed")
        
    # Handle Category A
    if cat1 is not None and not cat1.empty:
        category_1_page = Category1Page(page)     
        if await category_1_page.fill_category_1(cat1, df2) != True:
            rak_logger.error("Failed to fill Category A")
            return

        rak_logger.info("Category A Filled")
        
    # Handle Category B
    if no_of_categories > 1:
        # Handle Category B
        category_2_page = Category2Page(page)
        cat2 = df2[df2['Category'] == unique_categories_list[1]]
        if await category_2_page.fill_category_2(cat2, df2) != True:
            rak_logger.error("Failed to fill Category B")
            return

        rak_logger.info("Category B Filled")

    # Handle Category C
    if no_of_categories > 2:
        category_3_page = Category3Page(page)
        cat3 = df2[df2['Category'] == unique_categories_list[2]]        
        if await category_3_page.fill_category_3(cat3) != True:
            rak_logger.error("Failed to fill Category C")
            return

        rak_logger.info("Category C Filled")
        

    # Download the PDF
    download_page = DownloadPage(page)
    return_value = await download_page.download_quotation(quotation_no, unique_categories_list, df2)

    if return_value != True:
        rak_logger.error("Failed to download the quotation")
        # Close the browser context and browser
        await context.close()
        await browser.close()
        rak_logger.info("RAK INSURANCE Finished")
        return False

    rak_logger.info("Quotation download completed")

    # Close the browser context and browser
    await context.close()
    await browser.close()

    rak_logger.debug("RAK INSURANCE Finished")
    return return_value