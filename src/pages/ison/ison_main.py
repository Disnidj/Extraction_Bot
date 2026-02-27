import asyncio
from patchright.async_api import Playwright
import pandas as pd
from src.pages.ison.login import Login
from src.pages.ison.newCase import NewCase
from src.pages.ison.quatation import DownloadPage
from src.pages.ison.categories.categories1 import Categories1
from src.pages.ison.categories.categories2 import Categories2
from src.pages.ison.categories.categories3 import Categories3
from src.services.excel_service.read_excel import read_excel
from src.utils.logger import ison_logger
from src.utils.load_yaml import IS_HEADLESS

async def login_ison(playwright: Playwright, referral_id):

    # Define portal name
    portal_name = "ISON"
    
    # Get the pandas dataframes from the Excel file
    df1, df2 = read_excel('ISON', referral_id)

    if df1.empty:
        print("No data found sheet1")
        ison_logger.error("No data found sheet1")
        raise Exception("No data found sheet1")
    
    if df2.empty:
        print("Empty company data NLGIC")
        # ison_logger.error("Empty company data NLGIC")
        return
   

    # Extract unique categories
    unique_categories_letters = sorted(df2['Category'].unique().tolist())  
    print(f"Unique categories in letters: {unique_categories_letters}")
    ison_logger.info(f"Unique categories in letters: {unique_categories_letters}")
  

    browser = None 
    # Launch the browser
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(headless=IS_HEADLESS, args=args)
    context = await browser.new_context()
    context.set_default_timeout(60000)
    page = await context.new_page()

    while True:
        login = Login(page)
        if (await login.perform_login()):
                        
            new_case = NewCase(page, df1, df2, portal_name)
            await new_case.fill_company_information()

            # Process categories based on unique categories in letters
            if 'A' in unique_categories_letters:
                cat1 = df2[df2['Category'] == 1]
                categories1 = Categories1(page, df2, cat1)
                if not await categories1.categories1_information(df2):
                    ison_logger.error("Failed to process Category A")
                    return
                ison_logger.info("Category A processed successfully")

            if 'B' in unique_categories_letters:
                cat2 = df2[df2['Category'] == 2]
                categories2 = Categories2(page, df2, cat2)
                if not await categories2.categories2_information(df2):
                    ison_logger.error("Failed to process Category B")
                    return
                ison_logger.info("Category B processed successfully")

            if 'C' in unique_categories_letters:
                cat3 = df2[df2['Category'] == 3]
                categories3 = Categories3(page, df2, cat3)
                if not await categories3.categories3_information():
                    ison_logger.error("Failed to process Category C")
                    return
                ison_logger.info("Category C processed successfully")

            download_quatation = DownloadPage(page)
            await download_quatation.download_quotation()

            await asyncio.sleep(3)

            break

    await context.close()
    await browser.close()

    ison_logger.debug("ISON Insurance Portal Closed")

