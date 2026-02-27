from patchright.async_api import Playwright
from src.services.excel_service.read_excel import read_excel
import asyncio
import pandas as pd
from src.pages.maxHealth.login import Login
from src.pages.maxHealth.newCase import NewCase
from src.utils.logger import maxhealth_logger 
from src.utils.load_yaml import IS_HEADLESS

async def login_maxHealth(playwright: Playwright, referral_id):

    df1, df2 = read_excel('MaxHealth', referral_id)

    if df1.empty:
        maxhealth_logger.error("No data found sheet1")  # Use logger
        raise Exception("No data found sheet1")
    if df2.empty:
        # maxhealth_logger.error("No data found for MaxHealth")  # Use logger
        return

    # Extract region, tpa, and network from df1/df2
    region = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0]).strip()
    tpa = str(df2['TPA'].iloc[0]).strip()
    network = str(df2['Network'].iloc[0]).strip()

    browser = None  # Define `browser` outside the try block
    try:
            # Launch the browser
            browser = await playwright.chromium.launch(headless=IS_HEADLESS)
            context = await browser.new_context()
            context.set_default_timeout(60000)
            page = await context.new_page()

            # Login and process form
            login = Login(page)
            await login.perform_login(df1)
            
            # Pass region, tpa, network to NewCase
            new_case = NewCase(page, df1, df2, region, tpa, network)
            await new_case.create_new_case(df1) 

            # Wait for completion before closing the browser
            await asyncio.sleep(1)  # Wait for any pending operations

    finally:
        # Ensure the browser closes properly
        if browser:
            await browser.close()

