import asyncio
import os
from src.utils.load_yaml import ADNIC_GENERATED_CENSUS_DIR,MED_SLEEP,MAX_SLEEP
from src.utils.logger import adnic_logger
import datetime
from datetime import datetime
from src.utils.support_functions import screenshot_and_compare, extract_dropdown_values


# process page
# *** This is the standard process page structure for the company portal add all process untill benifis mapping here ***
class MissingFieldException(Exception):
    pass

class ProcessPage:
    def __init__(self, page):
        self.page = page

    async def fill_process_form(self, df1, df2, portal_name=None):



        try:
            try:
                await asyncio.sleep(10)
                await screenshot_and_compare(self.page, "adnic", "ADNIC_1")
            except Exception as e:
                adnic_logger.error(f"An error occurred while taking screenshot: {e}")

            # Check if required values are empty
            required_fields = {
                "Company Name": "Company Name is missing",
                "City": "City is missing",
                "Contatct Person": "Contact Person is missing",
                "Contact  Number": "Contact Number is missing",
                "Email": "Email is missing"
            }
            for field, error_message in required_fields.items():
                if df1[df1['KEY'] == field]['VALUE'].empty:
                    adnic_logger.error(f"Error: {error_message} / required fields missing in ADNIC")
                    raise MissingFieldException(error_message)
                
            # page 2 (company details)
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_CompanyName"]').fill(df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
            await asyncio.sleep(MED_SLEEP)
            
            # buiseness_nature = df1[df1['KEY'] == "Businesss Nature"]['VALUE'].values[0]
            business_nature = str(df2['Business Nature'].iloc[0])
            adnic_logger.debug(f'Business Nature (Before Apply) {business_nature}')
            
            # Extract dropdown values for Business Nature
            region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
            selector = '//*[@id="ContentPlaceHolder1_ddl_buisnessNature"]'
            field_name = "Business Nature"
            await extract_dropdown_values(self.page, region, '', '', field_name, selector, portal_name)
            
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_buisnessNature"]').select_option(business_nature)
            adnic_logger.debug(f'Business Nature (After Apply) {business_nature}')

            await asyncio.sleep(MED_SLEEP)
            city = df1[df1['KEY'] == "City"]['VALUE'].values[0]
            if city == "Sajah":
                city = "Sharjah"
            
            adnic_logger.debug(f'Selected City (Before Apply): {city}')
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_City"]').select_option(city)
            adnic_logger.debug(f'City selected (After Apply): {city}')
            await asyncio.sleep(MED_SLEEP)

            adnic_logger.debug(f'Location (Before Apply): {city}')
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_location"]').fill(city)
            adnic_logger.debug(f'Location (After Apply): {city}')
            await asyncio.sleep(MED_SLEEP)
            
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_contactperson"]').fill(df1[df1['KEY'] == "Contatct Person"]['VALUE'].values[0])
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_ContactNumber"]').fill(str(df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0]))
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator('//*[@id="ContentPlaceHolder1_txt_email"]').fill(df1[df1['KEY'] == "Email"]['VALUE'].values[0])
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_NewRenew"]').select_option(df1[df1['KEY'] == "New-Renew"]['VALUE'].values[0])
            await asyncio.sleep(MED_SLEEP)

            adnic_logger.info("Company details filling completed")
            await self.page.locator('//*[@id="ContentPlaceHolder1_btn_submit"]').click()
            
            try:
                await asyncio.sleep(10)
                await screenshot_and_compare(self.page, "adnic", "ADNIC_2")
            except Exception as e:
                adnic_logger.error(f"An error occurred while taking screenshot: {e}")

            # page 3 (Company Census Upload)
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator('//*[@id="ContentPlaceHolder1_fileUpload_member"]').set_input_files(os.path.join(ADNIC_GENERATED_CENSUS_DIR, "adnic_census.xlsx"), timeout=80000)
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator('//*[@id="ContentPlaceHolder1_but_uploadUpload"]').click()
            adnic_logger.debug("Company Census Uploaded")

            # Check if alert is visible and close it if it is
            try:
                # Wait for a short time to see if the alert appears
                alert_panel = self.page.locator('//*[@id="ContentPlaceHolder1_pnl_Error"]/div')
                is_visible = await alert_panel.is_visible(timeout=5000)  # 5 seconds timeout
                
                if is_visible:
                    adnic_logger.debug("Alert detected, attempting to close it")
                    close_button = self.page.locator('//*[@id="ContentPlaceHolder1_ImageButton1"]')
                    await close_button.click()
                    adnic_logger.debug("Alert closed successfully")
                else:
                    adnic_logger.debug("No alert detected, continuing with execution")
            except Exception as e:
                adnic_logger.warning(f"Error handling alert: {str(e)}")

            adnic_logger.debug("Company Census Uploaded")
            await asyncio.sleep(MAX_SLEEP)
            await self.page.wait_for_load_state('networkidle')

            

            # Selecting options on Do any of the members in the scheme suffer from any illnesses as listed below?
            #Cancers (any type) / Tumors?
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_status01"]').select_option("No")
            await asyncio.sleep(MED_SLEEP)
            #Paralysis / Coma?
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_status02"]').select_option("No")
            await asyncio.sleep(MED_SLEEP)
            #Multiple Sclerosis?
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_status03"]').select_option("No")
            await asyncio.sleep(MED_SLEEP)
            #Currently Admitted in NICU or Other any Current In-Patient Hospitalizations?
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_status04"]').select_option("No")
            await asyncio.sleep(MED_SLEEP)
            #Heart Ailments requiring Coronary Artery Bypass Surgery?
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_status05"]').select_option("No")
            await asyncio.sleep(MED_SLEEP)
            #Organ Failure?
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_status06"]').select_option("No")
            await asyncio.sleep(MED_SLEEP)
            #End Stage Kidney / Lung / Liver Disease
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_status07"]').select_option("No")
            await asyncio.sleep(MED_SLEEP)
            #Aplastic Anemia
            await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_status08"]').select_option("No")
            await asyncio.sleep(MED_SLEEP)


            adnic_logger.info("Do any of the members in the scheme suffer from any illnesses as listed below? selected")
            await self.page.locator('//*[@id="ContentPlaceHolder1_btn_submit"]').click()
            adnic_logger.info("census data submitted")
            await asyncio.sleep(MED_SLEEP)

            # # Policy Start date
            # input_locator = self.page.locator('//*[@id="ContentPlaceHolder1_Txt_pSdate"]')
            # await input_locator.evaluate("element => element.removeAttribute('disabled')")
            # await input_locator.fill("22-Jan-2025")
            # await asyncio.sleep(MED_SLEEP)

            # Policy Start date
            start_date = df1[df1['KEY'] == "Effective from"]['VALUE'].values[0]
            adnic_logger.debug('Policy Start Date given:'+start_date)
            formatted_date = datetime.strptime(start_date, "%m/%d/%Y").strftime("%d-%b-%Y")
            adnic_logger.debug('Formatted Date'+formatted_date)
            input_locator = self.page.locator('//*[@id="ContentPlaceHolder1_Txt_pSdate"]')
            
            await input_locator.evaluate("element => element.removeAttribute('disabled')")
            await input_locator.evaluate("document.getElementById('ContentPlaceHolder1_Txt_pSdate').removeAttribute('readonly')")
            # await input_locator.fill("22-Jan-2025")

            await input_locator.fill(str(formatted_date))
            adnic_logger.debug('Policy staret date filled')
            await asyncio.sleep(MED_SLEEP)

            # Broker Commission - Extract dropdown values first
            region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0] if 'Emirates' in df1['KEY'].values else ''
            broker_selector = '//*[@id="ContentPlaceHolder1_brk_Mar"]'
            field_name = "Broker Commission"
            await extract_dropdown_values(self.page, region, '', '', field_name, broker_selector, portal_name or 'ADNIC')

            # Broker Broker Commission
            broker_margin_value = df2["Broker Commission"].values[0]
            await self.page.locator('//*[@id="ContentPlaceHolder1_brk_Mar"]').select_option(broker_margin_value)
            await asyncio.sleep(MED_SLEEP)
            adnic_logger.info("Broker Commission filled successfully")
            
        except MissingFieldException as e:
            adnic_logger.error(f"Missing required field: {str(e)}")
            print(f"Error: {str(e)}")
            raise

        except Exception as e:
            adnic_logger.error(f"Unexpected error: {str(e)}")
            print(f"Unexpected error: {str(e)}")
            raise
