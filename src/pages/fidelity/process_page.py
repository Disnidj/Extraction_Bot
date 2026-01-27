import asyncio
import os
from src.utils.load_yaml import AURA_GENERATED_CENSUS_DIR, MED_SLEEP,MAX_SLEEP
from src.utils.logger import fidelity_logger
from datetime import datetime
import asyncio
import datetime
from src.utils.support_functions import extract_region, extract_tpa, extract_network, screenshot_and_compare, extract_dropdown_values


# process page
# *** This is the standard process page structure for the company portal add all process untill benifis mapping here ***
class MissingFieldException(Exception):
    pass

        
class ProcessPage:
    def __init__(self, page, df1, df2, portal_name):
        self.page = page
        self.df1 = df1
        self.df2 = df2
        self.portal_name = portal_name


    # Category A
    def get_value_A(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[0]).strip()
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            return None
       
# Category B
    def get_value_B(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[1]).strip()
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            return None
       
# Category C
    def get_value_C(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[2]).strip()
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            return None

    async def fill_process_form(self, df1, cat1, num_categories):

        fidelity_logger.debug('Create Quote Starting')
        await self.page.locator("img[src='assets/icons/total_quotes.png']").click()
        # await self.page.get_by_text("Create new quote").click()
        await asyncio.sleep(MAX_SLEEP)

        # # #-------------------------------------------------Company Details-------------------------------------------------#

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "fidelity", "FIDELITY_1")
            await asyncio.sleep(10)
        except Exception as e:
            fidelity_logger.error(f"An error occurred: {e}")
            
        try:  
            #Company Name
            await asyncio.sleep(10)            
            company_name = (df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
            fidelity_logger.debug("Company Name :(Before Apply)" + company_name)
            await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[1]/div[1]/input').fill(company_name)
            await asyncio.sleep(MED_SLEEP)
            fidelity_logger.debug("Company Name :(After Apply)" + company_name)

            #Trade License Number
            trade_licence_number = (df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0])
            print(trade_licence_number) 
            fidelity_logger.debug("Trade License Number :(Before Apply)" + str(trade_licence_number))
            await self.page.locator('//*[@formcontrolname="trade_license_number"]').fill(str(trade_licence_number))
            await asyncio.sleep(MED_SLEEP)
            fidelity_logger.debug("Trade License Number :(After Apply)" + str(trade_licence_number))

            #Email
            email = (df1[df1['KEY'] == "Email"]['VALUE'].values[0])
            fidelity_logger.debug("Email :(Before Apply)" + email)
            await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[2]/div[1]/input').fill(email)
            await asyncio.sleep(MED_SLEEP)
            fidelity_logger.debug("Email :(After Apply)" + email)

            ##Contact Number
            # Extracting Contact Number components
            contact_number = str(df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0])
            print(contact_number)
            fidelity_logger.debug("Contact Number :(Before Apply)" + contact_number)
            number_prefix = contact_number[3:5]  # Extract '54'
            phone_number = contact_number[5:]    # Extract '5079578'       

            # Interacting with the dropdown (select element)
            await self.page.locator("select.mob-code").select_option(value=number_prefix)
            #//*[@id="CompanydetailsAcc"]/form/div/div[2]/div[2]/div[2]/select

            # Interacting with the textbox (input element)
            await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[2]/div[2]/div[2]/input').fill(phone_number)
            fidelity_logger.debug("Contact Number :(After Apply)" + contact_number)
            await asyncio.sleep(0.5)  

            # Nature of Business: Select dropdown value from Sheet1
            business_nature = (cat1['Business Nature'].values[0])
            print(business_nature)
            fidelity_logger.debug("Industry categories :(Before Apply)" + business_nature)
            
            # # Click on Business Nature dropdown first to open it
            # await self.page.get_by_role("combobox").nth(1).click()
            # await asyncio.sleep(0.1)
            
            # # Extract dropdown values for Business Nature
            # region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
            # selector = 'option'  # Target the dropdown options that appear after clicking
            # field_name = "Business Nature"
            # await extract_dropdown_values(self.page, region, '', '', field_name, selector, self.portal_name)

            # Extract dropdown values for Business Nature
            region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
            selector = '//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select'
            field_name = "Business Nature"
            await extract_dropdown_values(self.page, region, '', '', field_name, selector, self.portal_name)
                
            # Now select the business nature value
            # await self.page.get_by_role("combobox").nth(1).select_option("0")
            # fidelity_logger.debug("Industry categories :(After Apply)" + business_nature)
            # await asyncio.sleep(0.5)  
            await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select').select_option(value=business_nature)
            await asyncio.sleep(2)
    
            fidelity_logger.debug('Select Business Nature Cat A :(After Apply) ' + business_nature)

            
            # CLick Next button
            await self.page.get_by_role("button", name="Next").click()
            fidelity_logger.debug('Click Next')
            await asyncio.sleep(1)


# # #-------------------------------------------------Census-------------------------------------------------#

            # Fill Policy Start Date
            policy_start_date = (df1[df1['KEY'] == "Effective from"]['VALUE'].values[0])
            print(policy_start_date)
            fidelity_logger.debug('Policy Start Date :(Before Apply) '+policy_start_date)
            if isinstance(policy_start_date, (datetime.datetime,)):
                try:
                    print(type(policy_start_date))
                    date_obj = datetime.datetime.strptime(policy_start_date, "%m/%d/%Y")
                    policy_start_date = date_obj.strftime("%Y-%m-%d")  # Convert to 'YYYY-MM-DD' format
                except ValueError as e:
                    print(f"Date format error: {e}")
                    policy_start_date = None  # Handle invalid format
            elif isinstance(policy_start_date, str):
                try:
                    # Convert from string (mm/dd/yyyy) to datetime object
                    # date_obj = datetime.datetime.strptime(policy_start_date, '%m/%d/%Y')
                    date_obj = datetime.datetime.strptime(policy_start_date, '%m/%d/%Y')
                   
                    # Convert datetime object to 'dd-mm-yyyy' format
                    policy_start_date = date_obj.strftime('%Y-%m-%d')
 
                except ValueError as e:
                    fidelity_logger.error(f"Date format error: {e}")
                    policy_start_date = None  # Handle incorrect format gracefully
       
            fidelity_logger.debug('Formatted Policy Start Date '+policy_start_date)
 
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[1]/div[1]/input').fill(policy_start_date)
            fidelity_logger.debug('Policy start date :(After Apply) '+policy_start_date)
            await asyncio.sleep(0.5)
 
 
            # policy End Date --> AUTOFILLED
            # Quote options --> AUTOFILLED
 
            # Fill number of categories
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[2]/div[2]/select').select_option(str(num_categories))
            fidelity_logger.debug('Number of categories')
            await asyncio.sleep(0.5)
 
            # Enter distributor commission %---> defualt value(10%)
            broker_margin = str(cat1['Broker Commission'].iloc[0])
            broker_margin = str(broker_margin.replace('%', '').strip())
            fidelity_logger.debug(broker_margin)
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[3]/div[2]/input').fill(broker_margin)
            fidelity_logger.debug("Broker Commission completed")
            await asyncio.sleep(2)
 
            # Not required to fill 'Sales Agent' feild 
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/button').click()
            fidelity_logger.debug('Click census details')
            await asyncio.sleep(3)

            # Previously Insured
 
            previous_insured = str(cat1['Previous Insured'].iloc[0]).strip()
            print("previous", previous_insured)
            fidelity_logger.debug(f"Previous Insured: {previous_insured}")
 
            if previous_insured == "Yes":
                # Click on the 'Previous Insured' checkbox
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[3]/div[1]/div/div[2]/div').click()
                fidelity_logger.debug("Clicked on Previous Insured checkbox")
                await self.page.wait_for_timeout(2000)  # Better than await asyncio.sleep(2)
 
                # Fill in Previous Insurer (Dropdown)
                previous_insurer = str(cat1['Previous Insurer (Takaful)'].iloc[0]).strip()
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[1]/div[2]/select').select_option(previous_insurer)
                fidelity_logger.debug(f"Selected Previous Insurer: {previous_insurer}")
                await self.page.wait_for_timeout(2000)
 
                # Fill in Policy End Date
                policy_end_date = str(cat1['Policy End Date'].iloc[0]).strip()            
                fidelity_logger.debug(policy_end_date)

                if isinstance(policy_end_date, (datetime.datetime,)):
                    try:
                        date_obj = datetime.datetime.strptime(policy_end_date, "%m/%d/%Y")
                        policy_end_date = date_obj.strftime("%Y-%m-%d")  # Convert to 'YYYY-MM-DD' format
                    except ValueError as e:
                        print(f"Date format error: {e}")
                        policy_end_date = None  # Handle invalid format
                elif isinstance(policy_end_date, str):
                    try:
                        # Convert from string (mm/dd/yyyy) to datetime object
                        date_obj = datetime.datetime.strptime(policy_end_date, '%m/%d/%Y')
                        # date_obj = datetime.datetime.strptime(policy_end_date, '%d/%m/%Y')
                    
                        # Convert datetime object to 'dd-mm-yyyy' format
                        policy_end_date = date_obj.strftime('%Y-%m-%d')

                        fidelity_logger.info(f"Policy End date is : {policy_end_date}")
        
                    except ValueError as e:
                        fidelity_logger.error(f"Date format error: {e}")
                        policy_end_date = None  # Handle incorrect format gracefully
            
                fidelity_logger.debug('Formatted Policy End Date '+ policy_end_date)
        
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[2]/div[2]/input').fill(policy_end_date)
                fidelity_logger.debug('Policy End date :(After Apply) '+policy_end_date)
                await asyncio.sleep(0.5)
               
                fidelity_logger.debug("Policy End Date Filled")
                await asyncio.sleep(3)

            try:
                fidelity_logger.debug("Clicked NEXT Button")
                await asyncio.sleep(15)
                await screenshot_and_compare(self.page, "fidelity", "FIDELITY_2")
            except Exception as e:
                fidelity_logger.error(f"An error occurred while taking screenshot: {e}")

            #-------------------------------------------------Third Step-------------------------------------------------------
 
            # Choose Group

            group = self.get_value_A("TPA")
            fidelity_logger.debug('Choose Group: (Before Apply)'+group)
            print('Choose Group: (Before Apply)'+group)


            region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
            selector = '//*[@id="censusDetailsAcc"]/div/form/table/tr[2]/td[2]/select'
            field_name = "Group"  
            await extract_dropdown_values(self.page, region, '', '', field_name, selector, self.portal_name)

            # await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[2]/td[2]/select/').select_option(value="0")
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[2]/td[2]/select', value=group)
            # await self.page.locator('.selct-box').nth(0).select_option(value="0")
            # await self.page.locator('.selct-box').nth(0).select_option(value="1")
            fidelity_logger.debug('Choose Group')
            print("ok")
            await asyncio.sleep(0.5)  

            ##for 1 category
            if num_categories == 1:
                # Emirates Cat A
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                dropdown_selector = '//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select'
                field = 'Region'
                await extract_region(self.page, self.portal_name, field, dropdown_selector)
                fidelity_logger.debug('Select Emirate Cat A :(Before Apply)' + emirates)
                print(emirates)
                await self.page.select_option(dropdown_selector, value=emirates)
                fidelity_logger.debug('Select Emirate Cat A :(After Apply)' + emirates)
                await asyncio.sleep(3)

                ## TPA for Cat A
                tpa = self.get_value_A("Plan Selection")
                tpa = tpa.rstrip()
                dropdown_selector_tpa = '//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select'
                field_tpa = 'TPA'
                await extract_tpa(self.page, self.portal_name, emirates, field_tpa, dropdown_selector_tpa)
                print(tpa)
                fidelity_logger.debug('Select TPA Cat A :(Before Apply)' + tpa)
                await self.page.locator(dropdown_selector_tpa).select_option(value=tpa)
                fidelity_logger.debug('Select TPA Cat A :(After Apply)' + tpa)

                # Select Plan for Cat A
                plan = self.get_value_A("Network")
                plan = plan.rstrip()
                dropdown_selector_plan = '//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select'
                field_plan = 'Plan'
                await asyncio.sleep(3)
                await extract_network(self.page, self.portal_name, emirates, tpa, field_plan, dropdown_selector_plan)
                print(plan)
                fidelity_logger.debug('Select plan Cat A :(Before Apply)%' + plan + '%')
                await self.page.locator(dropdown_selector_plan).select_option(value=plan)
                await asyncio.sleep(3)
                fidelity_logger.debug('Select plan Cat A :(After Apply)' + plan)
                print('select plan')

                 
            elif num_categories == 2:
                # Emirates Cat A
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                dropdown_selector_A = '//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select'
                field = 'Region'
                await extract_region(self.page, self.portal_name, field, dropdown_selector_A)
                fidelity_logger.debug('Select Emirate Cat A :(Before Apply)' + emirates)
                await self.page.select_option(dropdown_selector_A, value=emirates)
                fidelity_logger.debug('Select Emirate Cat A :(After Apply)' + emirates)
                await asyncio.sleep(3)

                # Emirates Cat B
                dropdown_selector_B = '//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[3]/select'
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                field = 'Region'
                await extract_region(self.page, self.portal_name, field, dropdown_selector_B)
                fidelity_logger.debug('Select Emirate Cat B :(Before Apply)' + emirates)
                await self.page.select_option(dropdown_selector_B, value=emirates)
                fidelity_logger.debug('Select Emirate Cat B :(After Apply)' + emirates)
                await asyncio.sleep(3)


                ## TPA for Cat A
                tpa_A = self.get_value_A("Plan Selection")
                tpa_A = tpa_A.rstrip()
                dropdown_selector_tpa_A = '//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select'
                field_tpa = 'TPA'
                await extract_tpa(self.page, self.portal_name, emirates, field_tpa, dropdown_selector_tpa_A)
                fidelity_logger.debug('Select TPA Cat A :(Before Apply)' + tpa_A)
                await self.page.locator(dropdown_selector_tpa_A).select_option(value=tpa_A)
                fidelity_logger.debug('Select TPA Cat A :(After Apply)' + tpa_A)

                ## TPA for Cat B
                tpa_B = self.get_value_B("Plan Selection")
                tpa_B = tpa_B.rstrip()
                dropdown_selector_tpa_B = '//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select'
                field_tpa = 'TPA'
                await extract_tpa(self.page, self.portal_name, emirates, field_tpa, dropdown_selector_tpa_B)
                fidelity_logger.debug('Select TPA Cat B :(Before Apply)' + tpa_B)
                await self.page.locator(dropdown_selector_tpa_B).select_option(value=tpa_B)
                fidelity_logger.debug('Select TPA Cat B :(After Apply)' + tpa_B)

                # Select Plan for Cat A
                plan_A = self.get_value_A("Network")
                plan_A = plan_A.rstrip()
                dropdown_selector_plan_A = '//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select'
                field_plan = 'Plan'
                await extract_network(self.page, self.portal_name, emirates, tpa_A, field_plan, dropdown_selector_plan_A)
                fidelity_logger.debug('Select plan Cat A :(Before Apply)%' + plan_A + '%')
                await self.page.locator(dropdown_selector_plan_A).select_option(value=plan_A)
                await asyncio.sleep(3)
                fidelity_logger.debug('Select plan Cat A :(After Apply)' + plan_A)
                print('select plan')

                # Select Plan for Cat B
                plan_B = self.get_value_B("Network")
                plan_B = plan_B.rstrip()
                dropdown_selector_plan_B = '//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select'
                field_plan = 'Plan'
                await extract_network(self.page, self.portal_name, emirates, tpa_B, field_plan, dropdown_selector_plan_B)
                fidelity_logger.debug('Select plan Cat B :(Before Apply)' + plan_B)
                await self.page.locator(dropdown_selector_plan_B).select_option(value=plan_B)
                await asyncio.sleep(3)
                fidelity_logger.debug('Select plan Cat B :(After Apply)' + plan_B)
                print('select plan')

            if num_categories == 3:
                # Emirates Cat A
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                dropdown_selector_A = '//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select'
                field = 'Region'
                await extract_region(self.page, self.portal_name, field, dropdown_selector_A)
                await self.page.select_option(dropdown_selector_A, value=emirates)
                fidelity_logger.debug('Select Emirate Cat A :(After Apply)' + emirates)
                await asyncio.sleep(3)

                # Emirates Cat B
                dropdown_selector_B = '//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[3]/select'
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                field = 'Region'
                await extract_region(self.page, self.portal_name, field, dropdown_selector_B)
                fidelity_logger.debug('Select Emirate Cat B :(Before Apply)' + emirates)
                await self.page.select_option(dropdown_selector_B, value=emirates)
                fidelity_logger.debug('Select Emirate Cat B :(After Apply)' + emirates)
                await asyncio.sleep(3)

                # Emirates Cat C
                dropdown_selector_C = '//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[4]/select'
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                field = 'Region'
                await extract_region(self.page, self.portal_name, field, dropdown_selector_C)
                print(emirates)
                fidelity_logger.debug('Select Emirate Cat C :(Before Apply)' + emirates)
                await self.page.select_option(dropdown_selector_C, value=emirates)
                fidelity_logger.debug('Select Emirate Cat C:(After Apply)' + emirates)
                await asyncio.sleep(3)
 

                ## TPA for Cat A
                tpa_A = self.get_value_A("Plan Selection")
                tpa_A = tpa_A.rstrip()
                dropdown_selector_tpa_A = '//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select'
                field_tpa = 'TPA'
                await extract_tpa(self.page, self.portal_name, emirates, field_tpa, dropdown_selector_tpa_A)
                print(tpa_A)
                fidelity_logger.debug('Select TPA Cat A :(Before Apply)' + tpa_A)
                await self.page.select_option(dropdown_selector_tpa_A, value=tpa_A)
                fidelity_logger.debug('Select TPA Cat A :(After Apply)' + tpa_A)

                ## TPA for Cat B
                tpa_B = self.get_value_B("Plan Selection")
                tpa_B = tpa_B.rstrip()
                dropdown_selector_tpa_B = '//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select'
                field_tpa = 'TPA'
                await extract_tpa(self.page, self.portal_name, emirates, field_tpa, dropdown_selector_tpa_B)
                fidelity_logger.debug('Select TPA Cat B :(Before Apply)' + tpa_B)
                await self.page.locator(dropdown_selector_tpa_B).select_option(value=tpa_B)
                fidelity_logger.debug('Select TPA Cat B :(After Apply)' + tpa_B)

                ## TPA for Cat C
                tpa_C = self.get_value_C("Plan Selection")
                tpa_C = tpa_C.rstrip()
                dropdown_selector_tpa_C = '//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[4]/select'
                field_tpa = 'TPA'
                await extract_tpa(self.page, self.portal_name, emirates, field_tpa, dropdown_selector_tpa_C)
                fidelity_logger.debug('Select TPA Cat C :(Before Apply)' + tpa_C)
                await self.page.locator(dropdown_selector_tpa_C).select_option(value=tpa_C)
                fidelity_logger.debug('Select TPA Cat C :(After Apply)' + tpa_C)
 
                # Select Plan for Cat A
                plan_A = self.get_value_A("Network")
                plan_A = plan_A.rstrip()
                dropdown_selector_plan_A = '//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select'
                field_plan = 'Plan'
                await extract_network(self.page, self.portal_name, emirates, tpa_A, field_plan, dropdown_selector_plan_A)
                fidelity_logger.debug('Select plan Cat A :(Before Apply)%' + plan_A + '%')
                await self.page.locator(dropdown_selector_plan_A).select_option(value=plan_A)
                await asyncio.sleep(3)
                fidelity_logger.debug('Select plan Cat A :(After Apply)' + plan_A)
                print('select plan')

                # Select Plan for Cat B
                plan_B = self.get_value_B("Network")
                plan_B = plan_B.rstrip()
                dropdown_selector_plan_B = '//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select'
                field_plan = 'Plan'
                await extract_network(self.page, self.portal_name, emirates, tpa_B, field_plan, dropdown_selector_plan_B)
                fidelity_logger.debug('Select plan Cat B :(Before Apply)' + plan_B)
                await self.page.locator(dropdown_selector_plan_B).select_option(value=plan_B)
                await asyncio.sleep(3)
                fidelity_logger.debug('Select plan Cat B :(After Apply)' + plan_B)
                print('select plan')

                # Select Plan for Cat C
                plan_C = self.get_value_C("Network")
                plan_C = plan_C.rstrip()
                dropdown_selector_plan_C = '//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[4]/select'
                field_plan = 'Plan'
                await extract_network(self.page, self.portal_name, emirates, tpa_C, field_plan, dropdown_selector_plan_C)
                fidelity_logger.debug('Select plan Cat C :(Before Apply)' + plan_C)
                await self.page.locator(dropdown_selector_plan_C).select_option(value=plan_C)
                await asyncio.sleep(3)
                fidelity_logger.debug('Select plan Cat C :(After Apply)' + plan_C)
                print('select plan')

           # Uplaod Census File
            # await self.page.get_by_text("Upload Template").click()
            fidelity_logger.debug("Upload Template Button clicked")
            file_path = os.path.join(AURA_GENERATED_CENSUS_DIR, 'aura_map.xlsx')
            await self.page.wait_for_load_state('networkidle')
            if previous_insured == "Yes":
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[6]/div[2]/label').set_input_files(file_path)
            elif previous_insured == "No":
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[5]/div[2]/label').set_input_files(file_path)

            fidelity_logger.debug("File Uploaded")
            await asyncio.sleep(10)
            await self.page.wait_for_load_state('networkidle')
            
            if await self.page.locator('//html/body/ngb-modal-window/div/div/div/div[3]/button').is_visible():
                await self.page.locator("//html/body/ngb-modal-window/div/div/div/div[3]/button").click()
                fidelity_logger.debug("Cancel Button Clicked")

            # Clicked Proceed Button
            await self.page.get_by_role("button", name="Proceed").click()
            fidelity_logger.debug("Proceed Button Clicked")
            await asyncio.sleep(10)
        except Exception as e:
            fidelity_logger.error(f"An error occurred: {e}")