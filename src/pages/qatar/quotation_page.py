# src/pages/takaful/quotation_page.py
import os
import asyncio
import re
from datetime import datetime
from src.utils.support_functions import extract_region, extract_tpa, extract_network, screenshot_and_compare, extract_dropdown_values
from src.utils.logger import qatar_logger


class QuotationPage:
    def __init__(self, page):
        self.page = page

    async def create_quotation(self,df1,catA, no_of_categories, portal_name=None):
        try :
            # Wait for and click to create a new quote
            await self.page.wait_for_selector("text=Create new quote", timeout=80000)
            await self.page.get_by_text("Create new quote").wait_for(state="visible", timeout=80000)
            await self.page.get_by_text("Create new quote").click()
            await asyncio.sleep(2)
            
            qatar_logger.debug("Create New Quote Button Clicked")

            try:
                await asyncio.sleep(10)
                await screenshot_and_compare(self.page, "qatar", "QATAR_1")
            except Exception as e:
                qatar_logger.error(f"An error occurred while taking screenshot: {e}")
            
            # await self.page.get_by_role("button", name="Okay").click()
            # await asyncio.sleep(0.1)
            
            qatar_logger.debug("Okay Button Clicked")

            # Fill in the Company Name
            
            await self.page.get_by_role("textbox").first.click()
            await self.page.get_by_role("textbox").first.fill(df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
            await asyncio.sleep(0.1)
            
            qatar_logger.debug("Company Name Filled")

            # Fill in the Trade License Number
            await self.page.get_by_role("textbox").nth(1).click()
            await self.page.get_by_role("textbox").nth(1).fill(str(df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0]))
            await asyncio.sleep(0.1)
            
            qatar_logger.debug("Trade License Number Filled")

            # Fill in the Email Address
            await self.page.get_by_role("textbox").nth(2).click()
            await self.page.get_by_role("textbox").nth(2).fill(df1[df1['KEY'] == "Email"]['VALUE'].values[0])
            await asyncio.sleep(0.1)
            
            qatar_logger.debug("Email Address Filled")

            # Extracting Contact Number components
            contact_number = str(df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0])
            number_prefix = contact_number[3:5]  # Extract '54'
            phone_number = contact_number[5:]    # Extract '5079578'

            # Interacting with the dropdown (select element)
            await self.page.locator("select.mob-code").select_option(value=number_prefix)

            # Interacting with the textbox (input element)
            await self.page.locator("input[formcontrolname='mobile_number']").fill(phone_number)
            await asyncio.sleep(0.1)
            
            qatar_logger.debug("Contact Number Filled")

            # Select appropriate Quote options
            # qatar_logger.info(df1[df1['KEY'] == "Businesss Nature"]['VALUE'].values[0])

            business_nature = str(catA['Business Nature'].iloc[0])
            qatar_logger.info(f'Business Nature is {business_nature}')
            
            # Extract dropdown values for Business Nature
            region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
            selector = '//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select'
            field_name = "Business Nature"
            await extract_dropdown_values(self.page, region, '', '', field_name, selector, portal_name)
            
            await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select').select_option(value=business_nature)
            await asyncio.sleep(2)
            
            qatar_logger.debug("Quote Options Filled")
            

            await self.page.get_by_role("button", name="Next").click()
            await asyncio.sleep(0.1)
            
            qatar_logger.debug("Next Button Clicked")

            # Fill the Census and Policy Start Date
            policy_start_date = df1[df1['KEY'] == "Effective from"]['VALUE'].values[0]

            # Ensure policy_start_date is a string
            if isinstance(policy_start_date, datetime):
                policy_start_date = policy_start_date.strftime('%m/%d/%Y')  # Convert to string if it's a datetime object

            formatted_date = datetime.strptime(policy_start_date, '%m/%d/%Y').strftime('%Y-%m-%d')

            await self.page.locator('input[formcontrolname="selected_policy_start_date"]').fill(formatted_date)
            await asyncio.sleep(0.1)

            qatar_logger.debug("Policy Start Date Filled")

            # # Fill the Quote Options if element exists
            # if await self.page.locator("div").filter(has_text=re.compile(r"^Quote optionsSelect Quote Options 1 2 3 4 5$")).count > 0:        
            #     await self.page.locator("div").filter(has_text=re.compile(r"^Quote optionsSelect Quote Options 1 2 3 4 5$")).get_by_role("combobox").select_option("1")
            #     await asyncio.sleep(0.1)
            
            # qatar_logger.debug("Quote Options Filled")

            # Refine locator for "Number of categories" select element
            qatar_logger.info(no_of_categories)

            # Wait for categories dropdown
            categories_selector = '//*[@id="censusDetailsAcc"]/div/form/div[2]/div[2]/select'
            await self.page.wait_for_selector(categories_selector, timeout=60000)
            categories_dropdown = self.page.locator(categories_selector)
            await categories_dropdown.wait_for(state="visible", timeout=60000)
            qatar_logger.info("Select Element Found")
            await asyncio.sleep(2)
            await categories_dropdown.select_option(str(no_of_categories))

            qatar_logger.debug("Number of Categories Filled")
            await asyncio.sleep(0.1)
            
            # # Fill in Commission
            # distributor_commission = str(df1[df1['KEY'] == "Broker Margin"]['VALUE'].values[0]).replace('%', '')
            # qatar_logger.info(distributor_commission)
            # await self.page.fill('input[formcontrolname="distributor_commission"]', distributor_commission)

            broker_margin = str(catA['Broker Commission'].iloc[0]).strip()
            broker_margin = str(broker_margin.replace('%', '').strip())
            qatar_logger.debug(broker_margin)
            
            # Wait for broker commission field
            commission_selector = '//*[@id="censusDetailsAcc"]/div/form/div[3]/div[2]/input'
            await self.page.wait_for_selector(commission_selector, timeout=60000)
            commission_field = self.page.locator(commission_selector)
            await commission_field.wait_for(state="visible", timeout=60000)
            await asyncio.sleep(1)
            await commission_field.fill(broker_margin)
            qatar_logger.debug("Broker Commission completed")
            await asyncio.sleep(2)

            # Previously Insured
 
            previous_insured = str(catA['Previous Insured'].iloc[0]).strip()
            qatar_logger.debug(f"Previous Insured: {previous_insured}")
    
            if previous_insured == "Yes":
                # Click on the 'Previous Insured' checkbox
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[3]/div[1]/div/div[2]/div').click()
                qatar_logger.debug("Clicked on Previous Insured checkbox")
                await self.page.wait_for_timeout(2000)  # Better than await asyncio.sleep(2)
    
                # Fill in Previous Insurer (Dropdown)
                previous_insurer = str(catA['Previous Insurer (Takaful)'].iloc[0]).strip()
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[1]/div[2]/select').select_option(previous_insurer)
                qatar_logger.debug(f"Selected Previous Insurer: {previous_insurer}")
                await self.page.wait_for_timeout(2000)
    
                # Fill in Policy End Date
                policy_end_date = str(catA['Policy End Date'].iloc[0]).strip()            
                qatar_logger.debug(policy_end_date)
                formatted_date = datetime.strptime(policy_end_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                qatar_logger.debug(formatted_date)
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[2]/div[2]/input').fill(formatted_date)
                await asyncio.sleep(2)
            
                qatar_logger.debug("Policy End Date Filled")
                await asyncio.sleep(3)

            # Click the button
            qatar_logger.debug("Clicked NEXT Button")
            await self.page.get_by_label("Census").get_by_role("button", name="Next").click()
            await self.page.wait_for_load_state('networkidle')

            try:
                await asyncio.sleep(10)
                await screenshot_and_compare(self.page, "qatar", "QATAR_2")
            except Exception as e:
                qatar_logger.error(f"An error occurred while taking screenshot: {e}")
            
            # Select option for 'Plans'
            
            TPA_Value = str(catA['TPA'].iloc[0])
            qatar_logger.info("TPA: " + TPA_Value)
            
            # Choose Group
            product_type = str(df1[df1['KEY'] == "Product Type"]['VALUE'].values[0])
            if product_type == "SME":
                product_type = "SME NAS"
            await self.page.wait_for_load_state('networkidle')
            qatar_logger.debug(product_type)
            
            # Wait for the group dropdown to be available
            group_dropdown = self.page.get_by_role("row", name="Group*").get_by_role("combobox")
            await group_dropdown.wait_for(state="visible", timeout=60000)
            await asyncio.sleep(2)
            await group_dropdown.select_option(product_type)
            await asyncio.sleep(2)
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

