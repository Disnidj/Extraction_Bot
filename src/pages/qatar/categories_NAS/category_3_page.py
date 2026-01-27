import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import convert_to_int
from src.utils.logger import qatar_logger

class Category3PageNAS:
    def __init__(self, page):
        self.page = page

    async def get_table_rows_count(self):
        try:
            rows = await self.page.query_selector_all('//table[@class="mt-3 table table-bordered ng-star-inserted"]//tr')
            count = len(rows)
            qatar_logger.debug(f"Total rows in table: {count}")
            return count
        except Exception as e:
            qatar_logger.error(f"Error counting table rows: {e}")
            return 0

    def get_field_selector(self, field_name, column):
        # More specific XPath that handles both exact and partial matches
        return f"//td[normalize-space(.)='{field_name}' or contains(normalize-space(.), '{field_name}')]/following-sibling::td[{column}]/select"

    async def select_option_with_error_handling(self, field_name, value, column, use_dynamic_selector=True):
        try:
            selector = self.get_field_selector(field_name, column) if use_dynamic_selector else field_name
            qatar_logger.debug(f"{field_name} Value for Column {column}: (Before Apply) {value}")
            await self.page.select_option(selector, value=value.rstrip(), timeout=3000)
            qatar_logger.debug(f"{field_name} Value for Column {column}: (After Apply) {value}")
            await asyncio.sleep(MAX_SLEEP)
            qatar_logger.debug(f"{field_name} Column {column} Filled")
            return True
        except Exception as e:
            qatar_logger.error(f"Error occurred while selecting {field_name} for Column {column}: {e}")
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
            
            qatar_logger.debug(f"Found {len(optical_selectors)} Optical Benefit fields for column {column}")
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
                    
                    qatar_logger.debug(f"Selector {i} options: {options}")
                    
                    # Try to find matching option
                    for opt in options:
                        normalized_text = self.normalize_value(opt['text'])
                        normalized_value = self.normalize_value(opt['value'])
                        
                        qatar_logger.debug(f"Comparing target '{normalized_target}' with option text '{normalized_text}' and value '{normalized_value}'")
                        
                        if normalized_target in [normalized_text, normalized_value]:
                            qatar_logger.debug(f"Found match in selector {i}: {opt}")
                            await selector.select_option(value=opt['value'], timeout=3000)
                            await asyncio.sleep(MAX_SLEEP)
                            qatar_logger.debug(f"Successfully set Optical Benefit value {value} in selector {i}")
                            return True
                    
                    qatar_logger.debug(f"No matching option found in selector {i}")
                    
                except Exception as e:
                    qatar_logger.debug(f"Error processing selector {i}: {e}")
                    continue
            
            qatar_logger.error(f"Could not set Optical Benefit in any available selector. Value: {value}")
            return False
            
        except Exception as e:
            qatar_logger.error(f"Error in handle_optical_benefit: {e}")
            return False

    async def fill_category_3(self, catC):
        qatar_logger.debug("Category C Started")
        print('Cat C')

        row_count = await self.get_table_rows_count()
        print(f'Total rows in table: {row_count}')

        # Use column 3 for both Aafiya and non-Aafiya
        column = 3

        
        fields = [
            {"name": "Sum Insured", "value": str(catC['Annual Limit'].iloc[0]), "column": column},
            # {"name": "Network", "value": str(catC['Network'].iloc[0]), "column": column},  #need to confirm
            {"name": "Territorial Scope of Coverage", "value": str(catC['Territory'].iloc[0]), "column": column},
            {"name": "IP Coinsurance", "value": str(catC['IP Coinsurance'].iloc[0]), "column": column},
            {"name": "Room type", "value": str(catC['Room Category'].iloc[0]), "column": column},
            {"name": "OP Consultation", "value": str(catC['Deductable'].iloc[0]), "column": column},
            {"name": "OP Services Co-pay", "value": str(catC['Diagnostic Copay'].iloc[0]), "column": column},
            {"name": "Pharmacy Limit", "value": str(catC['Pharmacy Sublimit'].iloc[0]), "column": column},
            {"name": "Pharmacy Co-Pay", "value": str(catC['Pharmacy'].iloc[0]), "column": column},
            {"name": "Prescribed Medicine Type", "value": "Both Branded & Generic Medicine", "column": column},
            {"name": "Physiotherapy", "value": str(catC['Physio'].iloc[0]), "column": column},
            {"name": "Laboratory , Radiology , Pathology and Diagnostic services.", "value": str(catC['Lab & X-Ray'].iloc[0]), "column": column},
            {"name": "X-ray, MRI, CT-scan, Ultra Sound and Endoscopy diagnostic services", "value": str(catC['Diagnostic/Lab Copay'].iloc[0]), "column": column},
            {"name": "Organ Transplantation", "value": str(catC['Organ Transplant'].iloc[0]), "column": column},
            {"name": "New Born Cover", "value": str(catC['New born cover'].iloc[0]), "column": column},
            {"name": "Birth Defects & Congenital Disorders for newborn &/or Deformities", "value": "Covered as per DHA and HAAD Regulation", "column": column},
            {"name": "Repatriation of Mortal Remains to the Country of Domicile", "value": str(catC['Repatriation of Mortal remains'].iloc[0]), "column": column},
            {"name": "Alternative Medicine", "value": str(catC['Alternative Medicine'].iloc[0]), "column": column},  #need to confirm
            {"name": "Psychiatric Benefits", "value": str(catC['Psychiatry'].iloc[0]), "column": column},
            {"name": "Maternity Benefit", "value": str(catC['Maternity In-patient Sublimit'].iloc[0]), "column": column},
            {"name": "Maternity Coinsurance", "value": str(catC['Maternity In-patient Co-pay'].iloc[0]), "column": column},
            {"name": "Dental Benefit", "value": str(catC['Dental'].iloc[0]), "column": column},
            {"name": "Dental Co-pay", "value": str(catC['Dental CO'].iloc[0]), "column": column},
            
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
                qatar_logger.error(f"Failed to fill field {field['name']} with value {field['value']}")
                return False
            
        qatar_logger.debug("Category C Completed")
        print('Category C Completed')
        return True