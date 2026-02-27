from patchright.async_api import async_playwright
from src.pages.nlg.login_page import LoginPage
from src.pages.nlg.quotation_page import QuotationPage
from src.pages.nlg.process_page import ProcessPage
from src.pages.nlg.categories.category_1_page import Category1Page
from src.pages.nlg.categories.category_2_page import Category2Page
from src.pages.nlg.categories.category_3_page import Category3Page
from src.services.excel_service.read_excel import read_excel
from src.utils.logger import nlg_logger
from src.utils.load_yaml import IS_HEADLESS

async def login_nlg(playwright: async_playwright, referral_id):
    # Get the pandas dataframes from the Excel file
    df1, df2 = read_excel('NLGIC', referral_id)

    if df1.empty:
        print("No data found sheet1")
        nlg_logger.error("No data found sheet1")
        raise Exception("No data found sheet1")
    
    if df2.empty:
        print("Empty company data NLGIC")
        # nlg_logger.error("Empty company data NLGIC")
        return
    
    unique_categories_list = sorted(df2['Category'].unique().tolist())
    no_of_categories = len(unique_categories_list)
    if no_of_categories == 0:
        print("No categories found")
        nlg_logger.error("No categories found")
        raise Exception("No categories found")
    
    
    cat1 = df2[df2['Category'] == unique_categories_list[0]]
    nlg_logger.info(f"Unique categories: {unique_categories_list}")
    nlg_logger.info(f"No of categories: {no_of_categories}")
    
    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=IS_HEADLESS, args=args)
    context = await browser.new_context(accept_downloads=True)
    context.set_default_timeout(60000)
    page = await context.new_page()

    login_page = LoginPage(page)
    login_successful = await login_page.login()
    if not login_successful:
        print("Login failed.........")
        await context.close()
        await browser.close()
        return True
    
    # Fill the process form
    process_page = ProcessPage(page)
    if not await process_page.fill_process_form(df1,cat1):
        nlg_logger.error("Failed to Fill the process form")
        return
    nlg_logger.info("The process form Filled")

    region = str(cat1["Region"].iloc[0]).strip()
    tpa = str(cat1['TPA'].iloc[0]).strip()
    plan = str(cat1['Network'].iloc[0]).strip()
    print(f"Region: {region}, TPA: {tpa}, Plan: {plan}")

    category_1_page = Category1Page(page)
    if not await category_1_page.fill_category_1(df1, cat1, region, tpa, plan):
        nlg_logger.error("Failed to fill Category A")
        return

    nlg_logger.info("Category A Filled")

    if no_of_categories > 1:
        category_2_page = Category2Page(page)
        cat2 = df2[df2['Category'] == unique_categories_list[1]]
        if not await category_2_page.fill_category_2(df2,cat2, region, tpa, plan):
            nlg_logger.error("Failed to fill Category B")
            return

        nlg_logger.info("Category B Filled")
        
    if no_of_categories > 2:
        category_3_page = Category3Page(page)
        cat3 = df2[df2['Category'] == unique_categories_list[2]]
        if not await category_3_page.fill_category_3(cat3):
            nlg_logger.error("Failed to fill Category C")
            return

        nlg_logger.info("Category C Filled")

    await page.get_by_role("button", name="Get Quote").click()

    # download the quotation
    quotation_page = QuotationPage(page)
    if not await quotation_page.download_quotation():
        nlg_logger.error("Failed to download the quotation")
        return

    nlg_logger.info("Quotation download completed")


    # Close the browser context and browser
    await context.close()
    await browser.close()
