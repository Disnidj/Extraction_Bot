import asyncio
import os
from src.utils.load_yaml import SUKOON_GENERATED_CENSUS_DIR,MED_SLEEP,MIN_SLEEP,MAX_SLEEP
from src.utils.logger import sukoon_logger
from datetime import datetime
from src.utils.support_functions import screenshot_and_compare, extract_dropdown_values

class ProcessPage:
    def __init__(self, page):
        self.page = page

    def get_value(self, df, key):
        return df[df['KEY'] == key]['VALUE'].values[0]
    

    async def fill_process_form(self,df1,cat1, portal_name):


        # try:
        #     await asyncio.sleep(10)
        #     await screenshot_and_compare(self.page, "Sukoon", "Sukoon_1")
        # except Exception as e:
        #     sukoon_logger.error(f"An error occurred while taking screenshot: {e}")

        # Click on Create Button
        await self.page.get_by_role("link", name="CREATE", exact=True).click()
        sukoon_logger.debug("Clicked on Create Button")


        # try:
        #     await asyncio.sleep(10)
        #     await screenshot_and_compare(self.page, "Sukoon", "Sukoon_2")
        # except Exception as e:
        #     sukoon_logger.error(f"An error occurred while taking screenshot: {e}")

        # Fill in the Company Name from Sheet1
        await self.page.locator("//input[@id='ContentPlaceHolder1_txtCompanyName']").fill(self.get_value(df1, "Company Name"))
        sukoon_logger.debug(f"Company Name Filled:::{self.get_value(df1, 'Company Name')}")
        await asyncio.sleep(MIN_SLEEP)

        # Nature of Business: Select dropdown value from Sheet2
        business_nature = str(cat1['Business Nature'].iloc[0])
        sukoon_logger.debug(f"Nature of Business:::{business_nature}")
        
        # Extract dropdown values for Nature of Business
        region = self.get_value(df1, 'Emirates')  # Get region from df1
        selector = "#ContentPlaceHolder1_divNatureOfBusiness"
        field_name = "Nature of Business"
        await extract_dropdown_values(self.page, region, '', '', field_name, selector, portal_name)
        
        await self.page.locator("#ContentPlaceHolder1_divNatureOfBusiness").get_by_text("Please Select").first.click()
        await self.page.locator(f"//span[text()='{business_nature}']").click()
        sukoon_logger.debug(f"Nature of Business Filled:::{business_nature}")
        await asyncio.sleep(MIN_SLEEP)


        # Fill other fields like Region from Sheet2
        sukoon_logger.debug(f"Region :::{self.get_value(df1, 'Emirates')}")
        await self.page.locator("#ContentPlaceHolder1_divRegion").get_by_text("Please Select").first.click()
        await self.page.locator(f"//span[text()='{self.get_value(df1, "Emirates")}']").click()
        sukoon_logger.debug(f"Region Filled:::{self.get_value(df1, 'Emirates')}")
        await asyncio.sleep(MIN_SLEEP)

        # Fill Plan Option from Sheet3
        region = self.get_value(df1, 'Product Type')
        sukoon_logger.debug(f"Plan Option :::{region}")
        await self.page.locator("#ContentPlaceHolder1_divProduct").get_by_text("Please Select").first.click()
        await self.page.get_by_role("link", name=self.get_value(df1, "Product Type")).click()
        sukoon_logger.debug(f"Plan Option Filled:::{self.get_value(df1, 'Product Type')}")
        await asyncio.sleep(MIN_SLEEP)

        # Select Is Previous Insured
        previous_insured = str(cat1['Previous Insured'].iloc[0])
        sukoon_logger.debug(f"Is Previous Insured::{previous_insured}")
        await self.page.locator("#ContentPlaceHolder1_divVirgin").get_by_text("Please Select").first.click()

        if previous_insured == "No":
            await self.page.get_by_role("link", name="No", exact=True).nth(4).click()
            sukoon_logger.debug("Is Previous Insured Filled:::No")
            await asyncio.sleep(MIN_SLEEP)

        if previous_insured == "Yes":
            await self.page.get_by_role("link", name="Yes", exact=True).nth(4).click()
            sukoon_logger.debug("Is Previous Insured Filled:::Yes")
            await asyncio.sleep(MIN_SLEEP)

            # Insurer effective date
            insurer_eff_date = str(cat1['Insurer Effective Date'].iloc[0])
            sukoon_logger.debug(f"Insurer Effective Date::{insurer_eff_date}")
            date_obj = datetime.strptime(insurer_eff_date, "%m/%d/%Y")
            # Convert the datetime object to dd/mm/yyyy format
            insurer_eff_date = date_obj.strftime("%d/%m/%Y")
            sukoon_logger.debug("Formatted Effective date: "+insurer_eff_date)
            input_locator = self.page.locator('#ContentPlaceHolder1_txtInceptiondate')
            hidden_input_locator = self.page.locator('#ContentPlaceHolder1_hdnInceptionDate')
            await input_locator.evaluate("el => el.removeAttribute('readonly')")
            await input_locator.fill(insurer_eff_date)
            await hidden_input_locator.evaluate(f"el => el.value = '{insurer_eff_date}'")
            await input_locator.evaluate("el => el.dispatchEvent(new Event('input', { bubbles: true }))")
            await input_locator.evaluate("el => el.dispatchEvent(new Event('change', { bubbles: true }))")
            await self.page.click("body")
            await asyncio.sleep(MED_SLEEP)
            sukoon_logger.debug("Insurer Effective Date Filled:: " + insurer_eff_date)

        

            #Insurer exp date
            insurer_exp_date = str(cat1['Insurer Expiry Date'].iloc[0])
            sukoon_logger.debug(f"Insurer Expiry Date::{insurer_exp_date}")
            date_obj = datetime.strptime(insurer_exp_date, "%m/%d/%Y")
            # Convert the datetime object to dd/mm/yyyy format
            insurer_exp_date = date_obj.strftime("%d/%m/%Y")
            sukoon_logger.debug("Formatted Expiry date: "+insurer_exp_date)
            input_locator = self.page.locator('#ContentPlaceHolder1_txtInsuranceDate')
            hidden_input_locator = self.page.locator('#ContentPlaceHolder1_hdnInsuranceDate')
            await input_locator.evaluate("el => el.removeAttribute('readonly')")
            await input_locator.fill(insurer_exp_date)
            await hidden_input_locator.evaluate(f"el => el.value = '{insurer_exp_date}'")
            await input_locator.evaluate("el => el.dispatchEvent(new Event('input', { bubbles: true }))")
            await input_locator.evaluate("el => el.dispatchEvent(new Event('change', { bubbles: true }))")
            await self.page.click("label[for='nature']")
            # await self.page.locator("body").click() 
            await asyncio.sleep(MED_SLEEP)
            sukoon_logger.debug("Insurer Expiry Date Filled:: " + insurer_exp_date)

            #Previous Insurer
            previous_insurer = str(cat1['Previous Insurer (Sukoon)'].iloc[0])
            sukoon_logger.debug(f"Previous Insurer::{previous_insurer}")
            await self.page.locator("#ContentPlaceHolder1_ddlPreviousInsured").select_option(label=previous_insurer)
            await self.page.locator("#ContentPlaceHolder1_divPreviousInsurer a").click()
            sukoon_logger.debug(f"Previous Insurer Filled:::{previous_insurer}")
            await asyncio.sleep(MIN_SLEEP)
            

            gap_of_coverage = str(cat1['Gap of Coverage'].iloc[0])
            sukoon_logger.debug(f"Gap of Coverage::{gap_of_coverage}")

            if gap_of_coverage == "Yes":
                #Reason
                reason = str(cat1['Reason'].iloc[0])
                sukoon_logger.debug(f"Reason::{reason}")
                await self.page.evaluate("document.getElementById('ContentPlaceHolder1_txtReason').removeAttribute('disabled');")
                await self.page.locator("#ContentPlaceHolder1_txtReason").click()
                await self.page.locator("#ContentPlaceHolder1_txtReason").fill(reason)
                await asyncio.sleep(MIN_SLEEP)



            #Is Dubai Visa
            is_dubai_visa = str(cat1['Is Dubai Visa'].iloc[0])
            sukoon_logger.debug(f"Is Dubai Visa::{is_dubai_visa}")
            await self.page.locator("#ContentPlaceHolder1_ddlIsDubaiVisa").select_option(value=is_dubai_visa)

            sukoon_logger.debug(f"Is Dubai Visa Filled:::{is_dubai_visa}")
            await asyncio.sleep(MIN_SLEEP)

            # await asyncio.sleep(1000)





        await asyncio.sleep(MED_SLEEP)
        # Upload the census file
        sukoon_logger.debug("Setting input files for Census Upload")
        # Ensure the file exists before uploading
        await self.page.locator("#ContentPlaceHolder1_uploadFile").set_input_files(os.path.join(SUKOON_GENERATED_CENSUS_DIR, "sukoon_census.xlsx"))
        sukoon_logger.debug("Uploaded Census")

        await self.page.get_by_role("button", name="Upload").hover()
        await asyncio.sleep(10)
        await screenshot_and_compare(self.page, "Sukoon", "Sukoon_3")

        await self.page.get_by_role("button", name="Upload").click()
        print("Completed Upload Census")
        await asyncio.sleep(MAX_SLEEP)

        print(df1[df1['KEY'] == "Effective from"]['VALUE'].values[0])
 
        # Convert to datetime object
        date_object = datetime.strptime(df1[df1['KEY'] == "Effective from"]['VALUE'].values[0], "%m/%d/%Y")

        # Convert back to string in the desired format
        formatted_date = date_object.strftime("%d/%m/%Y")

        # # Handle Policy Effective Date from Sheet1
        # date_obj = datetime.strptime(str(df1[df1['KEY'] == "Effective from"]['VALUE'].values[0]), "%Y-%m-%d %H:%M:%S")
        # formatted_date = date_obj.strftime("%d/%m/%Y")

        print(formatted_date)



        # Set the value attribute directly using JavaScript
        await self.page.locator("#ContentPlaceHolder1_hdnEffectiveDate").evaluate("(el, date) => el.value = date", formatted_date)
        sukoon_logger.debug(f"Policy Effective Date filled in element using JS:::{formatted_date}")
        await asyncio.sleep(MIN_SLEEP)