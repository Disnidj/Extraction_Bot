import asyncio
import datetime
import asyncio
from datetime import datetime  
import pandas as pd
import os
from src.utils.load_yaml import DUBAIINSURANCE_GENERATED_CENSUS_DIR
from src.utils.logger import dubaiinsurance_logger as logger
from src.utils.special_function_iframe import brocker_margin
from src.utils.support_functions import extract_dropdown_values, extract_region, extract_tpa, extract_network


class Process_page:
    def __init__(self, page, df1, df2):
        self.page = page
        self.df1 = df1
        self.df2 = df2     
        

    def fetch_value(self, key):
        # Fetches the value from df1 where the KEY matches the provided key
        return self.df1[self.df1['KEY'] == key]['VALUE'].iloc[0]
    
    def fetch_value_df2(self, column_name):
        if column_name in self.df2.columns:
            return self.df2[column_name].iloc[0]  # Get first row's value from the given column
        else:
            raise ValueError(f"Column '{column_name}' not found in df2")
    

    async def fill_company_information(self, portal_name):

        print("Filling Company Information")
        logger.info("Filling Company Information")
        await asyncio.sleep(1) 
        # Click 'SME' button
        await self.page.frame_locator("#MyIframe1").locator('//*[@id="ImageButton1"]').click()

        logger.info("Clicked SME Quotation button")

        # Fill Home page details
        await self.page.frame_locator("#MyIframe1").locator("#txt_CompanyName").click()
        company_name = self.fetch_value("Company Name")
        print(f"Company Name: {company_name}")
        logger.debug(f"Company Name: {company_name}")

        await self.page.frame_locator("#MyIframe1").locator("#txt_CompanyName").fill(company_name)
        await asyncio.sleep(1) 

        businesss_nature = str(self.df2['Business Nature'].iloc[0])
        print(f"Business Nature: {businesss_nature}")
        logger.debug(f"Business Nature: {businesss_nature}")
        
        # Extract dropdown values for Business Nature
        region = self.fetch_value("Emirates")
        selector = "#ddl_buisnessNature"
        field_name = "Business Nature"
        try:
            await extract_dropdown_values(self.page.frame_locator("#MyIframe1"), region, '', '', field_name, selector, portal_name)
        except Exception as e:  
            logger.error(f"Error extracting dropdown values for {field_name}: {e}")
        
        logger.debug(f"Business Nature: {businesss_nature}")
        await self.page.frame_locator("#MyIframe1").locator("#ddl_buisnessNature").select_option(businesss_nature)
        await asyncio.sleep(3)  

        city = self.fetch_value("City")
        print(f"city: {city}")
        logger.debug(f"city: {city}")
        await self.page.frame_locator("#MyIframe1").locator("#txt_location").fill(city)
        await asyncio.sleep(2) 
    
        contatct_person = self.fetch_value("Contatct Person")
        print(f"Contact person: {contatct_person}")
        logger.debug(f"Contact person: {contatct_person}")
        await self.page.frame_locator("#MyIframe1").locator("#txt_contactperson").fill(contatct_person)
        await asyncio.sleep(2) 

        contact_number = self.fetch_value("Contact  Number")
        contact_number = str(contact_number) 
        print(f"Contact number: {contact_number}")
        logger.debug(f"Contact number: {contact_number}")
        await self.page.frame_locator("#MyIframe1").locator("#txt_ContactNumber").fill(contact_number)
        await asyncio.sleep(2) 

        email = self.fetch_value("Email")
        print(f"Email: {email}")
        logger.debug(f"Email: {email}")
        await self.page.frame_locator("#MyIframe1").locator("#txt_email").fill(email)
        await asyncio.sleep(2) 

        # Default Value is New
        await self.page.frame_locator("#MyIframe1").locator("#ddl_NewRenew").select_option("New")
        await asyncio.sleep(2) 
        logger.info("Selected New option in (New/Renewal) dropdown")

        # Existing TPA (first occurrence)
        existing_tpa = str(self.df2['Dubai Existing TPA'].iloc[0]) 
        logger.debug(f"Existing TPA (Before Apply): {existing_tpa}")
        
        # Extract dropdown values for Existing TPA
        region = self.fetch_value("Emirates")
        dropdown_selector = "#ddl_tpaben1"
        field_name = "TPA 1"
        try:
            await extract_dropdown_values(self.page.frame_locator("#MyIframe1"),  region, existing_tpa, '', field_name, dropdown_selector, portal_name)
        except Exception as e:
            logger.error(f"Error extracting dropdown values for {field_name}: {e}")
        
        await self.page.frame_locator("#MyIframe1").locator("#ddl_tpaben1").select_option(existing_tpa)
        logger.debug(f"Existing TPA (After Apply): {existing_tpa}")
        await asyncio.sleep(10)

        if existing_tpa == "Others":
            await self.page.frame_locator("#MyIframe1").locator("#txt_expTPA").fill("TPA_NAME")  #here TPA_NAME  is a hardcoded value used for testing

        
        # Click Next button
        await self.page.frame_locator("#MyIframe1").locator("#btn_submit").click()
        await asyncio.sleep(2) 
        logger.info("Clicked next button")

#       ------------------------------------------Upload Member List Page------------------------------------

        file_upload_locator = self.page.frame_locator("#MyIframe1").locator("#fileUpload_member")
        try:
            await asyncio.sleep(2)
            await file_upload_locator.wait_for(state="visible", timeout=15000)
            await file_upload_locator.set_input_files(os.path.join(DUBAIINSURANCE_GENERATED_CENSUS_DIR, "Dubaiinsurance_map.xlsx"))
            print("File uploaded successfully")
            logger.info("File uploaded successfully")
        except TimeoutError as e:
            print(f"Timeout Error: {e}")
            logger.error(f"Timeout Error: {e}")
        except Exception as e:
            print(f"Failed to upload file: {e}")
            logger.error(f"Failed to upload file: {e}")

        # click Upload button
        await self.page.frame_locator("#MyIframe1").locator("#but_uploadUpload").click()
        logger.info("Clicked Upload button")
        # await asyncio.sleep(5)


        # 2. Check visibility of the alert panel
        try:
            # Check if alert panel is visible
            alert_panel = self.page.frame_locator("#MyIframe1").locator('//*[@id="pnl_Error"]/div')
            await asyncio.sleep(5)
            is_alert_visible = await alert_panel.is_visible(timeout=10000)

            # 3. If alert is visible, click close button
            if is_alert_visible:
                logger.info("Alert is visible, clicking close button")
                close_button = self.page.frame_locator("#MyIframe1").locator('//*[@id="ImageButton1"]')
                await close_button.click()
                logger.debug("Clicked close button on alert")
                await asyncio.sleep(3)  # Give time for alert to close
            else:
                logger.debug("No alert detected, continuing with next steps")

            # 4. Run next codes regardless of alert status
            # Click Next button
            await self.page.frame_locator("#MyIframe1").locator("#btn_submit").click()
            logger.debug("Click Next button")
            await asyncio.sleep(3)

        except Exception as e:
            logger.error(f"Error handling alert or next steps: {e}")
            # You might want to add additional error handling here


#       -----------------------------------------TOB Page------------------------------------------------------

        

        effective_from = self.fetch_value("Effective from")
        if isinstance(effective_from, datetime):
            effective_from_str = effective_from.strftime("%A, %B %d, %Y")
        else:
            # If it's not a datetime object, handle or convert here
            effective_from_str = effective_from

        print(f"Effective From: {effective_from_str}")
        logger.debug(f"Effective From: {effective_from_str}")


        input_locator = self.page.frame_locator("#MyIframe1").locator('//*[@id="Txt_pSdate"]')
        await input_locator.evaluate("element => element.removeAttribute('disabled')")
        await input_locator.fill(effective_from_str)
        logger.debug(f"Filled Effective From date: {effective_from_str}")

        await asyncio.sleep(10)


        # TPA (second occurrence in TOB page)
        tpa = str(self.df2['TPA'].iloc[0])
        logger.debug(f"TPA (Before Apply): {tpa}")
        
        # Try first locator
        tpa_locator1 = self.page.frame_locator("#MyIframe1").locator("#ddl_tpaben21")
        tpa_locator2 = self.page.frame_locator("#MyIframe1").locator("#ddl_tpaben1")
        
        # Extract dropdown values for both possible TPA selectors
        field_name = "TPA 2"
        try:
            if await tpa_locator1.is_visible(timeout=2000):
                dropdown_selector = "#ddl_tpaben21"
                # Extract values for first TPA selector
                try:
                    await extract_dropdown_values(self.page.frame_locator("#MyIframe1"), region, tpa, '', field_name, dropdown_selector, portal_name)
                except Exception as e:  
                    logger.error(f"Error extracting dropdown values for TPA (#ddl_tpaben21): {e}")
                
                await tpa_locator1.select_option(tpa)
                await tpa_locator1.press('Enter')
                logger.debug(f"TPA selected from #ddl_tpaben21: {tpa}")
                
            elif await tpa_locator2.is_visible(timeout=2000):
                # Extract values for second TPA selector
                dropdown_selector = "#ddl_tpaben1"
                try:
                    await extract_dropdown_values(self.page.frame_locator("#MyIframe1"), region, tpa, '', field_name, dropdown_selector, portal_name)
                except Exception as e:  
                    logger.error(f"Error extracting dropdown values for TPA (#ddl_tpaben1): {e}")
                
                await tpa_locator2.select_option(tpa)
                await tpa_locator2.press('Enter')
                logger.debug(f"TPA selected from #ddl_tpaben1: {tpa}")
                
            else:
                logger.warning("Neither TPA dropdown was visible")
        except Exception as e:
            logger.error(f"Error selecting TPA: {e}")


        # Fetch and normalize Broker Margin
        broker_margin = self.fetch_value_df2("Broker Commission")

        print(f"Broker Margin: '{broker_margin}'")  # Debugging
        logger.debug(f"Broker Margin: '{broker_margin}'")

        # Select option in dropdown inside iframe
        try:
            await self.page.frame_locator("#MyIframe1").locator("#brk_Mar").select_option(str(broker_margin))
            await self.page.frame_locator("#MyIframe1").locator("#brk_Mar").press('Enter')
            
            print(f"Broker Margin (After Apply): '{broker_margin}'")
            logger.debug(f"Broker Margin (After Apply): '{broker_margin}'")
            logger.debug("Broker Margin selection completed")
            
        except Exception as e:
            logger.error(f"Error occurred while selecting Broker Margin: {e}")
            print(f"Error occurred while selecting Broker Margin: {e}")
            # Optional: Try alternative approach or continue with next steps
            logger.warning("Continuing with next steps despite Broker Margin selection failure")