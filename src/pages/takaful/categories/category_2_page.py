import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import extract_dropdown_values 
from src.utils.logger import takaful_logger

class Category2Page:
    def __init__(self, page):
        self.page = page

    async def get_table_rows_count(self):
        try:
            rows = await self.page.query_selector_all('//table[@class="mt-3 table table-bordered ng-star-inserted"]//tr')
            count = len(rows)
            takaful_logger.debug(f"Total rows in table: {count}")
            return count
        except Exception as e:
            takaful_logger.error(f"Error counting table rows: {e}")
            return 0

    def get_field_selector(self, field_name, column=1):
        # More specific XPath that handles both exact and partial matches
        return f"//td[normalize-space(.)='{field_name}' or contains(normalize-space(.), '{field_name}')]/following-sibling::td[{column}]/select"

    def clean_value(self, value):
        """Clean numeric values by removing .0 suffix while preserving strings"""
        if not value:
            return ""
        
        # Convert to string if not already
        value_str = str(value).strip()
        
        try:
            # Check if it's a numeric value
            float_val = float(value_str)
            # If it's a whole number, convert to int
            if float_val.is_integer():
                return str(int(float_val))
            return value_str
        except ValueError:
            # If conversion fails, it's a non-numeric string
            return value_str

    def normalize_value(self, value):
        """Normalize value for comparison by removing commas and spaces"""
        if not value:
            return ""
        # First clean the value to handle .0 suffix
        cleaned = self.clean_value(value)
        return str(cleaned).replace(',', '').replace(' ', '').strip().lower()

    async def select_option_with_error_handling(self, region, tpa, network, field_name, value, column, use_dynamic_selector=True):
        try:
            selector = self.get_field_selector(field_name, column) if use_dynamic_selector else field_name
            cleaned_value = self.clean_value(value)
            takaful_logger.debug(f"{field_name} Value for Column {column}: (Before Apply) {cleaned_value}")
            await extract_dropdown_values(self.page, region, tpa, network, field_name, selector, 'TAKAFUL EMARAT')
            await self.page.select_option(selector, value=cleaned_value.rstrip(), timeout=3000)
            takaful_logger.debug(f"{field_name} Value for Column {column}: (After Apply) {cleaned_value}")
            await asyncio.sleep(MAX_SLEEP)
            takaful_logger.debug(f"{field_name} Column {column} Filled")
            return True
        except Exception as e:
            takaful_logger.error(f"Error occurred while selecting {field_name} for Column {column}: {e}")
            return False

    async def handle_optical_benefit(self, value, column, region, tpa, network):
        try:
            optical_selectors = await self.page.query_selector_all(
                f"//td[normalize-space(.)='Optical Benefit' or contains(normalize-space(.), 'Optical Benefit')]/following-sibling::td[{column}]/select"
            )
            
            if len(optical_selectors) <= 1:
                return await self.select_option_with_error_handling(region, tpa, network,"Optical Benefit", value, column)
            
            takaful_logger.debug(f"Found {len(optical_selectors)} Optical Benefit fields for column {column}")
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
                    
                    takaful_logger.debug(f"Selector {i} options: {options}")
                    
                    # Try to find matching option
                    for opt in options:
                        normalized_text = self.normalize_value(opt['text'])
                        normalized_value = self.normalize_value(opt['value'])
                        
                        takaful_logger.debug(f"Comparing target '{normalized_target}' with option text '{normalized_text}' and value '{normalized_value}'")
                        
                        if normalized_target in [normalized_text, normalized_value]:
                            takaful_logger.debug(f"Found match in selector {i}: {opt}")
                            await selector.select_option(value=opt['value'], timeout=3000)
                            await asyncio.sleep(MAX_SLEEP)
                            takaful_logger.debug(f"Successfully set Optical Benefit value {value} in selector {i}")
                            return True
                    
                    takaful_logger.debug(f"No matching option found in selector {i}")
                    
                except Exception as e:
                    takaful_logger.debug(f"Error processing selector {i}: {e}")
                    continue
            
            takaful_logger.error(f"Could not set Optical Benefit in any available selector. Value: {value}")
            return False
            
        except Exception as e:
            takaful_logger.error(f"Error in handle_optical_benefit: {e}")
            return False

    async def fill_category_2(self, catB, region, tpa, network):
        takaful_logger.debug("Category B Started")
        print('Cat B')
        
        row_count = await self.get_table_rows_count()
        print(f'Total rows in table: {row_count}')

        # Use column 2 for both Aafiya and non-Aafiya
        column = 2
        if catB['TPA'].iloc[0] == 'Aafiya':
            fields = [
                {"name": "Sum Insured", "value": str(catB['Annual Limit'].iloc[0]), "column": column},
                {"name": "Geographical Area of Cover", "value": str(catB['Territory'].iloc[0]), "column": column},
                {"name": "Room Category", "value": str(catB['Room Category'].iloc[0]), "column": column},
                {"name": "Organ Transplant", "value": str(catB['Organ Transplant'].iloc[0]), "column": column},
                {"name": "OP Consultation", "value": str(catB['Deductable'].iloc[0]), "column": column},
                {"name": "OP Services - Lab, Radiology, etc", "value": str(catB['Op Co Insurance'].iloc[0]), "column": column},
                {"name": "Physiotherapy treatment, subject to prior approval", "value": str(catB['Physio'].iloc[0]), "column": column},
                {"name": "Pharmacy Limit", "value": str(catB['Limit of Phamacy'].iloc[0]), "column": column},
                {"name": "Pharmacy Co-pay", "value": str(catB['Pharmacy'].iloc[0]), "column": column},
                {"name": "Maternity OP Services", "value": str(catB['Maternity - Married Females CO'].iloc[0]), "column": column},
                {"name": "Maternity IP Services", "value": str(catB['Maternity - Married Females Ip'].iloc[0]), "column": column},
                {"name": "New born cover", "value": str(catB['New born cover'].iloc[0]), "column": column},
                {"name": "Alternative Medicine", "value": str(catB['Alternative Medicine'].iloc[0]), "column": column},
                {"name": "Dental Benefit", "value": str(catB['Dental'].iloc[0]), "column": column},
                {"name": "Dental Co-pay", "value": str(catB['Dental CO'].iloc[0]), "column": column},
                {"name": "Air Ticket (Referral from Insurance Company)", "value": str(catB['Airfare for IP Treatment'].iloc[0]), "column": column},
                {"name": "Shingrix Vaccine", "value": str(catB['Shiqinx Vaccine'].iloc[0]), "column": column}, 
                {"name": "Optical Co-pay", "value": str(catB['Optical CO'].iloc[0]), "column": column},
                {"name": "Optical Benefit", "value": str(catB['Optical'].iloc[0]), "column": column},
            ]
                
        else:
            # For non-Aafiya TPA
            fields = [
                {"name": "Sum Insured", "value": str(catB['Annual Limit'].iloc[0]), "column": column},#
                {"name": "Territorial Scope of Coverage", "value": str(catB['Territory'].iloc[0]), "column": column},#
                {"name": "Room type", "value": str(catB['Room Category'].iloc[0]), "column": column},
                {"name": "OP Consultation", "value": str(catB['Deductable'].iloc[0]), "column": column},#
                {"name": "Pharmacy Limit", "value": str(catB['Limit of Phamacy'].iloc[0]), "column": column},#
                {"name": "Pharmacy Co-pay", "value": str(catB['Pharmacy'].iloc[0]), "column": column},#
                {"name": "OP Services", "value": str(catB['Op Co Insurance'].iloc[0]), "column": column},
                {"name": "Physiotherapy ( Subject to pre-approval)", "value": str(catB['Physio'].iloc[0]), "column": column},#
                {"name": "Organ Transplant", "value": str(catB['Organ Transplant'].iloc[0]), "column": column},#
                {"name": "Return Airfare for IP Treatment", "value": str(catB['Airfare for IP Treatment'].iloc[0]), "column": column},#
                {"name": "Maternity OP Services", "value": str(catB['Maternity - Married Females CO'].iloc[0]), "column": column},
                {"name": "Maternity IP Services", "value": str(catB['Maternity - Married Females Ip'].iloc[0]), "column": column},
                {"name": "New born cover", "value": str(catB['New born cover'].iloc[0]), "column": column},#
                {"name": "Dental Benefit", "value": str(catB['Dental'].iloc[0]), "column": column},#
                {"name": "Dental Co-pay", "value": str(catB['Dental CO'].iloc[0]), "column": column},#
                {"name": "Shingrix Vaccine", "value": str(catB['Shiqinx Vaccine'].iloc[0]), "column": column},
                {"name": "Optical Benefit", "value": str(catB['Optical'].iloc[0]), "column": column},#
                {"name": "Optical Co-pay", "value": str(catB['Optical CO'].iloc[0]), "column": column},#
                {"name": "Alternative Medicines", "value": str(catB['Alternative Medicine'].iloc[0]), "column": column},#
                {"name": "Alternative Medicines co-pay", "value": str(catB['Alternative Medicine Co'].iloc[0]), "column": column},
                {"name": "Psychiatric Benefit", "value": str(catB['Psychiatry'].iloc[0]), "column": column},#
            ]
        
        # Fill each field using dynamic selectors with column specification 
        for field in fields:
            if field["name"] == "Optical Benefit":
                success = await self.handle_optical_benefit(field["value"], field["column"], region, tpa, network)
            else:
                success = await self.select_option_with_error_handling(
                    region,
                    tpa,
                    network,
                    field["name"],
                    field["value"], 
                    column=field.get("column")
                )
            if not success:
                takaful_logger.error(f"Failed to fill field {field['name']} with value {field['value']}")
                return False
            
        takaful_logger.debug("Category B Completed")
        print('Category B Completed')
        return True