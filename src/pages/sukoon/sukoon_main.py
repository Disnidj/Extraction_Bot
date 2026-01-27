from patchright.async_api import Playwright
from src.pages.sukoon.login_page import LoginPage
from src.pages.sukoon.quotation_page import QuotationPage
from src.pages.sukoon.process_page import ProcessPage
from src.pages.sukoon.categories.category_1_page import Category1Page
from src.pages.sukoon.categories.category_2_page import Category2Page
from src.pages.sukoon.categories.category_3_page import Category3Page
from src.services.excel_service.read_excel import read_excel
from src.utils.logger import sukoon_logger
import asyncio

async def login_sukoon(playwright: Playwright, referral_id):
    # Get the pandas dataframes from the Excel file
    df1, df2 = read_excel('SUKOON INSURANCE', referral_id)
    portal_name = 'SUKOON INSURANCE'

    if df1.empty:
        print("No data found sheet1")
        sukoon_logger.error("No data found sheet1")
        raise Exception("No data found sheet1")
    
    if df2.empty:
        print("Empty company data SUKOON INSURANCE")
        # sukoon_logger.error("Empty company data SUKOON INSURANCE")
        return
    
    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    if no_of_categories == 0:
        print("No categories found")
        sukoon_logger.error("No categories found")
        raise Exception("No categories found")
    
    
    cat1 = df2[df2['Category'] == unique_categories_list[0]]
    sukoon_logger.debug(f"Unique categories: {unique_categories_list}")
    
    # Extract company name from df1
    def get_value(df, key):
        return df[df['KEY'] == key]['VALUE'].values[0]
    
    company_name = get_value(df1, 'Company Name')
    sukoon_logger.debug(f"Company Name extracted: {company_name}")
    
    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=False, args=args)
    context = await browser.new_context(accept_downloads=True)
    context.set_default_timeout(60000)
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
    
    # Fill the process form
    process_page = ProcessPage(page)
    await process_page.fill_process_form(df1, cat1, portal_name)

    category_1_page = Category1Page(page, df2, cat1, portal_name)
    await category_1_page.fill_category_1(cat1)

    if no_of_categories > 1:
        cat2 = df2[df2['Category'] == unique_categories_list[1]]
        category_2_page = Category2Page(page, df2, cat2, portal_name)
        await category_2_page.fill_category_2(cat2)
        
    if no_of_categories > 2:
        cat3 = df2[df2['Category'] == unique_categories_list[2]]
        category_3_page = Category3Page(page, df2, cat3, portal_name)
        await category_3_page.fill_category_3(cat3)

    # download the quotation
    quotation_page = QuotationPage(page)
    await quotation_page.download_quotation()


    # Close the browser context and browser
    await context.close()
    await browser.close()