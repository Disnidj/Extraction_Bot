import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import extract_dropdown_values, screenshot_and_compare
from src.utils.logger import fidelity_logger

class Category1Page:
    def __init__(self, page, portal_name):
        self.page = page
        self.portal_name = portal_name

    async def get_table_rows_count(self):
        try:
            rows = await self.page.query_selector_all('//table[@class="mt-3 table table-bordered ng-star-inserted"]//tr')
            count = len(rows)
            fidelity_logger.debug(f"Total rows in table: {count}")
            return count
        except Exception as e:
            fidelity_logger.error(f"Error counting table rows: {e}")
            return 0
        
    def get_field_selector(self, field_name, column=1):
        # Get nth select element for the field based on column number (1-based index)
        return f"//td[normalize-space(.)='{field_name}']/following-sibling::td[{column}]/select"
        

    def clean_value(self, value):
        """Clean numeric values by removing .0 suffix while preserving strings"""
        if not value:
            return ""
        value_str = str(value).strip()
        try:
            float_val = float(value_str)
            if float_val.is_integer():
                return str(int(float_val))
            return value_str
        except ValueError:
            return value_str

    def normalize_value(self, value):
        """Normalize value for comparison by removing commas and spaces"""
        if not value:
            return ""
        cleaned = self.clean_value(value)
        return str(cleaned).replace(',', '').replace(' ', '').strip().lower()

    async def select_option_with_error_handling(self, region, tpa, network, field_name, value, column, use_dynamic_selector=True):
        try:
            selector = self.get_field_selector(field_name, column) if use_dynamic_selector else field_name
            cleaned_value = self.clean_value(value)
            fidelity_logger.debug(f"{field_name} Value for Column {column}: (Before Apply) {cleaned_value}")
            
            # Extract dropdown values with error handling
            try:
                await extract_dropdown_values(self.page, region, tpa, network, field_name, selector, self.portal_name)
            except Exception as extract_error:
                fidelity_logger.warning(f"⚠️ {field_name}: Failed to extract dropdown values - {extract_error}")
                # Continue with selection attempt even if extraction fails

            # Apply selection with timeout protection
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=cleaned_value.rstrip()),
                    timeout=10  # 10 second timeout for selection
                )
                fidelity_logger.debug(f"{field_name} Value for Column {column}: (After Apply) {cleaned_value}")
                await asyncio.sleep(MAX_SLEEP)
                fidelity_logger.debug(f"✅ {field_name} Column {column} Filled")
                return True
                
            except asyncio.TimeoutError:
                fidelity_logger.error(f"⏰ {field_name}: Selection timeout after 10 seconds - skipping this field")
                return False
            except Exception as select_error:
                fidelity_logger.error(f"❌ {field_name}: Selection failed - {select_error}")
                return False
                
        except Exception as e:
            fidelity_logger.error(f"❌ Unexpected error in {field_name}: {e}")
            return False

    async def handle_optical_benefit(self, value, column, region, tpa, network):
        try:
            optical_selectors = await self.page.query_selector_all(
                f"//td[normalize-space(.)='Optical benefit limit' or contains(normalize-space(.), 'Optical benefit limit')]/following-sibling::td[{column}]/select"
            )
            if len(optical_selectors) <= 1:
                fidelity_logger.warning(f"⚠️ Optical benefit limit: Only {len(optical_selectors)} selector(s) found for column {column}")
                return await self.select_option_with_error_handling(region, tpa, network, "Optical benefit limit", value, column)
            
            fidelity_logger.debug(f"Found {len(optical_selectors)} Optical benefit limit fields for column {column}")
            normalized_target = self.normalize_value(value)
            
            for i, selector in enumerate(optical_selectors, 1):
                try:
                    # Get both text and value from options with timeout protection
                    options = await asyncio.wait_for(
                        selector.evaluate('''(element) => {
                            return Array.from(element.options).map(opt => ({
                                text: opt.text.trim(),
                                value: opt.value
                            }));
                        }'''),
                        timeout=5  # 5 second timeout for evaluation
                    )
                    
                    fidelity_logger.debug(f"Selector {i} options: {options}")
                    
                    for opt in options:
                        normalized_text = self.normalize_value(opt['text'])
                        normalized_value = self.normalize_value(opt['value'])
                        fidelity_logger.debug(f"Comparing target '{normalized_target}' with option text '{normalized_text}' and value '{normalized_value}'")
                        
                        if normalized_target in [normalized_text, normalized_value]:
                            fidelity_logger.debug(f"Found match in selector {i}: {opt}")
                            try:
                                await asyncio.wait_for(
                                    selector.select_option(value=opt['value']),
                                    timeout=10  # 10 second timeout for selection
                                )
                                await asyncio.sleep(MAX_SLEEP)
                                fidelity_logger.debug(f"✅ Successfully set Optical Benefit value {value} in selector {i}")
                                return True
                            except asyncio.TimeoutError:
                                fidelity_logger.error(f"⏰ Optical benefit limit: Selection timeout in selector {i}")
                                continue
                    
                    fidelity_logger.debug(f"No matching option found in selector {i}")
                    
                except asyncio.TimeoutError:
                    fidelity_logger.warning(f"⏰ Optical benefit limit: Timeout getting options from selector {i}")
                    continue
                except Exception as e:
                    fidelity_logger.debug(f"Error processing selector {i}: {e}")
                    continue
            
            fidelity_logger.error(f"❌ Could not set Optical Benefit in any available selector. Value: {value}")
            return False
            
        except Exception as e:
            fidelity_logger.error(f"❌ Unexpected error in handle_optical_benefit: {e}")
            return False

    async def fill_category_1(self, catA, region, tpa, network):
        fidelity_logger.debug("Category A Started")
        print('Category A Started')

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "fidelity", "FIDELITY_3")
            await asyncio.sleep(10)
        except Exception as e:
            fidelity_logger.error(f"An error occurred while taking screenshot: {e}")

        column = 1

        # Fidelity-specific field mapping
        if str(catA['Plan Selection'].iloc[0]).strip() == "NextcareEmployees Guard - Plan 1 - 5":
            fields = [
                {"name": "Territorial Scope of Coverage", "value": str(catA['Territory'].iloc[0]), "column": column},
                {"name": "Aggregate Annual Limit", "value": str(catA['Annual Limit'].iloc[0]), "column": column},
                {"name": "Medical Network", "value": str(catA['Pharmacy Sublimit'].iloc[0]), "column": column},
                {"name": "Room type", "value": str(catA['Room Category'].iloc[0]), "column": column},
                {"name": "Deductible per Consultation", "value": str(catA['Deductable'].iloc[0]), "column": column},
                {"name": "Prescribed Drugs & Medicines", "value": str(catA['Limit of Phamacy'].iloc[0]), "column": column},
                {"name": "Pharmacy Co-pay", "value": str(catA['Pharmacy'].iloc[0]), "column": column},
                {"name": "Diagnostics Co-pay", "value": str(catA['Diagnostic/Lab Copay'].iloc[0]), "column": column},
                {"name": "Dental benefit", "value": str(catA['Dental'].iloc[0]), "column": column},
                {"name": "Optical benefit limit", "value": str(catA['Optical'].iloc[0]), "column": column},
            ]
        else:
            fields = [
                # {"name": "Network", "value": str(catA['Network'].iloc[0]), "column": column},
                # {"name": "Plan", "value": str(catA['Sub Plan'].iloc[0]), "column": column},
                {"name": "Annual Limit", "value": str(catA['Annual Limit'].iloc[0]), "column": column},
                {"name": "Territories covered", "value": str(catA['Territory'].iloc[0]), "column": column},
                {"name": "Inpatient Co-Pay", "value": str(catA['IP Coinsurance'].iloc[0]), "column": column},
                {"name": "OP Consultation Deductible", "value": str(catA['Deductable'].iloc[0]), "column": column},
                {"name": "OP services co-pay", "value": str(catA['PreExisting and Chronic Conditions'].iloc[0]), "column": column},
                {"name": "Prescribed Medicines - Limit", "value": str(catA['Limit of Phamacy'].iloc[0]), "column": column},
                {"name": "Prescribed Medicines - Coinsurance", "value": str(catA['Pharmacy'].iloc[0]), "column": column},
                {"name": "Maternity benefit limit", "value": str(catA['Maternity - Married Females'].iloc[0]), "column": column},
                {"name": "Dental benefit limit", "value": str(catA['Dental'].iloc[0]), "column": column},
                {"name": "Optical benefit limit", "value": str(catA['Optical'].iloc[0]), "column": column},
            ]

        # Fill each field using dynamic selectors with column specification
        successful_fields = 0
        failed_fields = []
        
        for field in fields:
            field_name = field["name"]
            try:
                if not field["value"] or field["value"].lower() == "none":
                    fidelity_logger.warning(f"⚠️ Field {field['name']} has no value, skipping.")
                    failed_fields.append(field_name)
                    continue
                    
                if field["name"] == "Optical benefit limit":
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
                
                if success:
                    successful_fields += 1
                    fidelity_logger.info(f"✅ Successfully processed field: {field_name}")
                else:
                    failed_fields.append(field_name)
                    fidelity_logger.warning(f"⚠️ Skipping field due to timeout or error: {field_name}")
                    
            except Exception as e:
                failed_fields.append(field_name)
                fidelity_logger.error(f"❌ Exception while processing field {field_name}: {e}")
        
        # Log summary
        total_fields = len(fields)
        fidelity_logger.info(f"📊 Field processing summary: {successful_fields}/{total_fields} successful")
        
        if failed_fields:
            fidelity_logger.warning(f"⚠️ Failed fields: {', '.join(failed_fields)}")

        fidelity_logger.debug("Category A Completed")
        print('Category A Completed')
        
        # Return True if at least one field was processed successfully
        # This allows the process to continue even if some fields timeout
        return successful_fields > 0