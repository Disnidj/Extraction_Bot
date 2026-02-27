from patchright.async_api import Playwright
from src.pages.orient.login_page import LoginPage
from src.pages.orient.process_page import ProcessPage
from src.pages.orient.categories.category_1_page import Category1Page
from src.pages.orient.categories.category_2_page import Category2Page
from src.pages.orient.categories.category_3_page import Category3Page
from src.utils.cookies import orient_cookies
from src.pages.orient.download_page import DownloadPage
from src.services.excel_service.read_excel import read_excel
from src.utils.logger import orient_logger
from src.utils.load_yaml import IS_HEADLESS

async def login_orient(playwright: Playwright, referral_id):
    # Get the pandas dataframes from the Excel file
    portal_name = 'ORIENT INSURANCE PJSC'
    df1, df2 = read_excel('ORIENT INSURANCE PJSC', 'default')

    if df1.empty:
        print("No data found sheet1")
        orient_logger.error("No data found sheet1")
        raise Exception("No data found sheet1")

    if df2.empty:
        print("Empty company data IQ portal - Orient Insurance")
        # orient_logger.error("Empty company data IQ portal - Orient Insurance")
        return

    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    if no_of_categories == 0:
        print("No categories found")
        orient_logger.error("No categories found")
        raise Exception("No categories found")

    cat1 = df2[df2['Category'] == unique_categories_list[0]]
    orient_logger.debug(f"Unique categories: {unique_categories_list}")

    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=IS_HEADLESS, args=args)
    context = await browser.new_context(accept_downloads=True)
    context.set_default_timeout(300000)

    # # Set the cookie to the context
    # await context.add_cookies(orient_cookies)

    page = await context.new_page()

    # Login to the Takaful portal
    # login_page = LoginPage(page)
    # await login_page.login()

    login_page = LoginPage(page)
    login_successful = await login_page.login()
    if not login_successful:
        print("Login failed.........")
        await context.close()
        await browser.close()
        return True

    orient_logger.debug("Login Completed")

    # Fill the process form
    process_page = ProcessPage(page)
    quotation_no = await process_page.fill_process_form(df1, cat1, portal_name)

    orient_logger.debug("Process Form filled Completed")

    # Handle Category A
    if cat1 is not None and not cat1.empty:
        category_1_page = Category1Page(page)
        await category_1_page.fill_category_1(cat1, df2)

        orient_logger.debug("Category 1 filled Completed")

    # Handle Category B
    if no_of_categories > 1:
        category_2_page = Category2Page(page)
        cat2 = df2[df2['Category'] == unique_categories_list[1]]
        await category_2_page.fill_category_2(cat2, df2)

        orient_logger.debug("Category 2 filled Completed")

    # Handle Category C
    if no_of_categories > 2:
        category_3_page = Category3Page(page)
        cat3 = df2[df2['Category'] == unique_categories_list[2]]
        await category_3_page.fill_category_3(cat3)

        orient_logger.debug("Category 3 filled Completed")

    print("All Categories filled")
    # Download the PDF
    download_page = DownloadPage(page)
    return_value = await download_page.download_quotation(quotation_no, unique_categories_list,df2)

    orient_logger.debug("Download Completed")

    # Close the browser context and browser
    await context.close()
    await browser.close()

    orient_logger.debug("IQ Portal Closed")
    return return_value