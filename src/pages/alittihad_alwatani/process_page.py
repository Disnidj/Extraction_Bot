import asyncio
import os
from src.utils.load_yaml import AURA_GENERATED_CENSUS_DIR, MED_SLEEP,MAX_SLEEP
from src.utils.support_functions import extract_region,extract_tpa,extract_network, screenshot_and_compare, extract_dropdown_values
from datetime import datetime
import asyncio
import datetime
from src.utils.logger import alittihad_logger

# process page
# *** This is the standard process page structure for the company portal add all process untill benifis mapping here ***
class MissingFieldException(Exception):
    pass

class ProcessPage:
    def __init__(self, page, df1, df2):
        self.page = page
        self.df1 = df1
        self.df2 = df2

    # Category A
    def get_value_A(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[0])
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            alittihad_logger.error(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            alittihad_logger.error(f"IndexError: No data found in column '{column_name}'.")
            return None
       
# Category B
    def get_value_B(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[1])
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            alittihad_logger.error(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            alittihad_logger.error(f"IndexError: No data found in column '{column_name}'.")
            return None
       
# Category C
    def get_value_C(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[2])
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            alittihad_logger.error(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            alittihad_logger.error(f"IndexError: No data found in column '{column_name}'.")
            return None

    async def fill_process_form(self, df1, cat1, num_categories, portal_name):
        alittihad_logger.info('Create Quote Starting')
        await asyncio.sleep(5)
        # await self.page.locator("img[src='assets/icons/total_quotes.png']").click() 
        await self.page.locator("//div[contains(@class, 'cards') and .//div[text()='Create new quote']]").click() 

        

        alittihad_logger.info('Create Quote Clicked')
        await asyncio.sleep(MAX_SLEEP)


        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "ittihad", "Al_Ittihad_1")
        except Exception as e:
            alittihad_logger.error(f"An error occurred while taking screenshot: {e}")


# # #-------------------------------------------------Company Details-------------------------------------------------#

        #Company Name
        company_name = (df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
        alittihad_logger.debug("Company Name :(Before Apply)" + company_name)
        await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[1]/div[1]/input').fill(company_name)
        await asyncio.sleep(MED_SLEEP)
        alittihad_logger.debug("Company Name :(After Apply)" + company_name)

        #Trade License Number
        trade_licence_number = (df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0])
        print(trade_licence_number) 
        alittihad_logger.debug("Trade License Number :(Before Apply)" + str(trade_licence_number))
        await self.page.locator('//*[@formcontrolname="trade_license_number"]').fill(str(trade_licence_number))
        await asyncio.sleep(MED_SLEEP)
        alittihad_logger.debug("Trade License Number :(After Apply)" + str(trade_licence_number))

        #Email
        email = (df1[df1['KEY'] == "Email"]['VALUE'].values[0])
        alittihad_logger.debug("Email :(Before Apply)" + email)
        await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[2]/div[1]/input').fill(email)
        await asyncio.sleep(MED_SLEEP)
        alittihad_logger.debug("Email :(After Apply)" + email)


        ##Contact Number
        # Extracting Contact Number components
        contact_number = str(df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0])
        print(contact_number)
        alittihad_logger.debug("Contact Number :(Before Apply)" + contact_number)
        number_prefix = contact_number[3:5]  # Extract '54'
        phone_number = contact_number[5:]    # Extract '5079578'       
 
        # Interacting with the dropdown (select element)
        await self.page.locator("select.mob-code").select_option(value=number_prefix)
        #//*[@id="CompanydetailsAcc"]/form/div/div[2]/div[2]/div[2]/select
 
        # Interacting with the textbox (input element)
        await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[2]/div[2]/div[2]/input').fill(phone_number)
        alittihad_logger.debug("Contact Number :(After Apply)" + contact_number)
        await asyncio.sleep(0.5)  

        # Nature of Business: Select dropdown value from Sheet1
        business_nature = (cat1['Business Nature'].values[0])
        print(business_nature)
        alittihad_logger.debug("Industry categories :(Before Apply)" + business_nature)
        
        # Extract dropdown values for Business Nature
        region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
        selector = '//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select'
        field_name = "Business Nature"
        await extract_dropdown_values(self.page, region, '', '', field_name, selector, portal_name)
        
        await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select').select_option(business_nature)
        alittihad_logger.debug("Industry categories :(After Apply)" + business_nature)
        await asyncio.sleep(0.5)  
       
        # CLick Next button
        await self.page.get_by_role("button", name="Next").click()
        alittihad_logger.debug('Click Next')
        await asyncio.sleep(1)


# # #-------------------------------------------------Census-------------------------------------------------#

        # Fill Policy Start Date
        policy_start_date = (df1[df1['KEY'] == "Effective from"]['VALUE'].values[0])
        print(policy_start_date)
        alittihad_logger.debug('Policy Start Date :(Before Apply) '+policy_start_date)
        
        if isinstance(policy_start_date, (datetime.datetime,)):
            try:
                print(type(policy_start_date))
                date_obj = datetime.datetime.strptime(policy_start_date, "%m/%d/%Y")
                policy_start_date = date_obj.strftime("%Y-%m-%d")  # Convert to 'YYYY-MM-DD' format
            except ValueError as e:
                print(f"Date format error: {e}")
                alittihad_logger.error(f"Date format error: {e}")
                policy_start_date = None  # Handle invalid format
                
                
        elif isinstance(policy_start_date, str):
            try:
                # Convert from string (mm/dd/yyyy) to datetime object
                date_obj = datetime.datetime.strptime(policy_start_date, '%m/%d/%Y')
                # date_obj = datetime.datetime.strptime(policy_start_date, '%d/%m/%Y')
               
                # Convert datetime object to 'dd-mm-yyyy' format
                policy_start_date = date_obj.strftime('%Y-%m-%d')

                alittihad_logger.info(f"Policy Start date is : {policy_start_date}")
 
            except ValueError as e:
                alittihad_logger.error(f"Date format error: {e}")
                policy_start_date = None  # Handle incorrect format gracefully
       
        alittihad_logger.debug('Formatted Policy Start Date '+ policy_start_date)
 
        await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[1]/div[1]/input').fill(policy_start_date)
        alittihad_logger.debug('Policy start date :(After Apply) '+policy_start_date)
        await asyncio.sleep(0.5)
 
 
        # policy End Date --> AUTOFILLED
        # Quote options --> AUTOFILLED
 
        # Fill number of categories
        await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[2]/div[2]/select').select_option(str(num_categories))
        alittihad_logger.debug('Number of categories')
        await asyncio.sleep(0.5)
 
        # Enter distributor commission %---> defualt value(10%)
        broker_margin = str(cat1['Broker Commission'].iloc[0])
        broker_margin = str(broker_margin.replace('%', '').strip())
        alittihad_logger.debug(broker_margin)
        await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[3]/div[2]/input').fill(broker_margin)
        alittihad_logger.debug('Enter distributor commission')
 
 
        # Not required to fill 'Sales Agent' feild 
        await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/button').hover()
        await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/button').click()
        alittihad_logger.debug('Click census details')
        await asyncio.sleep(3)

        # Previously Insured
        previous_insured = str(cat1['Previous Insured'].iloc[0]).strip()
        alittihad_logger.debug(f"Previous Insured: {previous_insured}")
 
        if previous_insured == "Yes":
            # Click on the 'Previous Insured' checkbox
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[3]/div[1]/div/div[2]/div').click()
            alittihad_logger.debug("Clicked on Previous Insured checkbox")
            await self.page.wait_for_timeout(2000)  # Better than await asyncio.sleep(2)
 
            # Fill in Previous Insurer (Dropdown)
            previous_insurer = str(cat1['Previous Insurer (Takaful)'].iloc[0]).strip()
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[1]/div[2]/select').select_option(previous_insurer)
            alittihad_logger.debug(f"Selected Previous Insurer: {previous_insurer}")
            await self.page.wait_for_timeout(2000)
 
            # Fill in Policy End Date
            policy_end_date = str(cat1['Policy End Date'].iloc[0]).strip()            
            alittihad_logger.debug(policy_end_date)
            
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

                    alittihad_logger.info(f"Policy End date is : {policy_end_date}")
    
                except ValueError as e:
                    alittihad_logger.error(f"Date format error: {e}")
                    policy_end_date = None  # Handle incorrect format gracefully
        
            alittihad_logger.debug('Formatted Policy End Date '+ policy_end_date)
    
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[2]/div[2]/input').fill(policy_end_date)
            alittihad_logger.debug('Policy End date :(After Apply) '+policy_end_date)
            await asyncio.sleep(0.5)

            try:
                await asyncio.sleep(10)
                await screenshot_and_compare(self.page, "ittihad", "Al_Ittihad_2")
            except Exception as e:
                alittihad_logger.error(f"An error occurred while taking screenshot: {e}")


        #-------------------------------------------------Third Step-------------------------------------------------------

        # Choose Group
        group = 'SME Medical'
        alittihad_logger.debug('Choose Group: (Before Apply)'+group)
        # await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[2]/td[2]/select/').select_option(value="0")
        await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[2]/td[2]/select', value=group)
        # await self.page.locator('.selct-box').nth(0).select_option(value="0")
        # await self.page.locator('.selct-box').nth(0).select_option(value="1")
        alittihad_logger.debug('Choose Group')
        await asyncio.sleep(0.5)  

        ##for 1 category
        if num_categories == 1:
            # Emirates Cat A
            emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
            alittihad_logger.debug('Select Emirate Cat A :(Before Apply)' + emirates)
            print(emirates)
            dropdown_selector='//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select'
            field= 'Region'
            await extract_region(self.page, portal_name, field, dropdown_selector)
            await self.page.select_option(dropdown_selector, value=emirates)
            alittihad_logger.debug('Select Emirate Cat A :(After Apply)' + emirates)
            await asyncio.sleep(3)

            ## TPA for Cat A
            tpa = self.get_value_A("TPA")
            tpa = tpa.rstrip() 
            print(tpa)
            dropdown_selector='//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select'
            field= 'TPA'
            await extract_tpa(self.page, portal_name,emirates, field, dropdown_selector)
            alittihad_logger.debug('Select TPA Cat A :(Before Apply)' + tpa)
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select').select_option(value="0")
            alittihad_logger.debug('Select TPA Cat A :(After Apply)' + tpa)
 
            # Select Plan for Cat A
            plan = self.get_value_A("Network")
            plan = plan.rstrip() 
            print(plan)
            dropdown_selector='//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select'
            field= 'Plan'
            await asyncio.sleep(4)
            await extract_network(self.page, portal_name,emirates,tpa, field, dropdown_selector)
            alittihad_logger.debug('Select plan Cat A :(Before Apply)%' + plan + '%')
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select').select_option(value="0")
            await asyncio.sleep(3)
            alittihad_logger.debug('Select plan Cat A :(After Apply)' + plan)
            print('select plan')

             
        elif num_categories == 2:
            # Emirates Cat A
            emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
            alittihad_logger.debug('Select Emirate Cat A :(Before Apply)' + emirates)
            print(emirates)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select', value=emirates)
            alittihad_logger.debug('Select Emirate Cat A :(After Apply)' + emirates)
            await asyncio.sleep(3)

            # Emirates Cat B
            emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
            print(emirates)
            alittihad_logger.debug('Select Emirate Cat B :(Before Apply)' + emirates)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[3]/select', value=emirates)
            alittihad_logger.debug('Select Emirate Cat B :(After Apply)' + emirates)
            await asyncio.sleep(3)


            ## TPA for Cat A
            tpa = self.get_value_A("TPA")
            tpa = tpa.rstrip() 
            print(tpa)
            alittihad_logger.debug('Select TPA Cat A :(Before Apply)' + tpa)
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select').select_option(value="0")
            alittihad_logger.debug('Select TPA Cat A :(After Apply)' + tpa)

            ## TPA for Cat B
            tpa = self.get_value_B("TPA")
            tpa = tpa.rstrip() 
            print(tpa)
            alittihad_logger.debug('Select TPA Cat B :(Before Apply)' + tpa)
            # await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select', value=tpa)
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select').select_option(value="0")
            alittihad_logger.debug('Select TPA Cat B :(After Apply)' + tpa)

 
            # Select Plan for Cat A
            plan = self.get_value_A("Network")
            plan = plan.rstrip() 
            print(plan)
            alittihad_logger.debug('Select plan Cat A :(Before Apply)%' + plan + '%')
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select').select_option(value="0")
            await asyncio.sleep(3)
            alittihad_logger.debug('Select plan Cat A :(After Apply)' + plan)
            print('select plan')

            # Select Plan for Cat B
            plan = self.get_value_B("Network")
            plan = plan.rstrip() 
            print(plan)
            alittihad_logger.debug('Select plan Cat B :(Before Apply)' + plan)
            # await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select', value=plan)
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select').select_option(value="0")
            await asyncio.sleep(3)
            alittihad_logger.debug('Select plan Cat B :(After Apply)' + plan)
            print('select plan')


        ##for 3 categories
        # elif num_categories == 3:
        if num_categories == 3:

            # Emirates Cat A
            emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
            alittihad_logger.debug('Select Emirate Cat A :(Before Apply)' + emirates)
            print(emirates)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select', value=emirates)
            alittihad_logger.debug('Select Emirate Cat A :(After Apply)' + emirates)
            await asyncio.sleep(3)

            # Emirates Cat B
            emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
            print(emirates)
            alittihad_logger.debug('Select Emirate Cat B :(Before Apply)' + emirates)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[3]/select', value=emirates)
            alittihad_logger.debug('Select Emirate Cat B :(After Apply)' + emirates)
            await asyncio.sleep(3)

            # Emirates Cat C
            emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
            print(emirates)
            alittihad_logger.debug('Select Emirate Cat C :(Before Apply)' + emirates)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[4]/select', value=emirates)
            alittihad_logger.debug('Select Emirate Cat C:(After Apply)' + emirates)
            await asyncio.sleep(3)
 

            ## TPA for Cat A
            tpa = self.get_value_A("TPA")
            tpa = tpa.rstrip() 
            print(tpa)
            alittihad_logger.debug('Select TPA Cat A :(Before Apply)' + tpa)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select', value=tpa)
            alittihad_logger.debug('Select TPA Cat A :(After Apply)' + tpa)
            
            #auto filled TPA in cat b and cat c
            # ## TPA for Cat B
            # tpa = self.get_value_B("TPA")
            # tpa = tpa.rstrip() 
            # print(tpa)
            # alittihad_logger.debug('Select TPA Cat B :(Before Apply)' + tpa)
            # await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select', value=tpa)
            # alittihad_logger.debug('Select TPA Cat B :(After Apply)' + tpa)

            # ## TPA for Cat C
            # tpa = self.get_value_C("TPA")
            # tpa = tpa.rstrip() 
            # print(tpa)
            # alittihad_logger.debug('Select TPA Cat C :(Before Apply)' + tpa)
            # await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[4]/select', value=tpa)
            # alittihad_logger.debug('Select TPA Cat C :(After Apply)' + tpa)
 
            # Select Plan for Cat A
            plan = self.get_value_A("Network")
            plan = plan.rstrip() 
            print(plan)
            alittihad_logger.debug('Select plan Cat A :(Before Apply)%' + plan + '%')
            # await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select').select_option(value=plan)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select', value=plan)
            await asyncio.sleep(3)
            alittihad_logger.debug('Select plan Cat A :(After Apply)' + plan)
            print('select plan')

            # Select Plan for Cat B
            plan = self.get_value_B("Network")
            plan = plan.rstrip() 
            print(plan)
            alittihad_logger.debug('Select plan Cat B :(Before Apply)' + plan)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select', value=plan)
            await asyncio.sleep(3)
            alittihad_logger.debug('Select plan Cat B :(After Apply)' + plan)
            print('select plan')
 

            # Select Plan for Cat C
            plan = self.get_value_C("Network")
            plan = plan.rstrip() 
            print(plan)
            alittihad_logger.debug('Select plan Cat C :(Before Apply)' + plan)
            await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[4]/select', value=plan)
            await asyncio.sleep(3)
            alittihad_logger.debug('Select plan Cat C :(After Apply)' + plan)
            print('select plan')

        # Uplaod Census File
        # await self.page.get_by_text("Upload Template").click()
        alittihad_logger.debug("Upload Template Button clicked")
        file_path = os.path.join(AURA_GENERATED_CENSUS_DIR, 'aura_map.xlsx')
        await self.page.wait_for_load_state('networkidle')
        if previous_insured == "Yes":
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[6]/div[2]/label').set_input_files(file_path)
        elif previous_insured == "No":
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[5]/div[2]/label').set_input_files(file_path)

        alittihad_logger.debug("File Uploaded")
        await asyncio.sleep(10)
        await self.page.wait_for_load_state('networkidle')
       
        if await self.page.locator('//html/body/ngb-modal-window/div/div/div/div[3]/button').is_visible():
            await self.page.locator("//html/body/ngb-modal-window/div/div/div/div[3]/button").click()
            alittihad_logger.debug("Cancel Button Clicked")
 
        # Clicked Proceed Button
        await self.page.get_by_role("button", name="Proceed").hover()
        await self.page.get_by_role("button", name="Proceed").click()
        alittihad_logger.debug("Proceed Button Clicked")
        await asyncio.sleep(10)

        return True