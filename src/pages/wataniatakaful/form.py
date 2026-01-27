import asyncio
import datetime
import asyncio
import os
from src.utils.load_yaml import AURA_GENERATED_CENSUS_DIR,MAX_SLEEP,MED_SLEEP
from src.utils.logger import wataniatakaful_logger
from src.utils.support_functions import extract_region, extract_tpa, extract_network, screenshot_and_compare, extract_dropdown_values
class Form:
    def __init__(self, page, df1, df3, portal_name):
        self.page = page
        self.df1 = df1
        self.df3 = df3
        self.portal_name = portal_name

    def get_value(self, df, key):
        return df[df['KEY'] == key]['VALUE'].values[0]

# Category A
    def get_value_A(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df3[column_name].values[0])
        except KeyError:
            wataniatakaful_logger.debug(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            return None
        
# Category B
    def get_value_B(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df3[column_name].values[1])
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
            return str(self.df3[column_name].values[2])
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            return None


    async def fill_company_information(self, num_categories, df1):

        wataniatakaful_logger.debug('Create Quote Starting')
        # await self.page.locator("img[src='assets/icons/total_quotes.png']").click() 
        await self.page.get_by_text("Create new quote").click()
        wataniatakaful_logger.debug('Create Quote Clicked')
        await asyncio.sleep(12)

# # #-------------------------------------------------Company Details-------------------------------------------------#
        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "wataniatakaful", "WATANATAKAFUL_1")
            await asyncio.sleep(10)
        except Exception as e:
            wataniatakaful_logger.error(f"An error occurred while taking screenshot: {e}")
    

        #Company Name
        wataniatakaful_logger.debug("Company Name Starting")
        company_name = (df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
        wataniatakaful_logger.debug("Company Name :(Before Apply)" + company_name)
        await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[1]/div[1]/input').fill(company_name)
        await asyncio.sleep(MED_SLEEP)
        wataniatakaful_logger.debug("Company Name :(After Apply)" + company_name)

        #Trade License Number
        trade_licence_number = (df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0])
        wataniatakaful_logger.debug("Trade License Number :(Before Apply)" + str(trade_licence_number))
        await self.page.locator('//*[@formcontrolname="trade_license_number"]').fill(str(trade_licence_number))
        await asyncio.sleep(MED_SLEEP)
        wataniatakaful_logger.debug("Trade License Number :(After Apply)" + str(trade_licence_number))

        #Email
        email = (df1[df1['KEY'] == "Email"]['VALUE'].values[0])
        wataniatakaful_logger.debug("Email :(Before Apply)" + email)
        await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[2]/div[1]/input').fill(email)
        await asyncio.sleep(MED_SLEEP)
        wataniatakaful_logger.debug("Email :(After Apply)" + email)


        ##Contact Number
        # Extracting Contact Number components
        contact_number = str(df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0])
        wataniatakaful_logger.debug("Contact Number :(Before Apply)" + contact_number)
        number_prefix = contact_number[3:5]  # Extract '54'
        phone_number = contact_number[5:]    # Extract '5079578'       
    
        # Interacting with the dropdown (select element)
        await self.page.locator("select.mob-code").select_option(value=number_prefix)
        await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[2]/div[2]/div[2]/input').fill(phone_number)
        wataniatakaful_logger.debug("Contact Number :(After Apply)" + contact_number)
        await asyncio.sleep(MED_SLEEP)
            
            # wataniatakaful_logger.debug("Businesss Nature")  
            # await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select').select_option(value="0")
            # await asyncio.sleep(MED_SLEEP)
            
            
        #Businesss Nature
        businesss_nature = self.get_value_A("Business Nature")
        businesss_nature = businesss_nature.rstrip()  # Removing trailing spaces if any

        wataniatakaful_logger.debug('Select Business Nature Cat A :(Before Apply) ' + businesss_nature)
            
        # Extract dropdown values for Business Nature
        region = self.get_value_A("Emirates")
        selector = '//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select'
        field_name = "Business Nature"
        await extract_dropdown_values(self.page, region, '', '', field_name, selector, self.portal_name)

        # Use the retrieved value to select the option in the dropdown
        await self.page.locator('//*[@id="CompanydetailsAcc"]/form/div/div[3]/div[1]/select').select_option(value=businesss_nature)

        await asyncio.sleep(MED_SLEEP)

        wataniatakaful_logger.debug('Select Business Nature Cat A :(After Apply) ' + businesss_nature)

            
            
        # CLick Next button
        await self.page.get_by_role("button", name="Next").click()
        wataniatakaful_logger.debug('Click Next')
        await asyncio.sleep(MED_SLEEP)

        # # #-------------------------------------------------Census-------------------------------------------------#

        try:
            # Fill Policy Start Date
            policy_start_date = df1[df1['KEY'] == "Effective from"]['VALUE'].values[0]
            # policy_start_date = '03/26/2025'
            wataniatakaful_logger.debug('Policy Start Date :(Before Apply) ' + str(policy_start_date))

            if isinstance(policy_start_date, (datetime.datetime,)):
                try:
                    print(type(policy_start_date))
                    date_obj = policy_start_date  # If already a datetime object
                    policy_start_date = date_obj.strftime("%Y-%m-%d")  # Convert to 'YYYY-MM-DD'
                except ValueError as e:
                    print(f"Date format error: {e}")
                    policy_start_date = None
            elif isinstance(policy_start_date, str):
                try:
                    # Detect format and parse accordingly
                    if '/' in policy_start_date:
                        if policy_start_date.count('/') == 2:
                            # Determine if MM/DD/YYYY or DD/MM/YYYY
                            month, day, year = map(int, policy_start_date.split('/'))
                            if month > 12:  # If month > 12, it's actually DD/MM/YYYY
                                date_obj = datetime.datetime.strptime(policy_start_date, '%d/%m/%Y')
                            else:  # Otherwise, assume MM/DD/YYYY
                                date_obj = datetime.datetime.strptime(policy_start_date, '%m/%d/%Y')
                            
                            # Convert to 'YYYY-MM-DD' format
                            policy_start_date = date_obj.strftime('%Y-%m-%d')

                except ValueError as e:
                    wataniatakaful_logger.error(f"Date format error: {e}")
                    policy_start_date = None  # Handle incorrect format gracefully

            wataniatakaful_logger.debug('Formatted Policy Start Date ' + str(policy_start_date))

            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[1]/div[1]/input').fill(policy_start_date)
            wataniatakaful_logger.debug('Policy start date :(After Apply) ' + str(policy_start_date))
            await asyncio.sleep(MED_SLEEP)
    
    
            # policy End Date --> AUTOFILLED
            # Quote options --> AUTOFILLED

            # Fill number of categories
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[2]/div[2]/select').select_option(str(num_categories))
            wataniatakaful_logger.debug('Number of categories')
            await asyncio.sleep(MED_SLEEP)
    
            # Enter distributor commission %---> defualt value(10%)
            broker_margin = str(self.df3['Broker Commission'].iloc[0])
            broker_margin = str(broker_margin.replace('%', '').strip())
            wataniatakaful_logger.debug(broker_margin)
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[3]/div[2]/input').fill(broker_margin)
            wataniatakaful_logger.debug("Broker Commission completed")
            await asyncio.sleep(2)
    
            # Not required to fill 'Sales Agent' feild 
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/button').click()
            wataniatakaful_logger.debug('Click census details')
            await asyncio.sleep(MED_SLEEP)

            # Previously Insured
    
            previous_insured = str(self.df3['Previous Insured'].iloc[0]).strip()
            wataniatakaful_logger.debug(f"Previous Insured: {previous_insured}")
    
            if previous_insured == "Yes":
                # Click on the 'Previous Insured' checkbox
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[3]/div[1]/div/div[2]/div').click()
                wataniatakaful_logger.debug("Clicked on Previous Insured checkbox")
                await self.page.wait_for_timeout(2000)  # Better than await asyncio.sleep(2)
    
                # Fill in Previous Insurer (Dropdown)
                previous_insurer = str(self.df3['Previous Insurer (Takaful)'].iloc[0]).strip()
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[1]/div[2]/select').select_option(previous_insurer)
                wataniatakaful_logger.debug(f"Selected Previous Insurer: {previous_insurer}")
                await self.page.wait_for_timeout(2000)
    
                # Fill in Policy End Date
                policy_end_date = str(self.df3['Policy End Date'].iloc[0]).strip()            
                wataniatakaful_logger.debug(policy_end_date)

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

                        wataniatakaful_logger.info(f"Policy End date is : {policy_end_date}")
        
                    except ValueError as e:
                        wataniatakaful_logger.error(f"Date format error: {e}")
                        policy_end_date = None  # Handle incorrect format gracefully
            
                wataniatakaful_logger.debug('Formatted Policy End Date '+ policy_end_date)

                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[4]/div/div[2]/div[2]/input').fill(policy_end_date)
                await asyncio.sleep(2)
            
                wataniatakaful_logger.debug("Policy End Date Filled") 
                await asyncio.sleep(3)

            wataniatakaful_logger.debug("Clicked NEXT Button")
            await asyncio.sleep(10)
            
            try:
                await asyncio.sleep(10)
                await screenshot_and_compare(self.page, "wataniatakaful", "WATANATAKAFUL_2")
            except Exception as e:
                wataniatakaful_logger.error(f"An error occurred while taking screenshot: {e}")
            #-------------------------------------------------Third Step-------------------------------------------------------
    
            # Choose Group---->default value(SME HE)
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[2]/td[2]/select').select_option("2")
            wataniatakaful_logger.debug('Choose Group')
            await asyncio.sleep(MED_SLEEP)

            ##for 1 category
            if num_categories == 1:
                # Emirates Cat A
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                dropdown_selector='//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select'
                field= 'Region'
                await extract_region(self.page, self.portal_name, field, dropdown_selector)
                wataniatakaful_logger.debug('Select Emirate Cat A :(Before Apply)' + emirates)
                await self.page.select_option(dropdown_selector, value=emirates)
                wataniatakaful_logger.debug('Select Emirate Cat A :(After Apply)' + emirates)
                await asyncio.sleep(MED_SLEEP)

                ## TPA for Cat A
                tpa = self.get_value_A("TPA")
                tpa = tpa.rstrip() 
                dropdown_selector='//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select'
                field= 'TPA'
                await extract_tpa(self.page, self.portal_name,emirates, field, dropdown_selector)
                wataniatakaful_logger.debug('Select TPA Cat A :(Before Apply)' + tpa)
                await self.page.select_option(dropdown_selector, value="0")
                await asyncio.sleep(MED_SLEEP)
                wataniatakaful_logger.debug('Select TPA Cat A :(After Apply)' + tpa)
                
                
                # Select Plan for Cat A
                plan = self.get_value_A("TPA")
                plan = plan.rstrip()
                dropdown_selector='//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select'
                field= 'Plan'
                await extract_network(self.page, self.portal_name, emirates,tpa, field, dropdown_selector)
                wataniatakaful_logger.debug('Select plan Cat A :(Before Apply)%' + plan + '%')
                await self.page.select_option(dropdown_selector, value=plan)
                # await self.page.locator(dropdown_selector).select_option(value=plan)
                await asyncio.sleep(MED_SLEEP)
                wataniatakaful_logger.debug('Select plan Cat A :(After Apply)' + plan)

                
            elif num_categories == 2:
                # Emirates Cat A
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                wataniatakaful_logger.debug('Select Emirate Cat A :(Before Apply)' + emirates)
                await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select', value=emirates)
                wataniatakaful_logger.debug('Select Emirate Cat A :(After Apply)' + emirates)
                await asyncio.sleep(MED_SLEEP)

                # Emirates Cat B
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                wataniatakaful_logger.debug('Select Emirate Cat B :(Before Apply)' + emirates)
                await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[3]/select', value=emirates)
                wataniatakaful_logger.debug('Select Emirate Cat B :(After Apply)' + emirates)
                await asyncio.sleep(MED_SLEEP)


                ## TPA for Cat A
                tpa = self.get_value_A("TPA")
                tpa = tpa.rstrip() 
                wataniatakaful_logger.debug('Select TPA Cat A :(Before Apply)' + tpa)
                await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select', value="0")
                wataniatakaful_logger.debug('Select TPA Cat A :(After Apply)' + tpa)

                ## TPA for Cat B
                tpa = self.get_value_B("TPA")
                tpa = tpa.rstrip() 
                wataniatakaful_logger.debug('Select TPA Cat B :(Before Apply)' + tpa)
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select').select_option(value="0")
                wataniatakaful_logger.debug('Select TPA Cat B :(After Apply)' + tpa)

    
                # Select Plan for Cat A
                plan = self.get_value_A("TPA")
                plan = plan.rstrip() 
                wataniatakaful_logger.debug('Select plan Cat A :(Before Apply)%' + plan + '%')
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select').select_option(value=plan)
                await asyncio.sleep(MED_SLEEP)
                wataniatakaful_logger.debug('Select plan Cat A :(After Apply)' + plan)
                print('select plan')

                # Select Plan for Cat B
                plan = self.get_value_B("TPA")
                plan = plan.rstrip() 
                wataniatakaful_logger.debug('Select plan Cat B :(Before Apply)' + plan)
                # await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select', value=plan)
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select').select_option(value=plan)
                await asyncio.sleep(MED_SLEEP)
                wataniatakaful_logger.debug('Select plan Cat B :(After Apply)' + plan)


            ##for 3 categories
            # elif num_categories == 3:
            if num_categories == 3:

                # Emirates Cat A
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                wataniatakaful_logger.debug('Select Emirate Cat A :(Before Apply)' + emirates)
                await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select', value=emirates)
                wataniatakaful_logger.debug('Select Emirate Cat A :(After Apply)' + emirates)
                await asyncio.sleep(MED_SLEEP)

                # Emirates Cat B
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                wataniatakaful_logger.debug('Select Emirate Cat B :(Before Apply)' + emirates)
                await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[3]/select', value=emirates)
                wataniatakaful_logger.debug('Select Emirate Cat B :(After Apply)' + emirates)
                await asyncio.sleep(MED_SLEEP)

                # Emirates Cat C
                emirates = (df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
                wataniatakaful_logger.debug('Select Emirate Cat C :(Before Apply)' + emirates)
                await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[4]/select', value=emirates)
                wataniatakaful_logger.debug('Select Emirate Cat C:(After Apply)' + emirates)
                await asyncio.sleep(MED_SLEEP)

                # TPA for Cat A
                tpa = self.get_value_A("TPA")
                tpa = tpa.rstrip() 
                wataniatakaful_logger.debug('Select TPA Cat A :(Before Apply)' + tpa)
                await self.page.select_option('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select', value="0")
                wataniatakaful_logger.debug('Select TPA Cat A :(After Apply)' + tpa)

                ## TPA for Cat B
                tpa = self.get_value_B("TPA")
                tpa = tpa.rstrip() 
                wataniatakaful_logger.debug('Select TPA Cat B :(Before Apply)' + tpa)
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select').select_option(value="0")
                wataniatakaful_logger.debug('Select TPA Cat B :(After Apply)' + tpa)

                ## TPA for Cat C
                tpa = self.get_value_C("TPA")
                tpa = tpa.rstrip() 
                wataniatakaful_logger.debug('Select TPA Cat B :(Before Apply)' + tpa)
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[4]/select').select_option(value="0")
                wataniatakaful_logger.debug('Select TPA Cat B :(After Apply)' + tpa)

    
                # Select Plan for Cat A
                plan = self.get_value_A("TPA")
                plan = plan.rstrip() 
                wataniatakaful_logger.debug('Select plan Cat A :(Before Apply)%' + plan)
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select').select_option(value=plan)
                await asyncio.sleep(MED_SLEEP)
                wataniatakaful_logger.debug('Select plan Cat A :(After Apply)' + plan)

                # Select Plan for Cat B
                plan = self.get_value_B("TPA")
                plan = plan.rstrip() 
                wataniatakaful_logger.debug('Select plan Cat B :(Before Apply)' + plan)
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select').select_option(value=plan)
                await asyncio.sleep(MED_SLEEP)
                wataniatakaful_logger.debug('Select plan Cat B :(After Apply)' + plan)
                print('select plan')
    

                # Select Plan for Cat C
                plan = self.get_value_C("TPA")
                plan = plan.rstrip() 
                wataniatakaful_logger.debug('Select plan Cat C :(Before Apply)' + plan)
                await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[4]/select').select_option(value=plan)
                await asyncio.sleep(MED_SLEEP)
                wataniatakaful_logger.debug('Select plan Cat C :(After Apply)' + plan)

            # Census file upload          
            census_upload_file_path = os.path.join(AURA_GENERATED_CENSUS_DIR, "aura_map.xlsx")
            file_input_selector = '#fileClass'
            wataniatakaful_logger.debug('Census file upload Starting')
    
            # Upload the file
            await self.page.set_input_files(file_input_selector, census_upload_file_path)
            await asyncio.sleep(MAX_SLEEP)
            wataniatakaful_logger.debug('Census file uploaded')
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(MAX_SLEEP)
    
            # Press TAB button
            await self.page.keyboard.press("Tab")
            await asyncio.sleep(MED_SLEEP)
            await self.page.wait_for_load_state('networkidle')
            wataniatakaful_logger.debug('Tab pressed')
    
            # Press Enter button
            await self.page.keyboard.press("Enter")
            wataniatakaful_logger.debug('Enter pressed')
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(MED_SLEEP)

            # click Upload button
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[8]/button').hover()
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/div[8]/button').click()
            await asyncio.sleep(MAX_SLEEP)
            wataniatakaful_logger.debug('Census file upload completed')
            return True 

        except Exception as e:
            wataniatakaful_logger.error(f"An error occurred: {e}")