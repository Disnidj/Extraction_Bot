import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import extract_dropdown_values, screenshot_and_compare
from src.utils.logger import wataniatakaful_logger

class Category1Page:
    def __init__(self, page, portal_name):
        self.page = page
        self.portal_name = portal_name

    async def get_table_rows_count(self):
        try:
            rows = await self.page.query_selector_all('//table[@class="mt-3 table table-bordered ng-star-inserted"]//tr')
            count = len(rows)
            wataniatakaful_logger.debug(f"Total rows in table: {count}")
            return count
        except Exception as e:
            wataniatakaful_logger.error(f"Error counting table rows: {e}")
            return 0

    def get_field_selector(self, field_name, column=1):
        # Get nth select element for the field based on column number (1-based index)
        # return f"//td[normalize-space(.)='{field_name}' or contains(normalize-space(.), '{field_name}')]/following-sibling::td[{column}]/select"
        return f"//td[normalize-space(.)='{field_name}']/following-sibling::td[{column}]/select"


    async def select_option_with_error_handling(self, region, tpa, network, field_name, value, column, use_dynamic_selector=True):
        try:
            selector = self.get_field_selector(field_name, column) if use_dynamic_selector else field_name
            wataniatakaful_logger.debug(f"{field_name} Value for Column {column}: (Before Apply) {value}")
            await extract_dropdown_values(self.page, region, tpa, network, field_name, selector, self.portal_name)

            await self.page.select_option(selector, value=value.rstrip(), timeout=3000)
            wataniatakaful_logger.debug(f"{field_name} Value for Column {column}: (After Apply) {value}")
            await asyncio.sleep(MAX_SLEEP)
            wataniatakaful_logger.debug(f"{field_name} Column {column} Filled")
            return True
        except Exception as e:
            wataniatakaful_logger.error(f"Error occurred while selecting {field_name} for Column {column}: {e}")
            return False

    def normalize_value(self, value):
        """Normalize value for comparison by removing commas and spaces"""
        if not value:
            return ""
        return str(value).replace(',', '').replace(' ', '').strip().lower()

    async def handle_optical_benefit(self, value, column, region, tpa, network):
        try:
            optical_selectors = await self.page.query_selector_all(
                f"//td[normalize-space(.)='Optical Benefit' or contains(normalize-space(.), 'Optical Benefit')]/following-sibling::td[{column}]/select"
            )
            
            if len(optical_selectors) <= 1:
                return await self.select_option_with_error_handling(region, tpa, network, "Optical Benefit", value, column)
            
            wataniatakaful_logger.debug(f"Found {len(optical_selectors)} Optical Benefit fields for column {column}")
            normalized_target = self.normalize_value(value)
            
            for i, selector in enumerate(optical_selectors, 1):
                try:
                    # Get both text and value from options
                    options = await selector.evaluate('''(element) => {
                        return Array.from(element.options).map(opt => ({
                            text: opt.text.trim(),
                            value: opt.value
                        }));
                    }''')
                    
                    wataniatakaful_logger.debug(f"Selector {i} options: {options}")
                    
                    # Try to find matching option
                    for opt in options:
                        normalized_text = self.normalize_value(opt['text'])
                        normalized_value = self.normalize_value(opt['value'])
                        
                        wataniatakaful_logger.debug(f"Comparing target '{normalized_target}' with option text '{normalized_text}' and value '{normalized_value}'")
                        
                        if normalized_target in [normalized_text, normalized_value]:
                            wataniatakaful_logger.debug(f"Found match in selector {i}: {opt}")
                            await selector.select_option(value=opt['value'], timeout=3000)
                            await asyncio.sleep(MAX_SLEEP)
                            wataniatakaful_logger.debug(f"Successfully set Optical Benefit value {value} in selector {i}")
                            return True
                    
                    wataniatakaful_logger.debug(f"No matching option found in selector {i}")
                    
                except Exception as e:
                    wataniatakaful_logger.debug(f"Error processing selector {i}: {e}")
                    continue
            
            wataniatakaful_logger.error(f"Could not set Optical Benefit in any available selector. Value: {value}")
            return False
            
        except Exception as e:
            wataniatakaful_logger.error(f"Error in handle_optical_benefit: {e}")
            return False

    async def fill_category_1(self, catA, region, tpa, network):
        wataniatakaful_logger.debug("Category A Started")
        print('Cat A')
        
        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "wataniatakaful", "WATANIATAKAFUL_3")
        except Exception as e:
            wataniatakaful_logger.error(f"An error occurred while taking screenshot: {e}")
            
        try:
            await self.page.get_by_role("checkbox").check()
            await asyncio.sleep(MAX_SLEEP)
            await asyncio.sleep(MAX_SLEEP)
            wataniatakaful_logger.debug("Checkbox Marked")
        except Exception as e:
            wataniatakaful_logger.error(f"An error occurred while marking the checkbox: {e}")
            return False

        row_count = await self.get_table_rows_count()
        print(f'Total rows in table: {row_count}')

        # Use column 1 for both Aafiya and non-Aafiya
        column = 1

        # if catA['TPA'].iloc[0] == 'Aafiya':
        fields = [
            # {"name": "Plan Name", "value": str(catA['TPA'].iloc[0]), "column": column},
            {"name": "Network", "value": str(catA['Network'].iloc[0]), "column": column},
            {"name": "Sum Insured", "value": str(catA['Annual Limit'].iloc[0]), "column": column},
            {"name": "Geographical Cover", "value": str(catA['Territory'].iloc[0]), "column": column},
            {"name": "Pharmacy Coinsurance", "value": str(catA['Pharmacy'].iloc[0]), "column": column},
            {"name": "Lab. & Diagnostics Coinsurance", "value": str(catA['Lab & Diagnostics Co-pay'].iloc[0]), "column": column},
            
        ]

        

        # Fill each field using dynamic selectors with column specification 
        for field in fields:
            print(field)
            if field["name"] == "Optical Benefit":
                success = await self.handle_optical_benefit(field["value"], field["column"], region, tpa, network)
            else:
                print(field['name'])
                success = await self.select_option_with_error_handling(
                    region,
                    tpa,
                    network,
                    field["name"],
                    field["value"], 
                    column=field.get("column")
                )
            if not success:
                wataniatakaful_logger.error(f"Failed to fill field {field['name']} with value {field['value']}")
                return False
            
        wataniatakaful_logger.debug("Category A Completed")
        print('Category A Completed')
        return True