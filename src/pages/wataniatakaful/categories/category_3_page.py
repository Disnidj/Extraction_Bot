# import time
# from src.utils.support_functions import convert_to_int
# from src.utils.logger import logger

# class Category3Page:
#     def __init__(self, page, df3, cat1):
#         self.page = page
#         self.df3 = df3

#     def get_value(self, column_name):
#         try:
#             # Fetch value from the specific column and convert to string
#             return str(self.df3[column_name].values[2])
#         except KeyError:
#             print(f"KeyError: '{column_name}' column not found in DataFrame.")
#             return None
#         except IndexError:
#             print(f"IndexError: No data found in column '{column_name}'.")
#             return None

#     async def categories3_information(self):

#                 # Network
#         network = self.get_value("Network")
#         print(network)
#         await self.page.select_option('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[4]/td[2]/select', value=network)
#         time.sleep(4)
#         print('network')

#         # Sum Insured
#         sum_insured = self.get_value("Annual Limit")
#         print(sum_insured)
#         await self.page.select_option('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[5]/td[2]/select', value=sum_insured)
#         time.sleep(3)
#         print('select plan')

#         # Geographical Cover
#         territory = self.get_value("Territory")
#         print(territory)
#         await self.page.select_option('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[6]/td[2]/select/option[2]', value=territory)
#         time.sleep(3)
#         print('Territory')

#         # Pharmacy Coinsurance
#         pharmacy = self.get_value("Pharmacy")
#         print(pharmacy)
#         await self.page.select_option('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[7]/td[2]/select', value=pharmacy)
#         time.sleep(3)
#         print('Pharmacy')

#         # Lab. & Diagnostics Coinsurance
#         lb = self.get_value("Lab & Diagnostics Co-pay")
#         print(lb)
#         await self.page.select_option('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[8]/td[2]/select', value=lb)
#         time.sleep(3)
#         print('Lab & Diagnostics Co-pay')
    


import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import convert_to_int
from src.utils.logger import wataniatakaful_logger

class Category3Page:
    def __init__(self, page):
        self.page = page

    async def get_table_rows_count(self):
        try:
            rows = await self.page.query_selector_all('//table[@class="mt-3 table table-bordered ng-star-inserted"]//tr')
            count = len(rows)
            wataniatakaful_logger.debug(f"Total rows in table: {count}")
            return count
        except Exception as e:
            wataniatakaful_logger.error(f"Error counting table rows: {e}")
            return 0

    def get_field_selector(self, field_name, column):
        # More specific XPath that handles both exact and partial matches
        return f"//td[normalize-space(.)='{field_name}' or contains(normalize-space(.), '{field_name}')]/following-sibling::td[{column}]/select"

    async def select_option_with_error_handling(self, field_name, value, column, use_dynamic_selector=True):
        try:
            selector = self.get_field_selector(field_name, column) if use_dynamic_selector else field_name
            wataniatakaful_logger.debug(f"{field_name} Value for Column {column}: (Before Apply) {value}")
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

    async def handle_optical_benefit(self, value, column):
        try:
            optical_selectors = await self.page.query_selector_all(
                f"//td[normalize-space(.)='Optical Benefit' or contains(normalize-space(.), 'Optical Benefit')]/following-sibling::td[{column}]/select"
            )
            
            if len(optical_selectors) <= 1:
                return await self.select_option_with_error_handling("Optical Benefit", value, column)
            
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

    async def fill_category_3(self, catC):
        wataniatakaful_logger.debug("Category C Started")
        print('Cat C')

        row_count = await self.get_table_rows_count()
        print(f'Total rows in table: {row_count}')

        # Use column 3 for both Aafiya and non-Aafiya
        column = 3

        if catC['TPA'].iloc[0] == 'Aafiya':
            fields = [
                {"name": "Plan Name", "value": str(catC['TPA'].iloc[0]), "column": column},
                {"name": "Network", "value": str(catC['Network'].iloc[0]), "column": column},
                {"name": "Sum Insured", "value": str(catC['Annual Limit'].iloc[0]), "column": column},
                {"name": "Geographical Cover", "value": str(catC['Territory'].iloc[0]), "column": column},
                {"name": "Pharmacy Coinsurance", "value": str(catC['Pharmacy'].iloc[0]), "column": column},
                {"name": "Lab. & Diagnostics Coinsurance", "value": str(catC['Lab & Diagnostics Co-pay'].iloc[0]), "column": column},
                
            ]
        else:
            fields = [
                {"name": "Plan Name", "value": str(catC['TPA'].iloc[0]), "column": column},
                {"name": "Network", "value": str(catC['Network'].iloc[0]), "column": column},
                {"name": "Sum Insured", "value": str(catC['Annual Limit'].iloc[0]), "column": column},
                {"name": "Geographical Cover", "value": str(catC['Territory'].iloc[0]), "column": column},
                {"name": "Pharmacy Coinsurance", "value": str(catC['Pharmacy'].iloc[0]), "column": column},
                {"name": "Lab. & Diagnostics Coinsurance", "value": str(catC['Lab & Diagnostics Co-pay'].iloc[0]), "column": column},
                
            ]

        for field in fields:
            if field["name"] == "Optical Benefit":
                success = await self.handle_optical_benefit(field["value"], field["column"])
            else:
                success = await self.select_option_with_error_handling(
                    field["name"],
                    field["value"], 
                    column=field.get("column")
                )
            if not success:
                wataniatakaful_logger.error(f"Failed to fill field {field['name']} with value {field['value']}")
                return False
            
        wataniatakaful_logger.debug("Category C Completed")
        print('Category C Completed')
        return True