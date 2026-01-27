import asyncio
import os
from src.utils.load_yaml import IQ2HEALTH_GENERATED_CENSUS_DIR
import datetime
from src.utils.logger import dni_logger
from src.utils.support_functions import screenshot_and_compare, extract_dropdown_values


class ProcessPage:
    def __init__(self, page):
        self.page = page

    async def fill_process_form(self, df1, catA):

        # Wait for the page to load completely
        await self.page.wait_for_load_state('networkidle')
        
        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "dni", "DNI_1")
        except Exception as e:
            dni_logger.error(f"An error occurred while taking the screenshot: {e}")

        # Get the value from the DataFrame
        policy_start_date = df1[df1['KEY'] == "Effective from"]['VALUE'].values[0]
        print("excel psd: " + policy_start_date)
        # Parse the original date string (assuming it is in mm/dd/yyyy format)
        date_object = datetime.datetime.strptime(policy_start_date, '%m/%d/%Y')

        # Format the date into dd/mm/yyyy
        formatted_date = date_object.strftime('%d/%m/%Y')

        print("excel psd: " + formatted_date)

        option_to_select = catA['TPA'].iloc[0]

        # --------------------- process --------------------- #

        #policy holder details

        # await self.page.get_by_role("link", name=" New Quotation").click()
        # await asyncio.sleep(0.1)

        await self.page.locator('//*[@id="sidebar"]/ng-scrollbar/div/div[2]/div/div[1]/a/div[2]').click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Clicked on New Quotation Button")
        # await self.page.get_by_text("Group Quote").click()
        # await self.page.get_by_role("radio", name="Group").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Clicked on Group Quote Button")

        await self.page.locator("#txtPolicyHolder").get_by_role("combobox").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Clicked on Company Name Dropdown")

        await self.page.locator("#txtPolicyHolder").get_by_role("combobox").fill(df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Company Name Filled")

        await self.page.locator("input[name=\"registrationNo\"]").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Registration No Filled")

        await self.page.locator("input[name=\"registrationNo\"]").fill(str(df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0]))
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Trade License Number Filled")

        await self.page.locator("#inceptionDate").get_by_role("combobox").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Inception Date Filled")
        
        print("psd: " + formatted_date)
    
        await self.page.locator("#inceptionDate").get_by_role("combobox").fill(formatted_date)
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Inception Date Filled")

        #Business Nature
        business_nature = str(catA['Business Nature'].iloc[0])
        dni_logger.info(f'Business Nature is {business_nature}')
        
        # Use the exact same approach as Orient (now working) with proper XPath  
        region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
        
        # Use the specific XPath for Business Nature dropdown (same structure as Orient)
        business_nature_xpath = '//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[1]/ul/div[2]/div[2]/div/dx-select-box/div[1]/div/div[1]/input'
        field_name = "Business Nature"
        
        # Click on the dropdown to focus (like category pages)
        dropdown = self.page.locator(business_nature_xpath)
        await dropdown.click()
        dni_logger.debug(f"Attempting to select {field_name}: '{business_nature}'")
        
        # Extract dropdown values using the same method as category pages
        await extract_dropdown_values(self.page, region, '', '', field_name, business_nature_xpath, 'Dubai National Insurance And Reinsurance Co')

        # Use arrow keys to navigate through dropdown options (like category pages)
        max_attempts = 15
        attempts = 0

        while attempts < max_attempts:
            # Get the current selected value
            selected_value = await dropdown.evaluate("element => element.value")
            # Log the comparison between Excel and dropdown values
            dni_logger.debug(f"{field_name}: Checking option '{selected_value}' against target '{business_nature}'")
            
            # If a match is found, select the option
            if selected_value == business_nature:
                dni_logger.debug(f"{field_name}: Match found. Selecting '{selected_value}'")
                await self.page.keyboard.press("Enter")
                break
            else:
                # Log the mismatch and navigate to the next option
                dni_logger.debug(f"{field_name}: No match found. Navigating to next option.")
                await self.page.keyboard.press("ArrowDown")

            # Small delay to prevent rapid navigation
            await asyncio.sleep(0.1)
            attempts += 1

        if attempts >= max_attempts:
            dni_logger.warning(f"{field_name}: Could not find exact match for '{business_nature}' after {max_attempts} attempts")

        await asyncio.sleep(0.5)  # Extra pause after attempting selection

        
        dni_logger.debug("Clicked on TPA Dropdown")

        await self.page.locator("input[name=\"licenseNo\"]").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("License No Filled")

        await self.page.locator("input[name=\"licenseNo\"]").fill(str(df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0]))
        await asyncio.sleep(0.1)
        
        dni_logger.debug("License No Filled")

        await self.page.get_by_role("radio", name="SME Product").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Clicked on SME Product Radio Button")

        await self.page.get_by_role("radio", name="Conventional Plan").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Clicked on Conventional Plan Radio Button")

		#Insurer Details 
        await self.page.locator('xpath=//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[1]/div[1]/div/dx-select-box/div[1]/div/div[1]/input').fill(catA['Existing Insurer'].iloc[0])
        await asyncio.sleep(1)
       
        dni_logger.debug("Existing Insurer Filled " + catA['Existing Insurer'].iloc[0])
 
        await self.page.locator('xpath=//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[1]/div[1]/div/dx-select-box/div[1]/div/div[1]/input').press("ArrowDown")
        dni_logger.debug('Arrow Down')
        await self.page.locator(f'//div[contains(@class, "dx-item-content") and text()="{catA['Existing Insurer'].iloc[0]}"]').click()
 
        await self.page.locator('xpath=//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[1]/div[1]/div/dx-select-box/div[1]/div/div[1]/input').press("Enter")
        await asyncio.sleep(1)
        dni_logger.debug('Enter')
       
       
        # dni_logger.debug("Company Name Selected " + catA['Company'].iloc[0])
        #Company Name
        await self.page.locator('xpath=//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[1]/div[2]/div/dx-select-box/div[1]/div/div[1]/input').fill('Dubai National Insurance And Reinsurance Co')
        await asyncio.sleep(1)
 
        await self.page.locator('xpath=//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[1]/div[2]/div/dx-select-box/div[1]/div/div[1]/input').press("ArrowDown")
        await asyncio.sleep(1)
 
        await self.page.locator('xpath=//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[1]/div[2]/div/dx-select-box/div[1]/div/div[1]/input').press("Enter")
        await asyncio.sleep(1)
       

        #existing TPA
        await self.page.locator('//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[3]/div[1]/div/dx-select-box/div/div/div[1]/input').fill(catA['Existing TPA'].iloc[0])
        await asyncio.sleep(1)
 
        await self.page.locator('//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[3]/div[1]/div/dx-select-box/div/div/div[1]/input').press("ArrowDown")
        await asyncio.sleep(1)
 
        await self.page.locator('//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[3]/div[1]/div/dx-select-box/div/div/div[1]/input').press("Enter")
        await asyncio.sleep(1)
       

        #TPA
        dni_logger.debug("TPA Selected " + catA['TPA'].iloc[0])
        value = catA['TPA'].iloc[0] 
 
        # Click the dropdown to open the options list
        await self.page.locator('xpath=//*[@id="content"]/sa-quotation/div/sa-uae-quotation/div/sa-policyholder/div/dx-validation-group/div/div/sa-ae-policyholder/div/div/div[2]/ul/div[3]/div[2]/div/dx-select-box/div[1]/div/div[1]/input').click()
        dni_logger.debug('tpa clicked')
        await asyncio.sleep(1)

        await self.page.get_by_role("option", name=value).click()
        dni_logger.debug('click option')


        # await self.page.locator('xpath=//*[@id="widgets-grid"]/div/div/div[2]/div[1]/dx-validation-group/div/div/sa-ae-policyholder/div/div[3]/div/div/div[3]/div[2]/div/div/dx-select-box/div[1]/div/div[1]/input').fill(catA['TPA'].iloc[0])
        # dni_logger.debug('fill tpa')
        # await self.page.locator('xpath=//*[@id="widgets-grid"]/div/div/div[2]/div[1]/dx-validation-group/div/div/sa-ae-policyholder/div/div[3]/div/div/div[3]/div[2]/div/div/dx-select-box/div[1]/div/div[1]/input').press("ArrowDown")
        # dni_logger.debug('arrowdown')
        # await self.page.locator('xpath=//*[@id="widgets-grid"]/div/div/div[2]/div[1]/dx-validation-group/div/div/sa-ae-policyholder/div/div[3]/div/div/div[3]/div[2]/div/div/dx-select-box/div[1]/div/div[1]/input').press("Enter")
        # dni_logger.debug("Clicked on TPA Dropdown")
        # # Get the list of available options
        # options_locator = self.page.locator('//div[@class="dx-item dx-list-item"]')
        # options_count = await options_locator.count()

        # # Loop through the options and match the text
        # for i in range(options_count):
        #     option_text = await options_locator.nth(i).text_content()
        #     if option_to_select in option_text:
        #         await options_locator.nth(i).click()
        #         break

        await asyncio.sleep(1)
        
        dni_logger.debug("TPA Filled " + catA['TPA'].iloc[0])
        
        #Policy Holder Contact
        await self.page.locator("input[name=\"firstName\"]").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Contact Person Clicked")

        await self.page.locator("input[name=\"firstName\"]").fill(df1[df1['KEY'] == "Contatct Person"]['VALUE'].values[0])
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Contact Person Filled " + df1[df1['KEY'] == "Contatct Person"]['VALUE'].values[0])

        await self.page.locator("input[name=\"email\"]").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Email Clicked")

        await self.page.locator("input[name=\"email\"]").fill(df1[df1['KEY'] == "Email"]['VALUE'].values[0])
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Email Filled " + df1[df1['KEY'] == "Email"]['VALUE'].values[0])

        await self.page.locator("input[name=\"phone\"]").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Phone Clicked")

        await self.page.locator("input[name=\"phone\"]").fill(str(df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0]))
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Phone Filled " + str(df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0]))

        await self.page.get_by_label("Proceed").click()
        await asyncio.sleep(0.1)
        
        dni_logger.debug("Proceed Clicked")
        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(5)

        await self.page.locator('input[type="file"]').set_input_files(os.path.join(IQ2HEALTH_GENERATED_CENSUS_DIR, "Census_Template_AE.xlsm"))
        await asyncio.sleep(4)
        
        dni_logger.debug("Uploaded Census Template")
        
        await self.page.wait_for_load_state('networkidle')

        await self.page.get_by_label("Upload", exact=True).click()
        await asyncio.sleep(0.1)
        await self.page.wait_for_load_state('networkidle')
        
        dni_logger.debug("Upload Completed")

        quotation_no = await self.page.locator("//td[contains(text(), 'Quotation No')]/following-sibling::td[1]").text_content()
        print(f"Saved Quotation No: {quotation_no}")

        
        await self.page.get_by_role("button", name="Proceed to Benefits ").click()
        await asyncio.sleep(1)
        await self.page.wait_for_load_state('networkidle')
        
        dni_logger.debug("Proceed to Benefits Clicked")
        
        return quotation_no