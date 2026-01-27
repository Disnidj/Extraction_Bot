import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import convert_to_int
from src.utils.logger import alittihad_logger

class Category3Page:
    def __init__(self, page):
        self.page = page

    async def get_table_rows_count(self):
        try:
            rows = await self.page.query_selector_all('//table[@class="mt-3 table table-bordered ng-star-inserted"]//tr')
            count = len(rows)
            alittihad_logger.debug(f"Total rows in table: {count}")
            return count
        except Exception as e:
            alittihad_logger.error(f"Error counting table rows: {e}")
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

    async def handle_optical_benefit(self, value, column):
        try:
            optical_selectors = await self.page.query_selector_all(
                f"//td[normalize-space(.)='Optical Benefit' or contains(normalize-space(.), 'Optical Benefit')]/following-sibling::td[{column}]/select"
            )
            
            if len(optical_selectors) <= 1:
                return await self.select_option_with_error_handling("Optical Benefit", value, column)
            
            alittihad_logger.debug(f"Found {len(optical_selectors)} Optical Benefit fields for column {column}")
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
                    
                    alittihad_logger.debug(f"Selector {i} options: {options}")
                    
                    # Try to find matching option
                    for opt in options:
                        normalized_text = self.normalize_value(opt['text'])
                        normalized_value = self.normalize_value(opt['value'])
                        
                        alittihad_logger.debug(f"Comparing target '{normalized_target}' with option text '{normalized_text}' and value '{normalized_value}'")
                        
                        if normalized_target in [normalized_text, normalized_value]:
                            alittihad_logger.debug(f"Found match in selector {i}: {opt}")
                            await selector.select_option(value=opt['value'], timeout=3000)
                            await asyncio.sleep(MAX_SLEEP)
                            alittihad_logger.debug(f"Successfully set Optical Benefit value {value} in selector {i}")
                            return True
                    
                    alittihad_logger.debug(f"No matching option found in selector {i}")
                    
                except Exception as e:
                    alittihad_logger.debug(f"Error processing selector {i}: {e}")
                    continue
            
            alittihad_logger.error(f"Could not set Optical Benefit in any available selector. Value: {value}")
            return False
            
        except Exception as e:
            alittihad_logger.error(f"Error in handle_optical_benefit: {e}")
            return False

    async def fill_category_3(self, catC):
        alittihad_logger.debug("Category C Started")
        print('Cat C')

        row_count = await self.get_table_rows_count()
        print(f'Total rows in table: {row_count}')

        # Use column 3 for both Aafiya and non-Aafiya
        column = 3

        if catC['TPA'].iloc[0] == ' Mednet':
            fields = [
                {"name": "Sum Insured", "value": str(catC['Annual Limit'].iloc[0]), "column": column},
                {"name": "Territorial Scope of Coverage", "value": str(catC['Territory'].iloc[0]), "column": column},
                {"name": "Room type", "value": str(catC['Room Category'].iloc[0]), "column": column},
                {"name": "Hospitalization and Day Treatment", "value": str(catC['Hospital accommodation Room'].iloc[0]), "column": column},
                {"name": "OP Consultation", "value": str(catC['Consultation Limit'].iloc[0]), "column": column},
                {"name": "Pharmacy Limit", "value": str(catC['Limit of Phamacy'].iloc[0]), "column": column},
                {"name": "Pharmacy Co-pay", "value": str(catC['Pharmacy'].iloc[0]), "column": column},
                {"name": "OP Services", "value": str(catC['Op Co Insurance'].iloc[0]), "column": column},
                {"name": "Physiotherapy ( Subject to pre-approval)", "value": str(catC['Physio'].iloc[0]), "column": column},
                {"name": "Organ Transplant", "value": str(catC['Organ Transplant'].iloc[0]), "column": column},
                {"name": "Return Airfare for IP Treatment", "value": str(catC['Airfare for IP Treatment'].iloc[0]), "column": column},
                {"name": "Second Medical Opinion", "value": str(catC['Second Medical Opinion'].iloc[0]), "column": column},
                {"name": "Maternity OP Services", "value": str(catC['Maternity Outpatient limit'].iloc[0]), "column": column},
                {"name": "Maternity IP Services", "value": str(catC['Maternity - Married Females Ip'].iloc[0]), "column": column},
                {"name": "Dental Benefit", "value": str(catC['Dental'].iloc[0]), "column": column},
                {"name": "Dental Co-pay", "value": str(catC['Dental CO'].iloc[0]), "column": column},
                {"name": "Dialysis", "value": str(catC['Renal Dialysis'].iloc[0]), "column": column},             
                {"name": "Optical Benefit", "value": str(catC['Optical'].iloc[0]), "column": column}, 
                {"name": "Optical Co-pay", "value": str(catC['Optical CO'].iloc[0]), "column": column},
                {"name": "Alternative Medicines", "value": str(catC['Alternative Medicine'].iloc[0]), "column": column},
                {"name": "Alternative Medicines co-pay", "value": str(catC['Alternative Medicine Co'].iloc[0]), "column": column},
                {"name": "Psychiatric Benefit", "value": str(catC['Psychiatry'].iloc[0]), "column": column},
                {"name": "Medical Appliances", "value": str(catC['Medical Appliances Sublimit'].iloc[0]), "column": column},
            ]
                
        else:
            # For non-Aafiya TPA
            fields = [
                {"name": "Sum Insured", "value": str(catC['Annual Limit'].iloc[0]), "column": column},
                {"name": "Territorial Scope of Coverage", "value": str(catC['Territory'].iloc[0]), "column": column},
                {"name": "Room type", "value": str(catC['Room Category'].iloc[0]), "column": column},
                {"name": "Hospitalization and Day Treatment", "value": str(catC['Hospital accommodation Room'].iloc[0]), "column": column},
                {"name": "OP Consultation", "value": str(catC['Consultation Limit'].iloc[0]), "column": column},
                {"name": "Pharmacy Limit", "value": str(catC['Limit of Phamacy'].iloc[0]), "column": column},
                {"name": "Pharmacy Co-pay", "value": str(catC['Pharmacy'].iloc[0]), "column": column},
                {"name": "OP Services", "value": str(catC['Op Co Insurance'].iloc[0]), "column": column},
                {"name": "Physiotherapy ( Subject to pre-approval)", "value": str(catC['Physio'].iloc[0]), "column": column},
                {"name": "Organ Transplant", "value": str(catC['Organ Transplant'].iloc[0]), "column": column},
                {"name": "Return Airfare for IP Treatment", "value": str(catC['Airfare for IP Treatment'].iloc[0]), "column": column},
                {"name": "Second Medical Opinion", "value": str(catC['Second Medical Opinion'].iloc[0]), "column": column},
                {"name": "Maternity OP Services", "value": str(catC['Maternity Outpatient limit'].iloc[0]), "column": column},
                {"name": "Maternity IP Services", "value": str(catC['Maternity - Married Females Ip'].iloc[0]), "column": column},
                {"name": "Dental Benefit", "value": str(catC['Dental'].iloc[0]), "column": column},
                {"name": "Dental Co-pay", "value": str(catC['Dental CO'].iloc[0]), "column": column},
                {"name": "Dialysis", "value": str(catC['Renal Dialysis'].iloc[0]), "column": column},             
                {"name": "Optical Benefit", "value": str(catC['Optical'].iloc[0]), "column": column}, 
                {"name": "Optical Co-pay", "value": str(catC['Optical CO'].iloc[0]), "column": column},
                {"name": "Alternative Medicines", "value": str(catC['Alternative Medicine'].iloc[0]), "column": column},
                {"name": "Alternative Medicines co-pay", "value": str(catC['Alternative Medicine Co'].iloc[0]), "column": column},
                {"name": "Psychiatric Benefit", "value": str(catC['Psychiatry'].iloc[0]), "column": column},
                {"name": "Medical Appliances", "value": str(catC['Medical Appliances Sublimit'].iloc[0]), "column": column},
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
                alittihad_logger.error(f"Failed to fill field {field['name']} with value {field['value']}")
                return False
            
        alittihad_logger.debug("Category C Completed")
        print('Category C Completed')
        return True