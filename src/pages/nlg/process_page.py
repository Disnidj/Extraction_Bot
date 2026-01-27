import asyncio
import os
from src.utils.load_yaml import NLG_GENERATED_CENSUS_DIR,MED_SLEEP,MAX_SLEEP
from src.utils.support_functions import extract_region,screenshot_and_compare, extract_dropdown_values
from src.utils.logger import nlg_logger

class MissingFieldException(Exception):
    pass

class ProcessPage:
    def __init__(self, page):
        self.page = page

    async def fill_process_form(self, df1, cat1):

         # page 1 (region selection)
        await self.page.locator("#ContentBoady1_btn_sme").hover()
        await self.page.locator("#ContentBoady1_btn_sme").click()

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "nlg", "NLG_1")
        except Exception as e:
            nlg_logger.error(f"Error taking screenshot - {e}")

        # Get the region value from df1
        region_value = str(df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]) if len(df1[df1['KEY'] == "Emirates"]['VALUE'].values) > 0 else "Dubai"
        region_value = region_value.rstrip()
        
        nlg_logger.debug(f"Attempting to select Region: '{region_value}' (Before Apply)")
        
        await asyncio.sleep(MED_SLEEP)
        
        # Extract dropdown values for debugging
        dropdown_selector = "#ContentBoady1_ddl_region"
        field = 'Region'
        portal_name = 'NLGIC'  # or whatever your portal name should be
        await extract_region(self.page, portal_name, field, dropdown_selector)
        
        # Select the region option
        await self.page.locator("#ContentBoady1_ddl_region").select_option(region_value)
        await asyncio.sleep(MED_SLEEP)
        
        # Verify the selection
        try:
            selected_region = await self.page.locator("#ContentBoady1_ddl_region").input_value()
            nlg_logger.debug(f"Region selected: '{selected_region}' (After Apply)")
        except:
            nlg_logger.warning("Could not verify Region selection")
        
        await self.page.get_by_role("button", name="SUBMIT").click()
        nlg_logger.debug("Region selection completed")


        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "nlg", "NLG_2")
        except Exception as e:
            nlg_logger.error(f"Error taking screenshot - {e}")

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
                    nlg_logger.error(f"Error: {error_message} / required fields missing in NLG")
                    raise MissingFieldException(error_message)
                
            # page 2 (company details)
            await asyncio.sleep(MED_SLEEP)
            await self.page.get_by_placeholder("Company Name").fill(df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
            await asyncio.sleep(MED_SLEEP)

            # businesss_nature = str(cat1['Business Nature'].iloc[0])
            # Business Nature dropdown
            # businesss_nature = str(cat1['Business Nature'].iloc[0])
            businesss_nature = 'Other Services & Activities'
            
            nlg_logger.debug(f"Attempting to select Business Nature: '{businesss_nature}' (Before Apply)")
            
            # Extract dropdown values for Business Nature
            region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
            selector = "#ContentBoady1_ddl_buisnessNature"
            field_name = "Business Nature"
            await extract_dropdown_values(self.page, region, '', '', field_name, selector, portal_name)
            
            await self.page.locator("#ContentBoady1_ddl_buisnessNature").select_option(businesss_nature)
            
            # Verify Business Nature selection
            try:
                selected_business_nature = await self.page.locator("#ContentBoady1_ddl_buisnessNature").input_value()
                nlg_logger.debug(f"Business Nature selected: '{selected_business_nature}' (After Apply)")
            except:
                nlg_logger.warning("Could not verify Business Nature selection")
                
            nlg_logger.debug("Business Nature filled")
            await asyncio.sleep(MED_SLEEP)

            # City dropdown
            city_value = "Dubai"
            nlg_logger.debug(f"Attempting to select City: '{city_value}' (Before Apply)")
            
            # Removed extract_dropdown_values for City
            
            await self.page.locator("#ContentBoady1_ddl_City").select_option(city_value)
            
            # Verify City selection
            try:
                selected_city = await self.page.locator("#ContentBoady1_ddl_City").input_value()
                nlg_logger.debug(f"City selected: '{selected_city}' (After Apply)")
            except:
                nlg_logger.warning("Could not verify City selection")

            await asyncio.sleep(MED_SLEEP)
            await self.page.get_by_placeholder("Location").fill(df1[df1['KEY'] == "City"]['VALUE'].values[0])
            await asyncio.sleep(MED_SLEEP)
            await self.page.get_by_placeholder("Contact Person Name").click()
            await asyncio.sleep(MED_SLEEP)
            await self.page.get_by_placeholder("Contact Person Name").fill(df1[df1['KEY'] == "Contatct Person"]['VALUE'].values[0])
            await asyncio.sleep(MED_SLEEP)
            await self.page.get_by_placeholder("Contact Number").fill(str(df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0]))
            await asyncio.sleep(MED_SLEEP)
            await self.page.get_by_placeholder("E-Mail").fill(df1[df1['KEY'] == "Email"]['VALUE'].values[0])
            await asyncio.sleep(MED_SLEEP)

            nlg_logger.debug("Company details filling completed")
            await self.page.get_by_role("button", name="Proceed >>>").click()

            # page 3 (Company Census Upload)
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_fileUpload_member").set_input_files(os.path.join(NLG_GENERATED_CENSUS_DIR, "MemberUpload.xlsx"), timeout=80000)
            await asyncio.sleep(MED_SLEEP)
            await self.page.get_by_role("button", name="Upload").click()
            nlg_logger.debug("Upload button clicked")
            await asyncio.sleep(MAX_SLEEP)
            
            # Check if the alert is visible and close it if it is
            alert_selector = "#ContentBoady1_pnl_Error > div"
            is_alert_visible = await self.page.locator(alert_selector).is_visible()
            
            if is_alert_visible:
                nlg_logger.debug("Alert is visible, attempting to close it")
                # Close the alert by clicking the close button
                await self.page.locator("#ContentBoady1_ImageButton1").click()
                nlg_logger.debug("Alert closed")
                await asyncio.sleep(MED_SLEEP)
            else:
                nlg_logger.debug("No alert detected, continuing with process")
            
            nlg_logger.debug("Company Census Uploaded")
            await asyncio.sleep(MAX_SLEEP)

            # Selecting options on the final page
            await self.page.locator("#ContentBoady1_ddl_above65").select_option("No")
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_ddl_status03").select_option("No")
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_ddl_status04").select_option("No")
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_ddl_status02").select_option("No")
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_ddl_status05").select_option("No")
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_ddl_status01").select_option("No")
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_ddl_status08").select_option("No")
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_ddl_status06").select_option("No")
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_ddl_status07").select_option("No")
            await asyncio.sleep(MED_SLEEP)
            await self.page.locator("#ContentBoady1_ddl_ailment").select_option("No")
            await asyncio.sleep(MED_SLEEP)

            nlg_logger.debug("Final page options selected (No)")
            await self.page.get_by_role("button", name="Next").click()
            nlg_logger.debug("census data submitted")
            return True

        except MissingFieldException as e:
            print(f"Error: {str(e)}")
            nlg_logger.error(f"Error: {str(e)}")
            return False

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            nlg_logger.error(f"Unexpected error: {str(e)}")
            return False
            return False
