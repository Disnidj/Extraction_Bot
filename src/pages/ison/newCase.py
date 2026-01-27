import asyncio
import datetime
import asyncio
from datetime import datetime  
import pandas as pd
from src.utils.load_yaml import ISON_GENERATED_CENSUS_DIR,MED_SLEEP,MAX_SLEEP
from src.utils.logger import ison_logger
from src.utils.support_functions import screenshot_and_compare, extract_dropdown_values
import os

class NewCase:
    def __init__(self, page, df1, df2, portal_name=None):
        self.page = page
        self.df1 = df1  
        self.df2 = df2      
        self.portal_name = portal_name      

    def get_value(self, df, key):
        return df[df['KEY'] == key]['VALUE'].values[0]
    

    async def fill_company_information(self):

        # Click 'SME' button
        await asyncio.sleep(0.5) 
        await self.page.get_by_role("button", name="SME").click()
        ison_logger.info("SME button clicked")
        await asyncio.sleep(0.5)

        # Click 'New Quotation' Button
        await self.page.get_by_role("link", name="New Quotation").click()
        ison_logger.info("New Quotation button clicked")
        await asyncio.sleep(0.5)


        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "ison", "ISON_1")
        except Exception as e:
            ison_logger.error(f"An error occurred while taking screenshot: {e}")

        # Fill in the Company Name from Sheet1
        company_name = str(self.get_value(self.df1, "Company Name")).strip()
        ison_logger.info(f'Company Name (Before Apply): {company_name}')
        await self.page.locator("#ContentBoady1_txt_CompanyName").fill(company_name)
        await asyncio.sleep(0.5) 
        ison_logger.info(f"Company Name (After Apply): {company_name}")

        # Business Nature from Sheet1
        business_nature = str(self.df2['Business Nature'].iloc[0]).strip()
        ison_logger.info(f'Business Nature (Before Apply): {business_nature}')
        
        # Extract dropdown values for Business Nature
        region = self.get_value(self.df1, "Emirates")
        selector = "#ContentBoady1_ddl_buisnessNature"
        field_name = "Business Nature"
        await extract_dropdown_values(self.page, region, '', '', field_name, selector, self.portal_name)
        
        await self.page.select_option("#ContentBoady1_ddl_buisnessNature", business_nature)
        await asyncio.sleep(0.5) 
        ison_logger.info("Business Nature (After Apply): {business_nature}")

        # Emirates from Sheet1
        await self.page.locator("#ContentBoady1_ddl_City").select_option("1")
        await asyncio.sleep(0.5) 
        ison_logger.info("Emirates filled")

        # City from Sheet1
        city = str(self.get_value(self.df1,"City")).strip()
        ison_logger.info(f'City (Before Apply): {city}')
        await self.page.locator("#ContentBoady1_txt_location").fill(city)
        await asyncio.sleep(0.5) 
        ison_logger.info(f"City (After Apply): {city}")

        # Contact Person from Sheet1
        contact_person = str(self.get_value(self.df1,"Contatct Person")).strip()
        ison_logger.info(f'Contact Person (Before Apply): {contact_person}')
        await self.page.locator("#ContentBoady1_txt_contactperson").fill(contact_person)
        await asyncio.sleep(0.5) 
        ison_logger.info(f"Contact Person (After Apply): {contact_person}")

        # Contact Number from Sheet1
        contact_number = str(self.get_value(self.df1, "Contact  Number")).strip()
        ison_logger.info(f'Contact Number (Before Apply): {contact_number}')
        await self.page.locator("#ContentBoady1_txt_ContactNumber").fill(contact_number)
        await asyncio.sleep(0.5) 
        ison_logger.info(f"Contact Number (After Apply): {contact_number}")

        # Email from Sheet1
        email = str(self.get_value(self.df1,"Email")).strip()
        ison_logger.info(f'Email (Before Apply): {email}')
        await self.page.locator("#ContentBoady1_txt_email").fill(email)
        await asyncio.sleep(0.5) 
        ison_logger.info(f"Email (After Apply): {email}")

        # Previous Insurance Company Name from Sheet1
        previous_insurance_company = str(self.get_value(self.df1,"Contatct Person")).strip()
        ison_logger.info(f'Previous Insurance Company Name (Before Apply): {previous_insurance_company}')
        await self.page.locator("#ContentBoady1_txt_preInsur").fill(previous_insurance_company)
        await asyncio.sleep(0.5) 
        ison_logger.info(f"Previous Insurance Company Name (After Apply): {previous_insurance_company}")

        # Target Premium Previous Insurance from Sheet1
        # target_premium = str(self.get_value(self.df1,"Target Premium"))
        # print("target premium: " + target_premium)
        # target_premium = int(target_premium)
        # await self.page.locator("#ContentBoady1_txt_targetPrem").fill(target_premium)
        # await asyncio.sleep(0.5) 
        # print("Target premium")

        # New-Renew from Sheet1
        new_renew = str(self.get_value(self.df1,"New-Renew"))
        ison_logger.info(f'New-Renew (Before Apply): {new_renew}')
        await self.page.locator("#ContentBoady1_ddl_NewRenew").select_option(new_renew)
        await asyncio.sleep(0.5) 
        ison_logger.info(f"New-Renew (After Apply): {new_renew}")

        await self.page.locator("#ContentBoady1_btn_submit").click()
        await asyncio.sleep(1) 

        await asyncio.sleep(10) 

        file_upload_locator = self.page.locator("#ContentBoady1_fileUpload_member")
        try:
            await asyncio.sleep(2)
            await file_upload_locator.wait_for(state="visible", timeout=15000)
            await file_upload_locator.set_input_files(os.path.join(ISON_GENERATED_CENSUS_DIR, "ison_map.xlsx"))
            print("File uploaded successfully")
            ison_logger.info("File uploaded successfully")
        except TimeoutError as e:
            print(f"Timeout Error: {e}")
            ison_logger.error(f"Timeout Error: {e}")
        except Exception as e:
            print(f"Failed to upload file: {e}")
            ison_logger.error(f"Failed to upload file: {e}")

        # click Upload button
        await self.page.locator("#ContentBoady1_but_uploadUpload").click()
        await asyncio.sleep(0.5)

        # click Next button
        await self.page.locator("#ContentBoady1_btn_submit").click()

#-------------------------------------------Product Details----------------------------------------        

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "ison", "ISON_2")
        except Exception as e:
            ison_logger.error(f"An error occurred while taking screenshot: {e}")
        
        # Extract the date from the dataframe
        date_value = self.get_value(self.df1, "Effective from")
        ison_logger.info(f'Effective from (Before Apply): {date_value}')
        
        # Check if date_value is already a datetime object
        if isinstance(date_value, datetime):
            date_obj = date_value  # It's already a datetime object
        else:
            # Parse the date string into a datetime object if it's a string
            date_obj = datetime.strptime(date_value, "%m/%d/%Y")
        
        # Format the date into the desired format
        formatted_date = date_obj.strftime("%d-%b-%Y")
        ison_logger.info(f'Effective from (Formatted): {formatted_date}')

    # Wait for the date picker element to be available
        date_input_selector = "#ContentBoady1_Txt_pSdate"
        await asyncio.sleep(5)
        await self.page.wait_for_selector(date_input_selector, timeout=5000)

        # Remove the 'disabled' attribute using JavaScript
        await self.page.evaluate(f"document.querySelector('{date_input_selector}').removeAttribute('disabled');")

        # Fill the date input with the desired date
        await self.page.fill(date_input_selector, formatted_date)

        # Optionally, trigger the 'change' event if needed
        await self.page.evaluate(f"document.querySelector('{date_input_selector}').dispatchEvent(new Event('change'));")

        await asyncio.sleep(4)
        ison_logger.info(f"Effective from (After Apply): {formatted_date}")

