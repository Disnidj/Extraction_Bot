import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import convert_to_int
from src.utils.logger import medgulf_logger

class Category3Page:
    def __init__(self, page):
        self.page = page

    async def get_table_rows_count(self):
        try:
            rows = await self.page.query_selector_all('//table[@class="mt-3 table table-bordered ng-star-inserted"]//tr')
            count = len(rows)
            medgulf_logger.debug(f"Total rows in table: {count}")
            return count
        except Exception as e:
            medgulf_logger.error(f"Error counting table rows: {e}")
            return 0

    def get_field_selector(self, field_name, column):
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

    async def select_option_with_error_handling(self, field_name, value, column, use_dynamic_selector=True):
        try:
            selector = self.get_field_selector(field_name, column) if use_dynamic_selector else field_name
            cleaned_value = self.clean_value(value)
            medgulf_logger.debug(f"{field_name} Value for Column {column}: (Before Apply) {cleaned_value}")
            await self.page.select_option(selector, value=cleaned_value.rstrip(), timeout=3000)
            medgulf_logger.debug(f"{field_name} Value for Column {column}: (After Apply) {cleaned_value}")
            await asyncio.sleep(MAX_SLEEP)
            medgulf_logger.debug(f"{field_name} Column {column} Filled")
            return True
        except Exception as e:
            medgulf_logger.error(f"Error occurred while selecting {field_name} for Column {column}: {e}")
            return False

    async def handle_routine_health_checkup(self, value, column):
        try:
            routine_health_selectors = await self.page.query_selector_all(
                f"//td[normalize-space(.)='Routine Health Check-up' or contains(normalize-space(.), 'Routine Health Check-up')]/following-sibling::td[{column}]/select"
            )
            
            if len(routine_health_selectors) <= 1:
                return await self.select_option_with_error_handling("Routine Health Check-up", value, column)
            
            medgulf_logger.debug(f"Found {len(routine_health_selectors)} Routine Health Check-up fields for column {column}")
            normalized_target = self.normalize_value(value)
            
            for i, selector in enumerate(routine_health_selectors, 1):
                try:
                    # Get both text and value from options
                    options = await selector.evaluate('''(element) => {
                        return Array.from(element.options).map(opt => ({
                            text: opt.text.trim(),
                            value: opt.value
                        }));
                    }''')
                    
                    medgulf_logger.debug(f"Selector {i} options: {options}")
                    
                    # Try to find matching option
                    for opt in options:
                        normalized_text = self.normalize_value(opt['text'])
                        normalized_value = self.normalize_value(opt['value'])
                        
                        medgulf_logger.debug(f"Comparing target '{normalized_target}' with option text '{normalized_text}' and value '{normalized_value}'")
                        
                        if normalized_target in [normalized_text, normalized_value]:
                            medgulf_logger.debug(f"Found match in selector {i}: {opt}")
                            await selector.select_option(value=opt['value'], timeout=3000)
                            await asyncio.sleep(MAX_SLEEP)
                            medgulf_logger.debug(f"Successfully set Routine Health Check-up value {value} in selector {i}")
                            return True
                    
                    medgulf_logger.debug(f"No matching option found in selector {i}")
                    
                except Exception as e:
                    medgulf_logger.debug(f"Error processing selector {i}: {e}")
                    continue

            medgulf_logger.error(f"Could not set Routine Health Check-up in any available selector. Value: {value}")
            return False
            
        except Exception as e:
            medgulf_logger.error(f"Error in handle_routine_health_checkup: {e}")
            return False

    async def fill_category_3(self, catC):
        medgulf_logger.debug("Category C Started")
        print('Cat C')

        row_count = await self.get_table_rows_count()
        print(f'Total rows in table: {row_count}')

        # Use column 3 for both Nextcare and non-Nextcare
        column = 3

        if catC['TPA'].iloc[0] == 'Nextcare':
            fields = [
                {"name": "Territorial Scope of Coverage", "value": str(catC['Territory'].iloc[0]), "column": column},
                {"name": "Aggregate Annual Limit", "value": str(catC['Annual Limit'].iloc[0]), "column": column},
                # {"name": "Medical Network", "value": str(catC['Network'].iloc[0]), "column": column},

                {"name": "In-patient Room Type", "value": str(catC['Room Category'].iloc[0]), "column": column},
                {"name": "Deductible per Consultation", "value": str(catC['Op Co Insurance'].iloc[0]), "column": column},
                {"name": "Prescribed Drugs & Medicines Annual Limit", "value": str(catC['Alternative Medicine'].iloc[0]), "column": column},
                {"name": "Prescribed Drugs & Medicines Co-pay", "value": str(catC['Alternative Medicine Co'].iloc[0]), "column": column},
                {"name": "Diagnostics Co-pay", "value": str(catC['Lab & Diagnostics Co-pay'].iloc[0]), "column": column},
                {"name": "Dental benefit", "value": str(catC['Dental'].iloc[0]), "column": column},
                {"name": "Optical benefit", "value": str(catC['Optical'].iloc[0]), "column": column},
            ]
        else:
            fields = [
                # {"name": "Network", "value": str(catC['Network'].iloc[0]), "column": column},
                {"name": "Annual Medical Limit", "value": str(catC['Annual Limit'].iloc[0]), "column": column},
                {"name": "Territories covered", "value": str(catC['Territory'].iloc[0]), "column": column},
                {"name": "IP & Day Care Co-pay", "value": str(catC['Diagnostic Copay'].iloc[0]), "column": column},
                {"name": "In-patient Room Type", "value": str(catC['Room Category'].iloc[0]), "column": column},
                {"name": "OP Consultation Co-pay", "value": str(catC['Op Co Insurance'].iloc[0]), "column": column},
                {"name": "OP Diagnostics Co-pay", "value": str(catC['Diagnostic/Lab Copay'].iloc[0]), "column": column},
                {"name": "Pharmacy Limit", "value": str(catC['Limit of Phamacy'].iloc[0]), "column": column},
                {"name": "Pharmacy Co-pay", "value": str(catC['Pharmacy'].iloc[0]), "column": column},
                {"name": "Prescribed Medicine Type", "value": str(catC['Medicine'].iloc[0]), "column": column},
                {"name": "Physiotherapy", "value": str(catC['Physio'].iloc[0]), "column": column},
                {"name": "Physiotherapy Co-pay", "value": str(catC['Physio Co'].iloc[0]), "column": column},
                {"name": "Nursing at home", "value": str(catC['Home Nursing Charges'].iloc[0]), "column": column},
                {"name": "Repatriation of Mortal Remains", "value": str(catC['Repatriation of Mortal remains'].iloc[0]), "column": column},
                {"name": "Alternative Medicine Limit", "value": str(catC['Alternative Medicine'].iloc[0]), "column": column},
                {"name": "Alternative Medicine Co-pay", "value": str(catC['Alternative Medicine Co'].iloc[0]), "column": column},
                {"name": "OP Psychiatric Benefits Limit", "value": str(catC['Renal Dialysis'].iloc[0]), "column": column}, 
                {"name": "OP Psychiatric Co-pay", "value": str(catC['Psychiatry'].iloc[0]), "column": column},
                {"name": "Maternity benefit limit", "value": str(catC['Maternity - Married Females'].iloc[0]), "column": column},
                {"name": "Maternity benefit co-pay", "value": str(catC['Maternity - Married Females CO'].iloc[0]), "column": column},
                {"name": "Dental benefit limit", "value": str(catC['Dental'].iloc[0]), "column": column},
                {"name": "Dental Co-pay", "value": str(catC['Dental CO'].iloc[0]), "column": column},
                {"name": "Optical benefit limit", "value": str(catC['Optical'].iloc[0]), "column": column},
                {"name": "Optical Co-pay", "value": str(catC['Optical CO'].iloc[0]), "column": column},
                {"name": "Routine Health Check-up", "value": str(catC['Telehealth Consultation'].iloc[0]), "column": column},
            ]

        for field in fields:
            if field["name"] == "Routine Health Check-up":
                success = await self.handle_routine_health_checkup(field["value"], field["column"])
            else:
                success = await self.select_option_with_error_handling(
                    field["name"],
                    field["value"], 
                    column=field.get("column")
                )
            if not success:
                medgulf_logger.error(f"Failed to fill field {field['name']} with value {field['value']}")
                return False
            
        medgulf_logger.debug("Category C Completed")
        print('Category C Completed')
        return True