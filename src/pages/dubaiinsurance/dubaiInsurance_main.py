from patchright.async_api import Playwright
from src.services.excel_service.read_excel import read_excel
import asyncio
import pandas as pd
from src.pages.dubaiinsurance.login import Login
from src.pages.dubaiinsurance.process_page import Process_page
from src.pages.dubaiinsurance.categories.categories1 import Categories1
from src.pages.dubaiinsurance.categories.categories2 import Categories2
from src.pages.dubaiinsurance.categories.categories3 import Categories3

from src.utils.logger import dubaiinsurance_logger as logger
import asyncio

async def login_dubaiInsurance(playwright: Playwright, referral_id):

    df1, df2 = read_excel('DUBAI INSURANCE CO', referral_id)
    portal_name = 'DUBAI INSURANCE CO'


    if df1.empty:
        print("No data found sheet1")
        logger.error("No data found sheet1")
        raise Exception("No data found sheet1")
    
    if df2.empty:
        print("Empty company data NLGIC")
        # logger.error("Empty company data NLGIC")
        return
    
    try:
            # Launch the browser
            args = ["--disable-blink-features=AutomationControlled"]
            browser = await playwright.chromium.launch(headless=False, args=args)
            context = await browser.new_context()
            context.set_default_timeout(60000)
            page = await context.new_page()

            while True:
                # Login and process form
                login = Login(page)
                if (await login.perform_login()):

                    unique_categories_list = sorted(df2['Category'].unique().tolist())
                    no_of_categories = len(unique_categories_list)
                    if no_of_categories == 0:
                        print("No categories found")
                        logger.error("No categories found")
                        raise Exception("No categories found")
                    

                    process_page = Process_page(page, df1, df2)
                    await process_page.fill_company_information(portal_name)

                    
                    logger.debug(f"Unique categories: {unique_categories_list}")

                    # region = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0]).strip()
                    tpa = str(df2['TPA'].values[0])
                    plan = str(df2['Network'].values[0])

                    if no_of_categories == 1:
                        
                        cat1 = df2[df2['Category'] == unique_categories_list[0]]
                        categories1 = Categories1(page, df2, cat1, portal_name)
                        if not await categories1.categories1_information(tpa, plan):
                            logger.error("Failed to process categories1 information")
                            raise Exception("Failed to process categories1 information")
                            return

                    elif no_of_categories == 2:
                        cat2 = df2[df2['Category'] == unique_categories_list[1]]
                        category_2_page = Categories2(page, df2, cat2)
                        if not await category_2_page.categories2_information():
                            logger.error("Failed to process categories2 information")
                            raise Exception("Failed to process categories2 information")
                            return
                        
                    elif no_of_categories == 3:
                        cat3 = df2[df2['Category'] == unique_categories_list[2]]
                        category_3_page = Categories3(page, df2, cat3)
                        if not await category_3_page.categories3_information():
                            logger.error("Failed to process categories3 information")
                            raise Exception("Failed to process categories3 information")
                            return
                            
                    # Wait for completion before closing the browser
                    await asyncio.sleep(1)  # Wait for any pending operations

                    break

    finally:
        # Ensure the browser closes properly
        if browser:
            await browser.close()
            logger.info("Browser closed")
