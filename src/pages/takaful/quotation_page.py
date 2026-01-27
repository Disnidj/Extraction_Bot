# src/pages/takaful/quotation_page.py
import os
import asyncio
import re
from datetime import datetime
from src.utils.support_functions import extract_region, extract_tpa, extract_network, screenshot_and_compare, extract_dropdown_values
from src.utils.logger import takaful_logger
 
from src.utils.load_yaml import AURA_GENERATED_CENSUS_DIR, BASE_PATH
 
class QuotationPage:
    def __init__(self, page):
        self.page = page
 
    async def create_quotation(self,df1, cat1, cat2, cat3, no_of_categories,portal_name):
        
        # Click to create a new quote
        await self.page.wait_for_load_state('networkidle')
        await self.page.get_by_text("Create new quote").wait_for(state="visible", timeout=60000)
        await self.page.get_by_text("Create new quote").click(timeout=60000)
        await asyncio.sleep(2)
       
        takaful_logger.debug("Create New Quote Button Clicked")

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "takaful", "TAKAFUL_EMARAT_1")
        except Exception as e:
            takaful_logger.error(f"An error occurred while taking screenshot: {e}")
        
        # Fill in the Company Name
        await self.page.get_by_role("textbox").first.click()
        await self.page.get_by_role("textbox").first.fill(df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
        await asyncio.sleep(2)
       
        takaful_logger.debug("Company Name Filled")
 
        # Fill in the Trade License Number
        await self.page.get_by_role("textbox").nth(1).click()
        await self.page.get_by_role("textbox").nth(1).fill(str(df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0]))
        await asyncio.sleep(2)
       
        takaful_logger.debug("Trade License Number Filled")
 
        # Fill in the Email Address
        await self.page.get_by_role("textbox").nth(2).click()
        await self.page.get_by_role("textbox").nth(2).fill(df1[df1['KEY'] == "Email"]['VALUE'].values[0])
        await asyncio.sleep(2)
       
        takaful_logger.debug("Email Address Filled")
 
        #-----------------------------------------------------------------------#
 
        # Fill in the Contact Number
        contact_number = str(df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0])
        number_prefix = contact_number[3:5]  # Extract '54'
        print(number_prefix)
        phone_number = contact_number[5:]    # Extract '5079578'
        print(phone_number)
       
        await self.page.locator("div").filter(has_text=re.compile(r"^\+ 971 50 52 54 56 58$")).get_by_role("combobox").select_option(number_prefix)
        await self.page.locator("div").filter(has_text=re.compile(r"^\+ 971 50 52 54 56 58$")).get_by_role("textbox").fill(phone_number)
        await asyncio.sleep(2)
       
        takaful_logger.debug("Contact Number Filled")
       
        # Businesss Nature
        businesss_nature = str(cat1['Business Nature'].iloc[0]).strip()
        businesss_nature = businesss_nature.rstrip()  # Removing trailing spaces if any
 
        takaful_logger.debug('Select Business Nature Cat A :(Before Apply) ' + businesss_nature)
        
        # Extract dropdown values for Business Nature
        region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
        selector = '//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select'
        field_name = "Business Nature"
        await extract_dropdown_values(self.page, region, '', '', field_name, selector, portal_name)
 
        # Use the retrieved value to select the option in the dropdown
        await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select').select_option(value=businesss_nature)
        await asyncio.sleep(2)
 
        takaful_logger.debug('Select Business Nature Cat A :(After Apply) ' + businesss_nature)
 
        await self.page.get_by_role("button", name="Next").click()
        await asyncio.sleep(2)
       
        takaful_logger.debug("Next Button Clicked")
 
 
#---------------------------------------------------------------------------------------------------------------------------------------#
 
        # Fill the Census and Policy Start Date
        policy_start_date = df1[df1['KEY'] == "Effective from"]['VALUE'].values[0]
        takaful_logger.debug(policy_start_date)
        formatted_date = datetime.strptime(policy_start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        takaful_logger.debug(formatted_date)
 
        await self.page.locator("input[type=\"date\"]").first.fill(formatted_date)
        await asyncio.sleep(0.1)
       
        takaful_logger.debug("Policy Start Date Filled")
        await asyncio.sleep(3)
 
        # Fill the Quote Options
        # await self.page.locator("div").filter(has_text=re.compile(r"^Number of categories \*Select Categories 1 2 3 4 5 6$")).get_by_role("combobox").select_option("1")
        await asyncio.sleep(0.1)
       
        takaful_logger.debug(no_of_categories)
        await self.page.locator("div").filter(has_text=re.compile(r"^Number of categories \*Select Categories 1 2 3 4 5 6$")).get_by_role("combobox").select_option(str(no_of_categories))
        await asyncio.sleep(0.1)
       
        takaful_logger.debug("Number of Categories Filled")
 
        # # Fill the Census
        # Broker Commission
        broker_margin = str(cat1['Broker Commission'].iloc[0]).strip()
        broker_margin = str(broker_margin.replace('%', '').strip())
        takaful_logger.debug(broker_margin)
        await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[3]/div[2]/input').fill(broker_margin)
        takaful_logger.debug("Broker Commission completed")
        await asyncio.sleep(2)

       
        # Previously Insured
 
        previous_insured = str(cat1['Previous Insured'].iloc[0]).strip()
        takaful_logger.debug(f"Previous Insured: {previous_insured}")
 
        if previous_insured == "Yes":
            # Click on the 'Previous Insured' checkbox
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[3]/div[1]/div/div[2]/div').click()
            takaful_logger.debug("Clicked on Previous Insured checkbox")
            await self.page.wait_for_timeout(2000)  # Better than await asyncio.sleep(2)
 
            # Fill in Previous Insurer (Dropdown)
            previous_insurer = str(cat1['Previous Insurer (Takaful)'].iloc[0]).strip()
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[1]/div[2]/select').select_option(previous_insurer)
            takaful_logger.debug(f"Selected Previous Insurer: {previous_insurer}")
            await self.page.wait_for_timeout(2000)
 
            # Fill in Policy End Date
            policy_end_date = str(cat1['Policy End Date'].iloc[0]).strip()            
            takaful_logger.debug(policy_end_date)
            formatted_date = datetime.strptime(policy_end_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            takaful_logger.debug(formatted_date)
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[2]/div[2]/input').fill(formatted_date)
            await asyncio.sleep(2)
           
            takaful_logger.debug("Policy End Date Filled")
            await asyncio.sleep(3)
           
       
        takaful_logger.debug("Clicked NEXT Button")
        await self.page.get_by_label("Census").get_by_role("button", name="Next").hover()
        await self.page.get_by_label("Census").get_by_role("button", name="Next").click()

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "takaful", "TAKAFUL_EMARAT_2")
        except Exception as e:
            takaful_logger.error(f"An error occurred while taking screenshot: {e}")

        # Choose Group
        product_type = str(df1[df1['KEY'] == "Product Type"]['VALUE'].values[0])
        if product_type == "SME":
            product_type = "SME Medical"
        await self.page.wait_for_load_state('networkidle')
        takaful_logger.debug(product_type)
        await self.page.get_by_role("row", name="Group*").get_by_role("combobox").select_option(product_type)
        await asyncio.sleep(2)
 
        #--------------------------------------Category A--------------------------------------#
        async def fill_cat1():
            takaful_logger.debug("Category 1 Started")
 
            # Select option for 'Emirates'
            emirates = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0])
            emirates = emirates.rstrip()
            dropdown_selector='//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select'
            field= 'Region'
            await extract_region(self.page, portal_name, field, dropdown_selector)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select', value=emirates)
            await asyncio.sleep(2)
            takaful_logger.debug("Emirates Filled (Cat 1)  " + emirates)
 
            # Select option for 'TPA'
            tpa = str(cat1['TPA'].iloc[0])
            tpa = tpa.rstrip()
            dropdown_selector='//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select'
            field= 'TPA'
            await extract_tpa(self.page, portal_name,emirates, field, dropdown_selector)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select', value=tpa)
            await asyncio.sleep(10)
            takaful_logger.debug("TPA Filled (Cat 1) "+ tpa)
 
            # Select option for 'Plan'
            plan = str(cat1['Network'].iloc[0])
            plan = plan.rstrip()
            dropdown_selector='//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select'
            field= 'Plan'
            await extract_network(self.page, portal_name, emirates,tpa, field, dropdown_selector)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select', value=plan)
            await asyncio.sleep(2)
            takaful_logger.debug("Plan Filled (Cat 1) "+ plan)
 
        # #--------------------------------------Category B--------------------------------------#
        async def fill_cat2():
 
            takaful_logger.debug("Category 2 Started")
 
            # Select option for 'Emirates'
            emirates = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0])
            emirates = emirates.rstrip()
            takaful_logger.debug("Emirates befor apply" + emirates)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select', value=emirates)
            await asyncio.sleep(2)
            takaful_logger.debug("Emirates Filled (Cat 1)" + emirates)
 
            # Select option for 'Emirates'
            emirates = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0])
            emirates = emirates.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[3]/select', value=emirates)
            await asyncio.sleep(5)
            takaful_logger.debug("Emirates Filled (Cat 2)" + emirates)
 
            # Select option for 'TPA'
            tpa = str(cat1['TPA'].iloc[0])
            tpa = tpa.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select', value=tpa)
            await asyncio.sleep(10)
            takaful_logger.debug("TPA Filled (Cat 1)"+ tpa)
 
            # Select option for 'TPA'
            tpa = str(cat2['TPA'].iloc[0])
            tpa = tpa.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select', value=tpa)
            await asyncio.sleep(2)
            takaful_logger.debug("TPA Filled (Cat 2)"+ tpa)
 
            # Select option for 'Plan'
            plan = str(cat1['Network'].iloc[0])
            plan = plan.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select', value=plan)
            await asyncio.sleep(2)
            takaful_logger.debug("Plan Filled (Cat 1)"+ plan) 
 
            # Select option for 'Plan'
            plan = str(cat2['Network'].iloc[0])
            plan = plan.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select', value=plan)
            await asyncio.sleep(2)
            takaful_logger.debug("Plan Filled (Cat 2)"+ plan)
 
        #--------------------------------------Category C--------------------------------------#
        async def fill_cat3():
            takaful_logger.debug("Category 3 Started")

            # Select option for 'Emirates'
            emirates = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0])
            emirates = emirates.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select', value=emirates)
            await asyncio.sleep(2)
            takaful_logger.debug("Emirates Filled (Cat 1)" + emirates)

            # Select option for 'Emirates'
            emirates = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0])
            emirates = emirates.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[3]/select', value=emirates)
            await asyncio.sleep(5)
            takaful_logger.debug("Emirates Filled (Cat 2)" + emirates)

            # Select option for 'Emirates'
            emirates = str(df1[df1['KEY'] == "Emirates"]["VALUE"].values[0])
            emirates = emirates.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[4]/select', value=emirates)
            await asyncio.sleep(5)
            takaful_logger.debug("Emirates Filled (Cat 3)" + emirates)

            # Select option for 'TPA'
            tpa = str(cat1['TPA'].iloc[0])
            tpa = tpa.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select', value=tpa)
            await asyncio.sleep(10)
            takaful_logger.debug("TPA Filled (Cat 1)"+ tpa)

            # Select option for 'TPA'
            tpa = str(cat2['TPA'].iloc[0])
            tpa = tpa.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select', value=tpa)
            await asyncio.sleep(2)
            takaful_logger.debug("TPA Filled (Cat 2)"+ tpa)

            # Select option for 'TPA'
            tpa = str(cat3['TPA'].iloc[0])
            tpa = tpa.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[4]/select', value=tpa)
            await asyncio.sleep(2)
            takaful_logger.debug("TPA Filled (Cat 3)"+ tpa)

            # Select option for 'Plan'
            plan = str(cat1['Network'].iloc[0])
            plan = plan.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select', value=plan)
            await asyncio.sleep(2)
            takaful_logger.debug("Plan Filled (Cat 1)" + plan)

            # Select option for 'Plan'
            plan = str(cat2['Network'].iloc[0])
            plan = plan.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select', value=plan)
            await asyncio.sleep(2)
            takaful_logger.debug("Plan Filled (Cat 2)" + plan)

            # Select option for 'Plan'
            plan = str(cat3['Network'].iloc[0])
            plan = plan.rstrip()
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[4]/select', value=plan)
            await asyncio.sleep(5)
            takaful_logger.debug("Plan Filled (Cat 3)" + plan)
        if no_of_categories == 1:
            takaful_logger.debug("Cat1")
            await fill_cat1()
        elif no_of_categories == 2:
            takaful_logger.debug("Cat2")
            await fill_cat2()
        else:
            takaful_logger.debug("Cat3")
            await fill_cat3()

        # Uplaod Census File
        # await self.page.get_by_text("Upload Template").click()
        takaful_logger.debug("Upload Template Button clicked")
        file_path = os.path.join(AURA_GENERATED_CENSUS_DIR, 'aura_map.xlsx')
        await self.page.wait_for_load_state('networkidle')
        if previous_insured == "Yes":
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[6]/div[2]/label').set_input_files(file_path)
        elif previous_insured == "No":
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[5]/div[2]/label').set_input_files(file_path)

        takaful_logger.debug("File Uploaded")
        await asyncio.sleep(10)
        await self.page.wait_for_load_state('networkidle')
       
        if await self.page.locator('//html/body/ngb-modal-window/div/div/div/div[3]/button').is_visible():
            await self.page.locator("//html/body/ngb-modal-window/div/div/div/div[3]/button").click()
            takaful_logger.debug("Cancel Button Clicked")
 
        # Clicked Proceed Button
        await self.page.get_by_role("button", name="Proceed").click()
        takaful_logger.debug("Proceed Button Clicked")
        await asyncio.sleep(10)
       
        if await self.page.locator('//html/body/ngb-modal-window/div/div/div/div[3]/button').is_visible():
            await self.page.locator("//html/body/ngb-modal-window/div/div/div/div[3]/button").click()
            takaful_logger.debug("Cancel Button Clicked")
 
        # Clicked Proceed Button
        await self.page.get_by_role("button", name="Proceed").hover()
        await self.page.get_by_role("button", name="Proceed").click()
        takaful_logger.debug("Proceed Button Clicked")
        await asyncio.sleep(10)