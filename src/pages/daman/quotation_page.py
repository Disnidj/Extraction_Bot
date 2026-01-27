import os
import asyncio
import re
from datetime import datetime
from src.pages.daman.categories.category_1_page import Category1Page
from src.pages.daman.categories.category_2_page import Category2Page
from src.pages.daman.categories.category_3_page import Category3Page
from src.utils.logger import daman_logger
from pathlib import Path
from src.utils.support_functions import extract_dropdown_values, screenshot_and_compare
from src.utils.load_yaml import DAMAN_GENERATED_CENSUS_DIR
from src.utils.load_yaml import MAX_SLEEP

class QuotationPage:
    def __init__(self, page):
        self.page = page
    
    async def handle_cookies(self):
        """Handles the cookie consent box by dismissing it if present."""
        try:
            dismiss_cookie_message = await self.page.wait_for_selector(
                '//span[@aria-label="dismiss cookie message" and @class="cc-close cc-close-banner-btn"]',
                timeout=5000  # Wait up to 5 seconds
            )
            await dismiss_cookie_message.click()
            daman_logger.debug("Cookies box dismissed successfully.")
        except Exception as e:
            daman_logger.debug(f"No cookies box found or error dismissing it: {str(e)}")

    async def create_quotation(self, df1, cat1, cat2, cat3, no_of_categories, salary_A, salary_B, salary_C, region, tpa, network, portal_name):
        daman_logger.debug("Navigating to Daman Health Broker Home page.")
        await self.page.goto('https://www.damanhealth.ae/eDamanApp/loadBrokerHome.action?request_locale=en')

        # Handle cookies before proceeding
        await self.handle_cookies()

        daman_logger.debug("Waiting for policy type dropdown.")
        select_dropdown = await self.page.wait_for_selector('//*[@id="dashboard_content_wrap"]/div[1]/div[2]/div/div[1]/select')
        # Extract dropdown values before selecting
        # await extract_dropdown_values(
        #     self.page,
        #     region, 
        #     tpa,
        #     network,
        #     field_name="Policy Type",
        #     dropdown_selector='//*[@id="dashboard_content_wrap"]/div[1]/div[2]/div/div[1]/select',
        #     portal_name=portal_name
        # )
        await select_dropdown.select_option(value='SME')
        await asyncio.sleep(1)

        daman_logger.debug("Clicking 'Generate quote' button.")
        generate_quote_element = await self.page.wait_for_selector('//input[@value="Generate quote"]')
        await generate_quote_element.click()

        daman_logger.debug("Waiting for and clicking 'I Agree' button.")
        accept_button = await self.page.wait_for_selector('//input[contains(@class, "submit-btn solid") and @value="I Agree"]')
        await accept_button.click()
        await self.page.wait_for_timeout(6000)

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "daman", "DAMAN_INSURANCE_1")
            await asyncio.sleep(MAX_SLEEP)
        except Exception as e:
            daman_logger.error(f"An error occurred while marking the checkbox: {e}")
        
        # Filling company name.
        daman_logger.debug("Filling company name")
        await self.page.get_by_role("textbox").first.fill(str(df1[df1['KEY'] == "Company Name"]['VALUE'].values[0]))
        daman_logger.debug("Filled company name")
        
        # Fill in the Staff ID
        await self.page.get_by_role("textbox").nth(1).click()
        await self.page.get_by_role("textbox").nth(1).fill(str(df1[df1['KEY'] == "Company CR Number"]['VALUE'].values[0]))
        await asyncio.sleep(0.1)
        
        daman_logger.debug("Staff ID Filled")

        # Fill commission channel selection
        daman_logger.debug("Selecting 'Broker' as the commission channel")
        # Extract dropdown values before selecting
        # await extract_dropdown_values(
        #     self.page,
        #     region,
        #     tpa,
        #     network,
        #     field_name="Commission Channel",
        #     dropdown_selector='#smeQuotationDTO\\.commission',
        #     portal_name=portal_name

        # )
        await self.page.select_option('#smeQuotationDTO\\.commission', value="Broker")
        await asyncio.sleep(0.1)

        
        # Fill industry
        daman_logger.debug("Selecting 'Other' as the industry")
        # Extract dropdown values before selecting
        await extract_dropdown_values(
            self.page,
            region,
            tpa,
            network,
            field_name="Business Nature",
            dropdown_selector='//select[@id="smeIndustry"]',
            portal_name=portal_name
        )
        await self.page.select_option('//select[@id="smeIndustry"]', value="Other")
        await asyncio.sleep(0.1)

        daman_logger.debug("Other selected as industry")

        # Fill the Policy Holder / Org Name 
        await self.page.get_by_role("textbox").nth(2).click()
        await self.page.get_by_role("textbox").nth(2).fill(df1[df1['KEY'] == "Company Name"]['VALUE'].values[0]) 
        await asyncio.sleep(0.1)
        
        daman_logger.debug("The Policy Holder / Org Name filled")

        # Fill the Inception Date 
        await self.page.wait_for_selector('#smeQuotationDTO_inceptionDateStr', timeout=5000)
        await self.page.click('#smeQuotationDTO_inceptionDateStr')
        date_value = df1[df1['KEY'] == "Effective from"]['VALUE'].values[0]
        # date_value = "28/02/2025"
        daman_logger.debug(f"filled date: {date_value}")
        await self.page.evaluate(f"document.querySelector('#smeQuotationDTO_inceptionDateStr').value = '{date_value}';")
        await self.page.evaluate("document.querySelector('#smeQuotationDTO_inceptionDateStr').dispatchEvent(new Event('input'));")
        await self.page.click("body")
        await asyncio.sleep(1)

        daman_logger.debug("Date Filled",date_value)
        
        # Log the value
        trade_license_number = str(df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0]) 
        daman_logger.debug(f"Filling in Trade License Number: {trade_license_number}")

        await self.page.wait_for_selector('//*[@id="smeQuotationDTO_tradeLicence"]', timeout=5000)
        await self.page.fill('//*[@id="smeQuotationDTO_tradeLicence"]', trade_license_number) 
        daman_logger.debug(f"Trade License Number: {trade_license_number} Filled.")
        await asyncio.sleep(4)

        # Fill Quotation Period 
        daman_logger.debug("Selecting '1year' as the Quotation Period ")
        # Extract dropdown values before selecting
        # await extract_dropdown_values(
        #     self.page,
        #     region,
        #     tpa,
        #     network,
        #     field_name="Quotation Period",
        #     dropdown_selector='//select[@name="smeQuotationDTO.quotePeriod"]',
        #     portal_name=portal_name
        # )
        await self.page.select_option('//select[@name="smeQuotationDTO.quotePeriod"]', value="1")
        await asyncio.sleep(0.1)

        region = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0]).strip()
        tpa = str(cat1['TPA'].iloc[0]).strip()
        plan = str(cat1['Network'].iloc[0]).strip()


        # Handle categories based on the count
        if no_of_categories == 1:
            category_page_01 = Category1Page(self.page)
            if not await category_page_01.fill_category_1(cat1 ,salary_A, region, tpa, plan, portal_name):
                daman_logger.error('Failed to fill Category A')
                return False
            daman_logger.debug("Category A Filled")

        elif no_of_categories == 2:
            category_page_01 = Category1Page(self.page)
            if not await category_page_01.fill_category_1(cat1 ,salary_A, region, tpa, plan, portal_name):
                daman_logger.error('Failed to fill Category A')
                return False
            daman_logger.debug("Category A Filled")
            
            category_page_02 = Category2Page(self.page)
            if not await category_page_02.fill_category_2(cat2, salary_B, region, tpa, plan, portal_name):
                daman_logger.error('Failed to fill Category B')
                return False
            daman_logger.debug("Categories B Filled")

        elif no_of_categories == 3:
            category_page_01 = Category1Page(self.page)
            if not await category_page_01.fill_category_1(cat1 ,salary_A, region, tpa, plan, portal_name):
                daman_logger.error('Failed to fill Category A')
                return False
            daman_logger.debug("Category A Filled")
            
            category_page_02 = Category2Page(self.page)
            if not await category_page_02.fill_category_2(cat2, salary_B, region, tpa, plan, portal_name):
                daman_logger.error('Failed to fill Category B')
                return False
            daman_logger.debug("Categories B Filled")
            
            category_page_03 = Category3Page(self.page)
            if not await category_page_03.fill_category_3(cat3, salary_C, region, tpa, plan, portal_name):
                daman_logger.error('Failed to fill Category C')
                return False
            daman_logger.debug("Categories C Filled")

        daman_logger.debug("Uploading census template file.")
        file_upload = os.path.join(DAMAN_GENERATED_CENSUS_DIR, "daman_census.xlsx")
        await self.page.locator('//label[@id="prev_ins_upload_link"]').set_input_files(file_upload)
        await asyncio.sleep(10)
        daman_logger.debug("Uploaded census template file.")

        daman_logger.debug("Checking required declaration checkboxes.")
        await self.page.wait_for_selector('#decleration', timeout=5000)
        await self.page.locator('#decleration').check()
        await asyncio.sleep(1)

        await self.page.wait_for_selector('#fraudDeclaration', timeout=5000)
        await self.page.locator('#fraudDeclaration').check()
        await asyncio.sleep(1)

        daman_logger.debug("Submitting the quotation form.")
        # await self.page.locator("//div[@class='call-to-actions-container bottom-fixed']//input[@class='submit-btn solid' and @type='button' and @value='Submit']").click()
        await self.page.locator('//input[@value="Submit" and contains(@onclick, "SBT")]').click()
        # await asyncio.sleep(5000)

        # Await the async function
        daman_logger.info("Waiting for quotation reference number.")
        element = await self.page.wait_for_selector("text=Please wait while we generate your quotation with reference", timeout=50000)
        
        # Await the inner_text() call
        text = await element.inner_text()
        daman_logger.debug(f"Extracted Text: {text}")

        match = re.search(r"#\s*(SMEON\d+)", text)
        if match:
            reference_number = match.group(1)
            daman_logger.info(f"Captured Reference Number: {reference_number}")
            
            # Use await when calling async evaluate functions
            await self.page.evaluate(f"sessionStorage.setItem('quotation_ref', '{reference_number}');")
            await self.page.evaluate(f"localStorage.setItem('quotation_ref', '{reference_number}');")
            stored_ref_local = await self.page.evaluate("localStorage.getItem('quotation_ref');")
            daman_logger.info(f"Stored Reference Number in localStorage: {stored_ref_local}")
        else:
            daman_logger.error("Error: Could not extract reference number.")

        # Wait for the button and get the actual element
        back_to_dashboard_button = await self.page.wait_for_selector('//input[@type="button" and @value="BACK TO DASHBOARD"]', state='visible', timeout=5000)

        # Click the button
        await back_to_dashboard_button.click()

        # Wait for navigation
        await self.page.wait_for_timeout(2000)
        daman_logger.info("Successfully navigated back to the dashboard.")

        daman_logger.info("SME quotation process completed successfully.")

        return True