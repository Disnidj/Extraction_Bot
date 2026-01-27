import asyncio
import os
from datetime import datetime

from src.utils.load_yaml import (
    MAXHEALTH_GENERATED_CENSUS_DIR,
    # MAXHEALTH_QUOTATION_DIR,
    ATTACHMENTS_SAVE_DIR,
    MAXHEALTH_TEMPLATES_DIR
)
from src.utils.logger import maxhealth_logger
import csv
import shutil
import pandas as pd
from src.utils.support_functions import extract_mui_dropdown_values, screenshot_and_compare

class NewCase:
    def __init__(self, page, df1, df2, region, tpa, network):
        self.page = page
        self.df1 = df1
        self.df2 = df2
        self.region = region
        self.tpa = tpa
        self.network = network

    def fetch_value(self, df, key):
        value = df[df['KEY'] == key]['VALUE'].values[0]
        maxhealth_logger.info(f"fetch_value: key={key}, value={value}")
        print(f"fetch_value: key={key}, value={value}")
        return value

    def get_value(self, column_name):
        try:
            value = str(self.df2[column_name].values[0])
            maxhealth_logger.info(f"get_value: column_name={column_name}, value={value}")
            print(f"get_value: column_name={column_name}, value={value}")
            return value
        except (KeyError, IndexError):
            msg = f"Column '{column_name}' not found or empty in DataFrame."
            maxhealth_logger.error(msg)
            print(msg)
            return None

    async def create_new_case(self, df1):
        maxhealth_logger.info("create_new_case: Started")
        print("create_new_case: Started")
        portal_name = "MaxHealth"
        await asyncio.sleep(2)
    
        try:
            maxhealth_logger.info("Waiting for New Case button to be visible.")
            await self.page.wait_for_selector("text=New Case", timeout=60000)
            maxhealth_logger.info("New Case button is visible.")
            
            # Click New Case button with extra diagnostics
            try:
                maxhealth_logger.info("Attempting to click New Case button.")
                print("Attempting to click New Case button.")
                await self.page.locator("text=New Case").click(timeout=60000, force=True)
                maxhealth_logger.info("New Case button clicked.")
                print("New Case button clicked.")
                await self.page.wait_for_load_state('networkidle', timeout=90000)
                maxhealth_logger.info("Page reached networkidle after New Case click.")
                print("Page reached networkidle after New Case click.")
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error clicking New Case button or waiting for page load - {e}")
                print(f"Error clicking New Case button or waiting for page load - {e}")
                # Take screenshot and dump page content for debugging
                try:
                    await self.page.screenshot(path="maxhealth_newcase_click_error.png")
                    content = await self.page.content()
                    with open("maxhealth_newcase_click_error.html", "w", encoding="utf-8") as f:
                        f.write(content)
                    maxhealth_logger.error("Saved screenshot and page content for New Case click failure.")
                except Exception as inner_e:
                    maxhealth_logger.error(f"Failed to save screenshot or page content: {inner_e}")
                return False

            await asyncio.sleep(2)

            # Upload Census File
            try:
                maxhealth_logger.info("Waiting for file input to be attached.")
                print("Waiting for file input to be attached.")
                # Retry loop for file input selector
                file_input_selector = "input[type='file'][accept*='.xlsx']"
                file_input_locator = self.page.locator(file_input_selector)
                file_input_found = False
                for attempt in range(10):  # Try for up to 50 seconds
                    try:
                        await self.page.wait_for_selector(file_input_selector, state="attached", timeout=5000)
                        await file_input_locator.wait_for(state="attached", timeout=5000)
                        file_input_found = True
                        break
                    except Exception as e:
                        maxhealth_logger.warning(f"Attempt {attempt+1}: File input not found yet: {e}")
                        await asyncio.sleep(5)
                if not file_input_found:
                    maxhealth_logger.error("File input not found after retries. Dumping page content and screenshot.")
                    try:
                        content = await self.page.content()
                        maxhealth_logger.error(f"Page content: {content[:1000]}...")
                        await self.page.screenshot(path="maxhealth_fileinput_error.png")
                        maxhealth_logger.error("Screenshot saved as maxhealth_fileinput_error.png")
                    except Exception as e2:
                        maxhealth_logger.error(f"Failed to get page content or screenshot: {e2}")
                    return False
                maxhealth_logger.info("File input is ready for file upload.")
                print("File input is ready for file upload.")
                await asyncio.sleep(3)
                file_path_1 = MAXHEALTH_GENERATED_CENSUS_DIR + "/MaxHealth.xlsx"
                maxhealth_logger.info(f"Uploading census file from path: {file_path_1}")

                await file_input_locator.set_input_files(file_path_1)
                await asyncio.sleep(2)
                maxhealth_logger.info("Census file uploaded successfully.")
                print("Census file uploaded successfully.")
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error uploading census - {e}")
                print(f"Error uploading census - {e}")
                return False


            # Screenshot after uploading census
            try:
                await asyncio.sleep(10)
                await screenshot_and_compare(self.page, "maxhealth", "MAXHEALTH_1")
                await asyncio.sleep(10)
            except Exception as e:
                maxhealth_logger.error(f"Error taking screenshot - {e}")

            await asyncio.sleep(2)

            # TPA Dropdown
            try:
                TPA = self.get_value("TPA")
                if not TPA:
                    raise ValueError("TPA value is missing or invalid.")
                TPA = TPA.strip().upper()
                maxhealth_logger.debug(f"Selected TPA value: {TPA}")

                # Selector for the dropdown
                dropdown_selector = '//*[@id="mui-39"]'  
                await self.page.wait_for_selector(dropdown_selector, timeout=90000)
                await self.page.click(dropdown_selector)
                await asyncio.sleep(2)

                # Wait for dropdown to be populated (increase sleep or use a loop)
                max_attempts = 5
                for attempt in range(max_attempts):
                    await asyncio.sleep(2)  # or a longer wait if needed
                    tpa_options = await extract_mui_dropdown_values(
                        self.page, self.region, self.tpa, self.network, "TPA", dropdown_selector, portal_name
                    )
                    if tpa_options:  # If options are found, break early
                        break
                else:
                    maxhealth_logger.error(f"TPA dropdown not populated after waiting. Options: {tpa_options}")
                    return False

                if not tpa_options or TPA not in [opt.upper() for opt in tpa_options]:
                    maxhealth_logger.error(f"TPA '{TPA}' not found in dropdown options: {tpa_options}")
                    print(f"TPA '{TPA}' not found in dropdown options: {tpa_options}")
                    # Decide: return False, skip, or select a default
                    return False

                # Use a robust Playwright selector for TPA option
                tpa_option_selector = f'li[role="option"]:has-text("{TPA}")'
                maxhealth_logger.info(f"Attempting to select TPA option with selector: {tpa_option_selector}")
                print(f"Attempting to select TPA option with selector: {tpa_option_selector}")
                try:
                    await self.page.locator(tpa_option_selector).wait_for(state="visible", timeout=30000)
                    await self.page.locator(tpa_option_selector).click()
                    await asyncio.sleep(2)
                    maxhealth_logger.debug("TPA value selected.")
                except Exception as e:
                    maxhealth_logger.error(f"Failed to select TPA option '{TPA}' with selector '{tpa_option_selector}': {e}")
                    print(f"Failed to select TPA option '{TPA}' with selector '{tpa_option_selector}': {e}")
                    return False

            except Exception as e:
                maxhealth_logger.error(f"error occured while selecting TPA - {e}")
                print(f"error occured while selecting TPA - {e}")
                return False
            
            # Network Dropdown
            try:
                # Ensure any open dropdown is closed
                await self.page.keyboard.press("Escape")
                await asyncio.sleep(0.5)

                network = self.get_value("Network")
                network = network.strip().upper()
                product_line = network.split()[0]
                dropdown_selector = '//*[@id="mui-40"]'

                # Open the dropdown before extracting values and clicking
                await self.page.click(dropdown_selector)
                await asyncio.sleep(2)

                network_options = await extract_mui_dropdown_values(
                    self.page, self.region, self.tpa, self.network, "Network", dropdown_selector, portal_name
                )
                maxhealth_logger.info(f"Extracted Network/Product Line dropdown values: {network_options}")
                print(f"Extracted Network/Product Line dropdown values: {network_options}")
                
                # **Use the working selector pattern**
                await self.page.locator(f'li[role="option"]:has-text("{product_line}")').click()
                await asyncio.sleep(2)
                maxhealth_logger.info(f"Product Line selected: {product_line}")
                print(f"Product Line selected: {product_line}")
            except Exception as e:
                maxhealth_logger.error(f"Error selecting network - {e}")
                print(f"Error selecting network - {e}")
                return False
            

            # Company Name
            try:
                company_name = self.fetch_value(self.df1, "Company Name")
                maxhealth_logger.info(f"Company Name: {company_name}")
                print(f"Company Name: {company_name}")
                await self.page.locator("//input[@id='clientName']").fill(company_name)
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error selecting client name - {e}")
                print(f"Error selecting client name - {e}")
                return False

            # Location Dropdown
            try:
                location = self.fetch_value(self.df1, "Emirates")
                dropdown_selector = '//*[@id="mui-42"]'

                await self.page.click(dropdown_selector)
                await asyncio.sleep(2)

                location_options = await extract_mui_dropdown_values(
                    self.page, self.region, self.tpa, self.network, "Location", dropdown_selector, portal_name
                )
                maxhealth_logger.info(f"Extracted Client Location dropdown values: {location_options}")
                print(f"Extracted Client Location dropdown values: {location_options}")
                await self.page.locator(f'li[role="option"]:has-text("{location}")').click()
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error selecting location - {e}")
                print(f"Error selecting location - {e}")
                return False

            # Contact Person
            try:
                contact_person = self.fetch_value(self.df1, "Contatct Person")
                maxhealth_logger.info(f"Contact Person: {contact_person}")
                print(f"Contact Person: {contact_person}")
                await self.page.locator("//input[@id='accountHandlingPersonName']").fill(contact_person)
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error selecting account handling person name - {e}")
                print(f"Error selecting account handling person name - {e}")
                return False

            # Policy Start Date
            try:
                policy_str_date = self.fetch_value(self.df1, "Effective from")
                maxhealth_logger.info(f"Policy Start Date: {policy_str_date}")
                print(f"Policy Start Date: {policy_str_date}")
                await self.page.locator("input[placeholder='dd/mm/yyyy']").click()
                await self.page.locator("input[placeholder='dd/mm/yyyy']").fill(policy_str_date)
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error selecting policy start date - {e}")
                print(f"Error selecting policy start date - {e}")
                return False

            # Email
            try:
                email = self.fetch_value(self.df1, "Email")
                maxhealth_logger.info(f"Email: {email}")
                print(f"Email: {email}")
                await self.page.locator('input[name="brokerSecondaryEmail"]').fill(email)
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error selecting account handling person email - {e}")
                print(f"Error selecting account handling person email - {e}")
                return False

            # Current Insurer
            try:
                current_insurer = self.fetch_value(self.df1, "Contatct Person")
                maxhealth_logger.info(f"Current Insurer: {current_insurer}")
                print(f"Current Insurer: {current_insurer}")
                await self.page.locator('input[name="currentInsurer"]').fill(current_insurer)
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error selecting current insurer - {e}")
                print(f"Error selecting current insurer - {e}")
                return False

            # Contact Number
            try:
                contact_number = str(self.fetch_value(self.df1, "Contact  Number"))
                maxhealth_logger.info(f"Contact Number: {contact_number}")
                print(f"Contact Number: {contact_number}")
                await self.page.locator('input[name="brokerMobile"]').fill(contact_number)
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error selecting account handling person mobile number - {e}")
                print(f"Error selecting account handling person mobile number - {e}")
                return False

            # Policy Holder Type Dropdown
            try:
                policy_holder_type = "SME Group: 10 members (minimum of 3 employees) up to 300 members"
                dropdown_selector = '//*[@id="mui-49"]'

                await self.page.click(dropdown_selector)
                await asyncio.sleep(2)

                policy_holder_options = await extract_mui_dropdown_values(
                    self.page, self.region, self.tpa, self.network, "Policy Holder Type", dropdown_selector, portal_name
                )
                maxhealth_logger.info(f"Extracted Policy Holder Type dropdown values: {policy_holder_options}")
                print(f"Extracted Policy Holder Type dropdown values: {policy_holder_options}")
                await self.page.locator(f'li[role="option"]:has-text("{policy_holder_type}")').click()
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error selecting policy holder type - {e}")
                print(f"Error selecting policy holder type - {e}")
                return False

            # Quotation For Dropdown
            try:
                quotation_for = self.fetch_value(self.df1, "New-Renew")
                maxhealth_logger.info(f"Quotation For: {quotation_for}")
                print(f"Quotation For: {quotation_for}")
                
                # Use multiple fallback selectors since IDs are dynamic
                selectors_to_try = [
                    '//label[text()="Quotation For"]/..//div[@role="button"]',  # Navigate from label
                ]
                
                quotation_dropdown_selector = None
                for selector in selectors_to_try:
                    try:
                        await self.page.wait_for_selector(selector, timeout=5000)
                        quotation_dropdown_selector = selector
                        maxhealth_logger.info(f"Found Quotation For dropdown with selector: {selector}")
                        print(f"Found Quotation For dropdown with selector: {selector}")
                        break
                    except:
                        maxhealth_logger.debug(f"Selector failed: {selector}")
                        continue
                
                if not quotation_dropdown_selector:
                    raise Exception("Could not locate Quotation For dropdown with any selector")
                
                await self.page.locator(quotation_dropdown_selector).click()
                await asyncio.sleep(2)
                
                quotation_options = await extract_mui_dropdown_values(
                    self.page, self.region, self.tpa, self.network, "Quotation For", quotation_dropdown_selector, portal_name
                )
                maxhealth_logger.info(f"Extracted Quotation For dropdown values: {quotation_options}")
                print(f"Extracted Quotation For dropdown values: {quotation_options}")
                await asyncio.sleep(1)
                
                if quotation_for == "New":
                    await self.page.get_by_role("option", name="New Client", exact=True).click()
                    await asyncio.sleep(0.5)
                    maxhealth_logger.info("Quotation For selected as 'New Client'.")
                    print("Quotation For selected as 'New Client'.")
                    await asyncio.sleep(2)

                    # Upload TOP
                    try:
                        # TOB file path
                        file_path = os.path.join(ATTACHMENTS_SAVE_DIR, "tob.pdf")

                        
                        # Provide the XPath to the input element where files are uploaded
                        input_xpath = '//*[@id="root"]/div/main/div/div/div[2]/div[1]/form/div/div/div[2]/div[2]/div[16]/div/div/input'
                        # Wait for the input to be attached and visible
                        await self.page.wait_for_selector(input_xpath, state="attached", timeout=80000)
                        await self.page.wait_for_selector(input_xpath, state="visible", timeout=80000)
                        # Set the input element's visibility to true before uploading (since it's hidden)
                        await self.page.eval_on_selector(input_xpath, "input => input.style.display = 'block'")
                        # Upload the file
                        await self.page.set_input_files(input_xpath, file_path)
                        await asyncio.sleep(4)

                    except Exception as e:
                        maxhealth_logger.info(f"File upload failed: {e}")
                        email = df1[df1['KEY'] == "Email"]['VALUE'].values[0]
                        error = "Failed to upload TOB file"
                        # update_error_log_table(var_req, "MaxHealth", email , error)
                        # update_request_status(var_req, "Failed")
                        return False

                    await asyncio.sleep(2) 
                    maxhealth_logger.info("ok2")

                else:
                    await self.page.get_by_role("option", name="New Client (Virgin Group)").click()
                    await asyncio.sleep(2)
                    maxhealth_logger.info("Quotation For selected as 'New Client (Virgin Group)'.")
                    print("Quotation For selected as 'New Client (Virgin Group)'.")
                    
            except Exception as e:
                maxhealth_logger.error(f"Error selecting Quotation For - {e}")
                print(f"Error selecting Quotation For - {e}")
                return False
            

            # Target Premium
            try:
                target_premium = self.get_value("Target Premium")
                maxhealth_logger.info(f"Target Premium: {target_premium}")
                print(f"Target Premium: {target_premium}")
                await self.page.locator('//*[@id="mui-51"]').click()
                await self.page.wait_for_selector('//*[@id="mui-51"]', timeout=60000)
                await self.page.locator('//*[@id="mui-51"]').type(target_premium)
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error selecting target premium - {e}")
                print(f"Error selecting target premium - {e}")
                return False


            try:
                await asyncio.sleep(10)
                await screenshot_and_compare(self.page, "maxhealth", "MAXHEALTH_2")
                await asyncio.sleep(10)
            except Exception as e:
                maxhealth_logger.error(f"Error taking screenshot - {e}")
                return False

            # Navigation Buttons
            try:
                await self.page.locator('//*[@id="root"]/div/main/div/div/div[2]/div[3]/button[2]').wait_for(state="visible", timeout=90000)
                await self.page.locator('//*[@id="root"]/div/main/div/div/div[2]/div[3]/button[2]').click()
                maxhealth_logger.info("Next button clicked.")
                print("Next button clicked.")
                await asyncio.sleep(2)
                await self.page.locator('//*[@id="root"]/div/main/div/div/div[2]/div[3]/button[3]/span').wait_for(state="visible", timeout=90000)
                await self.page.locator('//*[@id="root"]/div/main/div/div/div[2]/div[3]/button[3]/span').click()
                maxhealth_logger.info("Next button clicked (second).")
                print("Next button clicked (second).")
                await asyncio.sleep(2)
                await self.page.wait_for_load_state('networkidle', timeout=90000)
                await asyncio.sleep(2)
            except Exception as e:
                maxhealth_logger.error(f"Error during navigation - {e}")
                print(f"Error during navigation - {e}")
                return False

            # Categories
            maxhealth_logger.info("Finding categories.")
            print("Finding categories.")
            categories_present = self.df2['Category'].dropna().unique()
            maxhealth_logger.info(f"Categories present: {categories_present}")
            print(f"Categories present: {categories_present}")
            for category in categories_present:
                category = category.strip().upper()
                maxhealth_logger.info(f"Processing category {category}")
                print(f"Processing category {category}")
                category_data = self.df2[self.df2['Category'] == category]
                if category_data.empty:
                    maxhealth_logger.info(f"No data for category {category}")
                    print(f"No data for category {category}")
                select_plan = category_data['Territory'].values[0]
                maxhealth_logger.info(f"Processing category {category} with plan: {select_plan}")
                print(f"Processing category {category} with plan: {select_plan}")
                await asyncio.sleep(0.5)

            # Save and Exit
            try:
                await self.page.locator('//*[@id="root"]/div/main/div/div/div[2]/div[3]/button[2]').wait_for(state="visible", timeout=60000)
                await self.page.locator('//*[@id="root"]/div/main/div/div/div[2]/div[3]/button[2]').click()
                await asyncio.sleep(5)
                maxhealth_logger.info("Clicked save and exit button.")
                print("Clicked save and exit button.")
                await asyncio.sleep(5)
                await self.page.wait_for_load_state('networkidle')
                await asyncio.sleep(5)
            except Exception as e:
                maxhealth_logger.error(f"Error during save and exit - {e}")
                print(f"Error during save and exit - {e}")
                return False

            maxhealth_logger.info("create_new_case: Completed successfully")
            return True

        except Exception as e:
            maxhealth_logger.error(f"Error occurred while quotation creation - {e}")
            print(f"Error occurred while quotation creation - {e}")
            return False