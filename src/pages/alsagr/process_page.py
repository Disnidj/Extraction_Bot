import time
import os
from src.utils.load_yaml import ALSAGR_GENERATED_CENSUS_DIR, MED_SLEEP,MAX_SLEEP
from src.utils.logger import alsagr_logger
from datetime import datetime
from src.utils.support_functions import screenshot_and_compare, extract_dropdown_values


# process page
# *** This is the standard process page structure for the company portal add all process untill benifis mapping here ***
class MissingFieldException(Exception):
    pass

class ProcessPage:
    def __init__(self, page):
        self.page = page

    async def fill_process_form(self, df1, cat1, portal_name=None):

        alsagr_logger.debug("Clicbruebnrm ͜")

        # 1. Click mobile menu button
        await self.page.locator("button.button-menu-mobile").click()
        alsagr_logger.debug("Clicked mobile menu button")
        time.sleep(MAX_SLEEP)

        # 2. Click Medical Portal link
        await self.page.locator('a[href="#sys-295"]').click()
        alsagr_logger.debug("Clicked Medical Portal link")
        time.sleep(MAX_SLEEP)

        # 3. Click SME/Group/EBP B2B link
        await self.page.locator('a[href="#mod-318"]').click()
        alsagr_logger.debug("Clicked SME/Group/EBP B2B link")
        time.sleep(MAX_SLEEP)


        await self.page.locator('(//a[text()="Quotation Information"])[1]').hover()
        try:
            time.sleep(10)
            await screenshot_and_compare(self.page, "alsagr", "ALSAGR_1")
        except Exception as e:
            alsagr_logger.error(f"An error occurred while taking screenshot: {e}")

        # 4. Click Quotation Information
        await self.page.locator('(//a[text()="Quotation Information"])[1]').click()
        alsagr_logger.debug("Clicked Quotation Information link")
        time.sleep(MAX_SLEEP)

        # 5. Click New Quotation button
        await self.page.locator('button[title="Add New Quotation"]').click()
        alsagr_logger.debug("Clicked New Quotation button")
        time.sleep(MAX_SLEEP)
       
        

        # # Uplaod Censuse file
        # file_input_locator = self.page.locator("input[type='file'][accept*='.xlsx']")
        # await file_input_locator.wait_for(state="attached", timeout=10000) 

        # # Set the file
        # await file_input_locator.set_input_files("D:\\AlgoSpring\\python\\MaxHealth\\MaxHealth.xlsx")
        

        # Branch
        try:
            time.sleep(10)
            await screenshot_and_compare(self.page, "alsagr", "ALSAGR_2")
        except Exception as e:
            alsagr_logger.error(f"An error occurred while taking screenshot: {e}")

        await self.page.locator("#CollapseQuoteInformation #branch").select_option("SHEIKH ZAYED")
        alsagr_logger.debug("Selected Branch: SHEIKH ZAYED")
        time.sleep(MAX_SLEEP)
        await self.page.wait_for_load_state('networkidle')

        # Client Type 
        client_type = (df1[df1['KEY'] == "New-Renew"]['VALUE'].values[0])
        alsagr_logger.debug(f"Client Type (Before Apply): {client_type}")
        if client_type == "New":
            await self.page.locator("#client").select_option("New Client")
        else:
            await self.page.locator("#client").select_option("Existing Client")
        alsagr_logger.debug(f"Client Type (After Apply): {client_type}")        
        time.sleep(MED_SLEEP)

        # Product Type
        await self.page.locator("#CollapseQuoteInformation #productType").select_option("SME")
        alsagr_logger.debug("Product Type: SME")
        time.sleep(MED_SLEEP)

        # Click Add Prospect Button
        await self.page.get_by_role("button", name="Add Prospect").click()
        alsagr_logger.debug("Clicked Add Prospect Button")
        time.sleep(MED_SLEEP)

#-------------------------------------------------Insured Information-------------------------------------------------#
        

        try:
            time.sleep(10)
            await screenshot_and_compare(self.page, "alsagr", "ALSAGR_3")
        except Exception as e:
            alsagr_logger.error(f"An error occurred while taking screenshot: {e}")
        # Insured Type
        # insured_type = (df1[df1['KEY'] == "Insured Type"]['VALUE'].values[0]) 
        insured_type = "Government"
        alsagr_logger.debug(f"Insured Type (Before Apply): {insured_type}")
        await self.page.locator("#insuredType").select_option(insured_type)
        alsagr_logger.debug(f"Insured Type (After Apply): {insured_type}")
        time.sleep(MED_SLEEP)
        await self.page.wait_for_load_state('networkidle')

        # Company CR Number
        company_CR_number = (df1[df1['KEY'] == "Company CR Number"]['VALUE'].values[0])
        alsagr_logger.debug(f"Company CR Number (Before Apply): {company_CR_number}")
        await self.page.locator("#companyCRNumber").fill(str(company_CR_number))
        alsagr_logger.debug(f"Company CR Number (After Apply): {company_CR_number}")
        time.sleep(MED_SLEEP)
        await self.page.wait_for_load_state('networkidle')

        # Insured / Company Name
        company_name = (df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
        alsagr_logger.debug(f"Company Name (Before Apply): {company_name}")
        await self.page.locator("#fullName").fill(company_name)
        alsagr_logger.debug(f"Company Name (After Apply): {company_name}")
        time.sleep(MED_SLEEP)
        await self.page.wait_for_load_state('networkidle')

        # Email
        email = (df1[df1['KEY'] == "Email"]['VALUE'].values[0])
        alsagr_logger.debug(f"Email (Before Apply): {email}")
        await self.page.locator("#policyEmail").fill(email)
        alsagr_logger.debug(f"Email (After Apply): {email}")
        time.sleep(MED_SLEEP)
        await self.page.wait_for_load_state('networkidle')

        # Trade License Number
        trade_licence_number = (df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0])
        alsagr_logger.debug(f"Trade License Number (Before Apply): {trade_licence_number}")
        await self.page.locator("#tradeLicenseNo").fill(str(trade_licence_number))
        alsagr_logger.debug(f"Trade License Number (After Apply): {trade_licence_number}")
        time.sleep(MED_SLEEP)

        # Trade License Expiry Date - Change date format parsing to match the Excel format
        trade_licence_ex_date = (df1[df1['KEY'] == "Trade License Expiry Date"]['VALUE'].values[0])
        alsagr_logger.debug(f"Trade License Expiry Date (Before Apply): {trade_licence_ex_date}")
        # Correct format for day/month/year
        formatted_date = datetime.strptime(trade_licence_ex_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        alsagr_logger.debug(f"Trade License Expiry format Date (Before Apply): {formatted_date}")
        await self.page.locator("#tradeLicenseExpiryDate").fill(formatted_date)
        alsagr_logger.debug(f"Trade License Expiry format Date (After Apply): {formatted_date}")
        time.sleep(MAX_SLEEP)

        # Telephone Number
         # No need to fill this field

        # # Entity Type
        # # entity_type = str(cat1['Entity Type'].iloc[0])
        # entity_type = "Citizen"
        # alsagr_logger.debug(f"Entity Type (Before Apply): {entity_type}")
        # await self.page.locator("#entityType").select_option(entity_type)
        # alsagr_logger.debug(f"Entity Type (After Apply): {entity_type}")
        # time.sleep(MED_SLEEP)
        # await self.page.wait_for_load_state('networkidle')

        # # Entity ID
        # # entity_id = str(cat1['Entity ID'].iloc[0])
        # entity_id = "5,675"
        # alsagr_logger.debug(f"Entity ID (Before Apply): {entity_id}")
        # await self.page.locator("#fullNaentityIdme").fill(entity_id)
        # alsagr_logger.debug(f"Entity ID (After Apply): {entity_id}")
        # time.sleep(MED_SLEEP)
        # await self.page.wait_for_load_state('networkidle')

        # Click Save Button
        await self.page.locator("//*[@id='CollapseCustomerInfo']/div[2]/button").click()
        alsagr_logger.debug("Clicked Save Button")
        time.sleep(MAX_SLEEP)

        # Click Pop-up Window Ok Button
        await self.page.get_by_role("button", name="Ok S").click()
        alsagr_logger.debug("Clicked Pop-up Window Ok Button")
        time.sleep(MAX_SLEEP)

        # Insured Type
        tpa = str(cat1['TPA'].iloc[0])
        alsagr_logger.debug(f"TPA (Before Apply): {tpa}")
        await self.page.wait_for_load_state('networkidle')
        time.sleep(MED_SLEEP)
        await self.page.locator("#CollapseQuoteInformation #tpa").select_option(tpa)
        alsagr_logger.debug(f"TPA (After Apply): {tpa}")
        time.sleep(MED_SLEEP)
        await self.page.wait_for_load_state('networkidle')

        # Currency - Autofilled
        # Maternity Age Min - Autofilled
        # Maternity Age Max - Autofilled
        # Child Min Age - Autofilled
        # Child Max Age - Autofilled

        # Nature of Group
        nature_of_group = str(cat1['Business Nature'].iloc[0])
        alsagr_logger.debug(f"Nature of Group (Before Apply): {nature_of_group}")
        
        # Extract dropdown values for Business Nature (Nature of Group)
        region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
        selector = "#natureOfGroup"
        field_name = "Business Nature"
        await extract_dropdown_values(self.page, region, '', '', field_name, selector, portal_name)
        
        await self.page.locator("#natureOfGroup").select_option(nature_of_group)
        alsagr_logger.debug(f"Nature of Group (After Apply): {nature_of_group}")
        time.sleep(MED_SLEEP)
        await self.page.wait_for_load_state('networkidle')

        # Effective Date
        effective_from = (df1[df1['KEY'] == "Effective from"]['VALUE'].values[0])
        alsagr_logger.debug(f"Effective Date (Before Apply): {effective_from}")
        # Correct format for day/month/year
        effective_from = datetime.strptime(effective_from, '%m/%d/%Y').strftime('%Y-%m-%d')
        alsagr_logger.debug(f"Effective Date format (After Apply): {effective_from}")
        await self.page.locator("#effectiveDate").fill(effective_from)
        alsagr_logger.debug(f"Effective Date format (After Apply): {effective_from}")
        time.sleep(MAX_SLEEP)

        # Expiry Date -Autofilled

        # Click  I agree to all terms and Conditions as per Guidelines.
        await self.page.wait_for_load_state('networkidle')
        time.sleep(MED_SLEEP)
        await self.page.locator("#agreeTerms").click()
        alsagr_logger.debug("Agreed to all terms and conditions")
        time.sleep(MED_SLEEP)

        # Click Yes Button
        await self.page.get_by_role("button", name="Yes S").click()
        alsagr_logger.debug("Clicked Yes Button")
        time.sleep(MED_SLEEP)

        # click Save Button
        await self.page.locator('//button[@title="Save"]').click()
        # await self.page.get_by_role("button", name="Ɠ Save").click()
        alsagr_logger.debug("Clicked Save Button")
        time.sleep(MED_SLEEP)

        # Click Pop-up Window Ok Button
        await self.page.get_by_role("button", name="Ok S").click()
        alsagr_logger.debug("Clicked Pop-up Window Ok Button")
        time.sleep(MED_SLEEP)

        # Click Next Button
        await self.page.get_by_role("button", name="Next m").click()
        alsagr_logger.debug("Clicked Next Button")
        time.sleep(MED_SLEEP)

        try:
            # Click Upload Button
            await self.page.get_by_role("button", name="2").click()
            alsagr_logger.debug("Clicked Upload Button")
            time.sleep(MED_SLEEP)

            # Set file to upload
            file_path = (os.path.join(ALSAGR_GENERATED_CENSUS_DIR,"MemberUpload.xlsx"))
            alsagr_logger.debug(f"File path to upload: {file_path}")
            await self.page.get_by_label("Select Excel File:").set_input_files(file_path)
            alsagr_logger.debug("File Uploaded")
            time.sleep(MED_SLEEP)

            # Click Upload Button
            await self.page.get_by_role("button", name="Upload").click()
            alsagr_logger.debug("Clicked Upload Button after file upload")
            time.sleep(MED_SLEEP)

            # Click Proceed button
            await self.page.get_by_text("Proceed").click()
            alsagr_logger.debug("Clicked Proceed Button")
            time.sleep(MED_SLEEP)

        except Exception as e:
            alsagr_logger.error(f"Error during census upload: {e}")
        
            return False

        # Click Next Button
        await self.page.get_by_role("button", name="Next m").click()
        alsagr_logger.debug("Clicked Next Button")
        time.sleep(MAX_SLEEP)

        # # Tick plan button
        # await self.page.locator("#showPlans").click()
        # alsagr_logger.debug("Ticked plan button")
        # time.sleep(MAX_SLEEP)

        time.sleep(MAX_SLEEP)

        # Check if category page loaded
        next_page_element = self.page.locator('//*[@id="scroll-horizontal-datatable"]/thead/tr/th[1]')
        if await next_page_element.is_visible():
            alsagr_logger.info("Category page loaded successfully")
            return True
        else:
            alsagr_logger.error("Category page not loaded")
            return False
 