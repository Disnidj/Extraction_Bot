import asyncio
from src.utils.logger import rak_logger
from src.utils.support_functions import extract_dropdown_values, screenshot_and_compare


class Category1Page:

    def __init__(self, page):

        self.page = page

    async def fill_category_1(self, catA, df2):
        # Convert all DataFrame values to strings
        catA = catA.astype(str)

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "rak", "RAK_2")
        except Exception as e:
            rak_logger.error(f"An error occurred while taking screenshot: {e}")

        # # General Benefits
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[1]/div[2]/div/div[2]/dx-select-box/div/div/div[1]/input', catA['Network'].iloc[0].split('-')[0].strip(), "Network Part 1", df2)
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[1]/div[1]/div/dx-select-box/div/div/div[1]/input',(network_value := catA['Network'].iloc[0].split('- ', 1)[1].strip()) + (" " if network_value in [ "Green","Silver Premium"] else ""),"Network Part 2", df2)

        # # Other Fields
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[1]/div[2]/div/dx-select-box/div[1]/div/div[1]/input', catA['Territory'].iloc[0], "Territory", df2)#
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[2]/div[1]/div/dx-select-box/div/div/div[1]/input',catA['Annual Limit'].iloc[0], "Annual Limit", df2)#
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[2]/div[2]/div/dx-select-box/div[1]/div/div[1]/input',catA['Reimbursement'].iloc[0].replace('100%', '100 %') if catA['Reimbursement'].iloc[0] == '100% of UCR' else catA['Reimbursement'].iloc[0],"Reimbursement", df2)#
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[4]/div[1]/div/dx-select-box/div[1]/div/div[1]/input', "Up to AAL", "Consultation Limit", df2)#
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[4]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Deductable'].iloc[0], "Deductable", df2)#
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[5]/div[1]/div/dx-select-box/div[1]/div/div[1]/input', "Up to AAL", "Co-payment on diagnostics", df2)#
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[5]/div[2]/div/dx-select-box/div/div/div[1]/input',  catA['Diagnostic Copay'].iloc[0], "Diagnostic Copay", df2)
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[6]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Limit of Phamacy'].iloc[0], "Limit of Phamacy", df2)

        # # Handle Pharmacy value that may appear as a percentage
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[6]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Pharmacy'].iloc[0], "Pharmacy", df2)#
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[7]/div/div/dx-select-box/div/div/div[1]/input', catA['Physio Co'].iloc[0], "Physio Co", df2)#
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[9]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Maternity - Married Females'].iloc[0], "Maternity - Married Females", df2)#
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[9]/div[2]/div/dx-select-box/div/div/div[1]/input', "NIL", "Waiting Period", df2)

        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[11]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Dental'].iloc[0], "Dental", df2)#
        # if catA['Dental'].iloc[0] != 'Not Covered':
        #     await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[11]/div[2]/div/dx-select-box/div[1]/div/div[1]/input',  catA['Dental CO'].iloc[0], "Dental CO", df2)
        
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[13]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Optical'].iloc[0], "Optical", df2)#
        # if catA['Optical'].iloc[0] != 'Not Covered':
        #     await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[13]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Optical CO'].iloc[0], "Optical CO", df2)
        
        # await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[15]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Alternative Medicine'].iloc[0], "Alternative Medicine", df2)#
        # if catA['Alternative Medicine'].iloc[0] != 'Not Covered':
        #     await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div[15]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Alternative Medicine Co'].iloc[0], "Alternative Medicine Co", df2)

        # rak_logger.debug("Category A Completed")
        # print('Category A Completed')
        # return True

        # General Benefits
        await self._select_option('//*[@id="collapse_0"]/div/div/div[1]/div/div[2]/dx-select-box/div[1]/div/div[1]/input', catA['Sub Plan'].iloc[0].split('-')[0].strip(), "Network Part 1")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[2]/div/div[2]/div/dx-select-box/div[1]/div/div[1]/input', catA['Network'].iloc[0], "Plan")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[1]/div[1]/div/dx-select-box/div[1]/div/div[1]/input',(network_value := catA['Sub Plan'].iloc[0].split('- ', 1)[1].strip()) + (" " if network_value in [ "Green","Silver Premium"] else ""),"Network Part 2")

        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[1]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Territory'].iloc[0], "Geographical Scope")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[2]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Annual Limit'].iloc[0], "Annual Aggregate Limit")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[2]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Reimbursement'].iloc[0], "Reimbursement")
        
        # Maternity Benefit
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[4]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['MaternityNewborn'].iloc[0], "Maternity Benefit - Annual Limit")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[4]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Waiting Period'].iloc[0], "Maternity Benefit - Waiting Period")
                    
        # Outpatient Benefit
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[5]/div/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Outpatient Plan'].iloc[0], "Outpatient Plan")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[6]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Consultation Limit'].iloc[0], "Consultation Limit")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[6]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Deductable'].iloc[0], "Consultation Copay")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[7]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Lab & Diagnostics Sublimit'].iloc[0], "Diagnostic Limit")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[7]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Lab & Diagnostics Co-pay'].iloc[0], "Diagnostic Copay")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[8]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Limit of Phamacy'].iloc[0], "Pharmacy Limit")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[8]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Pharmacy'].iloc[0], "Pharmacy Copay")
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[9]/div/div/dx-select-box/div/div/div[1]/input', catA['Physio Co'].iloc[0], "Physiotherapy Copay")

        # Additional Benefit
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[10]/div/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Additional Benefits Plan'].iloc[0], "Additional Benefit Plan")

        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[11]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Dental'].iloc[0], "Dental")
        if catA['Dental'].iloc[0] != 'Not Covered':
            await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[11]/div[2]/div/dx-select-box/div/div/div[1]/input',  catA['Dental CO'].iloc[0], "Dental CO")
        
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[12]/div[1]/div/dx-select-box/div[1]/div/div[1]/input', catA['Optical'].iloc[0], "Optical")
        if catA['Optical'].iloc[0] != 'Not Covered':
            await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[12]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Optical CO'].iloc[0], "Optical CO")
        
        await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[13]/div[1]/div/dx-select-box/div/div/div[1]/input', catA['Alternative Medicine'].iloc[0], "Alternative Medicine")
        if catA['Alternative Medicine'].iloc[0] != 'Not Covered':
            await self._select_option('//*[@id="collapse_0"]/div/div/div[3]/div[13]/div[2]/div/dx-select-box/div/div/div[1]/input', catA['Alternative Medicine Co'].iloc[0], "Alternative Medicine Co")

        rak_logger.debug("Category A Completed")
        print('Category A Completed')
        return True      

    async def _select_option(self, input_locator, value_to_select, field_name, df2):

        try:
            region = df2['Region'].iloc[0]
            tpa = df2['TPA'].iloc[0]
            network = df2['Network'].iloc[0]

            # Click on the dropdown to focus
            dropdown = self.page.locator(input_locator)
            await dropdown.click()
            rak_logger.debug(f"Attempting to select {field_name}: '{value_to_select}'")

            await extract_dropdown_values(self.page, region, tpa, network, field_name, input_locator, 'RAK INSURANCE')

            max_attempts = 15  # Limit the number of attempts
            attempts = 0

            # Use arrow keys to navigate through dropdown options
            while attempts < max_attempts:
                # Get the current selected value
                selected_value = await dropdown.evaluate("element => element.value")
                # Log the comparison between Excel and dropdown values
                rak_logger.debug(f"{field_name}: Checking option '{selected_value}' against target '{value_to_select}'")
                # If a match is found, select the option
                if selected_value == value_to_select:
                    rak_logger.debug(f"{field_name}: Match found. Selecting '{selected_value}'")
                    await self.page.keyboard.press("Enter")
                    return

                else:
                    # Log the mismatch and navigate to the next option
                    rak_logger.debug(
                        f"{field_name}: No match found. Navigating to next option.")
                    await self.page.keyboard.press("ArrowDown")

                # Small delay to prevent rapid navigation
                await asyncio.sleep(0.1)
                attempts += 1

            else:
                raise Exception(f"Maximum attempts reached without success for {field_name} field")

        except TimeoutError:
            rak_logger.error(f"Timeout error while selecting {field_name}. Locator: {input_locator}")

        except Exception as e:
            rak_logger.error(f"Error selecting {field_name}: {e}. Locator: {input_locator}, Value: {value_to_select}")

        finally:
            await asyncio.sleep(0.5)  # Extra pause after attempting selection

    def _convert_to_percentage(self, value):
        """Converts decimal values to a percentage format string."""

        try:

            float_value = float(value)

            return f"{int(float_value * 100)}%"

        except ValueError:

            rak_logger.error(f"Error converting value '{value}' to percentage format.")

            return value
        
    def _convert_to_int(self, value):
        try:
            # Convert to float if it's a string with a decimal, then to int and back to string
            value = int(float(value)) if isinstance(value, str) else int(value)

            return str(value)  # Return the integer as a string

        except ValueError:
            rak_logger.error(f"Error converting value '{value}' to int format.")
            return value