import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import extract_dropdown_values
from src.utils.logger import qatar_logger

class Category2PageNAS:
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

    async def select_option_with_error_handling(self, region, tpa, network, portal_name, field_name, value, column, use_dynamic_selector=True):
        try:
            selector = self.get_field_selector(field_name, column) if use_dynamic_selector else field_name
            qatar_logger.debug(f"{field_name} Value for Column {column}: (Before Apply) {value}")
            
            # Extract dropdown values with error handling
            try:
                await extract_dropdown_values(self.page, region, tpa, network, field_name, selector, portal_name)
            except Exception as extract_error:
                qatar_logger.warning(f"⚠️ {field_name}: Failed to extract dropdown values - {extract_error}")
                # Continue with selection attempt even if extraction fails
            
            # Apply selection with timeout protection
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=value.rstrip()),
                    timeout=10  # 10 second timeout for selection
                )
                qatar_logger.debug(f"{field_name} Value for Column {column}: (After Apply) {value}")
                await asyncio.sleep(MAX_SLEEP)
                qatar_logger.debug(f"✅ {field_name} Column {column} Filled")
                return True
                
            except asyncio.TimeoutError:
                qatar_logger.error(f"⏰ {field_name}: Selection timeout after 10 seconds - skipping this field")
                return False
            except Exception as select_error:
                qatar_logger.error(f"❌ {field_name}: Selection failed - {select_error}")
                return False
                
        except Exception as e:
            qatar_logger.error(f"❌ Unexpected error in {field_name}: {e}")
            return False

    def normalize_value(self, value):
        """Normalize value for comparison by removing commas and spaces"""
        if not value:
            return ""
        return str(value).replace(',', '').replace(' ', '').strip().lower()

    async def handle_optical_benefit(self, value, column, region, tpa, network, portal_name):
        try:
            optical_selectors = await self.page.query_selector_all(
                f"//td[normalize-space(.)='Optical Benefit' or contains(normalize-space(.), 'Optical Benefit')]/following-sibling::td[{column}]/select"
            )
            
            if len(optical_selectors) <= 1:
                qatar_logger.warning(f"⚠️ Optical Benefit: Only {len(optical_selectors)} selector(s) found for column {column}")
                return await self.select_option_with_error_handling(region, tpa, network, portal_name, "Optical Benefit", value, column)
            
            qatar_logger.debug(f"Found {len(optical_selectors)} Optical Benefit fields for column {column}")
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
                    
                    qatar_logger.debug(f"Selector {i} options: {options}")
                    
                    # Try to find matching option
                    for opt in options:
                        normalized_text = self.normalize_value(opt['text'])
                        normalized_value = self.normalize_value(opt['value'])
                        
                        qatar_logger.debug(f"Comparing target '{normalized_target}' with option text '{normalized_text}' and value '{normalized_value}'")
                        
                        if normalized_target in [normalized_text, normalized_value]:
                            qatar_logger.debug(f"Found match in selector {i}: {opt}")
                            try:
                                await asyncio.wait_for(
                                    selector.select_option(value=opt['value']),
                                    timeout=10  # 10 second timeout for selection
                                )
                                await asyncio.sleep(MAX_SLEEP)
                                qatar_logger.debug(f"✅ Successfully set Optical Benefit value {value} in selector {i}")
                                return True
                            except asyncio.TimeoutError:
                                qatar_logger.error(f"⏰ Optical Benefit: Selection timeout in selector {i}")
                                continue
                    
                    qatar_logger.debug(f"No matching option found in selector {i}")
                    
                except asyncio.TimeoutError:
                    qatar_logger.warning(f"⏰ Optical Benefit: Timeout getting options from selector {i}")
                    continue
                except Exception as e:
                    qatar_logger.debug(f"Error processing selector {i}: {e}")
                    continue
            
            qatar_logger.error(f"❌ Could not set Optical Benefit in any available selector. Value: {value}")
            return False
            
        except Exception as e:
            qatar_logger.error(f"❌ Unexpected error in handle_optical_benefit: {e}")
            return False

    async def fill_category_2(self, catB, region, tpa, network, portal_name):
        qatar_logger.debug("Category B Started")
        print('Cat B')

        row_count = await self.get_table_rows_count()
        print(f'Total rows in table: {row_count}')

        # Use column 2 for both Aafiya and non-Aafiya
        column = 2

        fields = [
            {"name": "Sum Insured", "value": str(catB['Annual Limit'].iloc[0]), "column": column},
            # {"name": "Network", "value": str(catB['Network'].iloc[0]), "column": column},  #need to confirm
            {"name": "Territorial Scope of Coverage", "value": str(catB['Territory'].iloc[0]), "column": column},
            {"name": "IP Coinsurance", "value": str(catB['IP Coinsurance'].iloc[0]), "column": column},
            {"name": "Room type", "value": str(catB['Room Category'].iloc[0]), "column": column},
            {"name": "OP Consultation", "value": str(catB['Deductable'].iloc[0]), "column": column},
            {"name": "OP Services Co-pay", "value": str(catB['Diagnostic Copay'].iloc[0]), "column": column},
            {"name": "Pharmacy Limit", "value": str(catB['Pharmacy Sublimit'].iloc[0]), "column": column},
            {"name": "Pharmacy Co-Pay", "value": str(catB['Pharmacy'].iloc[0]), "column": column},
            {"name": "Prescribed Medicine Type", "value": "Both Branded & Generic Medicine", "column": column},
            {"name": "Physiotherapy", "value": str(catB['Physio'].iloc[0]), "column": column},
            {"name": "Laboratory , Radiology , Pathology and Diagnostic services.", "value": str(catB['Lab & X-Ray'].iloc[0]), "column": column},
            {"name": "X-ray, MRI, CT-scan, Ultra Sound and Endoscopy diagnostic services", "value": str(catB['Diagnostic/Lab Copay'].iloc[0]), "column": column},
            {"name": "Organ Transplantation", "value": str(catB['Organ Transplant'].iloc[0]), "column": column},
            {"name": "New Born Cover", "value": str(catB['New born cover'].iloc[0]), "column": column},
            {"name": "Birth Defects & Congenital Disorders for newborn &/or Deformities", "value": "Covered as per DHA and HAAD Regulation", "column": column},
            {"name": "Repatriation of Mortal Remains to the Country of Domicile", "value": str(catB['Repatriation of Mortal remains'].iloc[0]), "column": column},
            {"name": "Alternative Medicine", "value": str(catB['Alternative Medicine'].iloc[0]), "column": column},  #need to confirm
            {"name": "Psychiatric Benefits", "value": str(catB['Psychiatry'].iloc[0]), "column": column},
            {"name": "Maternity Benefit", "value": str(catB['Maternity In-patient Sublimit'].iloc[0]), "column": column},
            {"name": "Maternity Coinsurance", "value": str(catB['Maternity In-patient Co-pay'].iloc[0]), "column": column},
            {"name": "Dental Benefit", "value": str(catB['Dental'].iloc[0]), "column": column},
            {"name": "Dental Co-pay", "value": str(catB['Dental CO'].iloc[0]), "column": column},
            
        ]

        # Fill each field using dynamic selectors with column specification
        successful_fields = 0
        failed_fields = []
        
        for field in fields:
            field_name = field["name"]
            try:
                if field["name"] == "Optical Benefit":
                    success = await self.handle_optical_benefit(field["value"], field["column"], region, tpa, network, portal_name)
                else:
                    success = await self.select_option_with_error_handling(
                        region,
                        tpa,
                        network,
                        portal_name,
                        field["name"],
                        field["value"], 
                        column=field.get("column")
                    )
                
                if success:
                    successful_fields += 1
                    qatar_logger.info(f"✅ Successfully processed field: {field_name}")
                else:
                    failed_fields.append(field_name)
                    qatar_logger.warning(f"⚠️ Skipping field due to timeout or error: {field_name}")
                    
            except Exception as e:
                failed_fields.append(field_name)
                qatar_logger.error(f"❌ Exception while processing field {field_name}: {e}")
        
        # Log summary
        total_fields = len(fields)
        qatar_logger.info(f"📊 Field processing summary: {successful_fields}/{total_fields} successful")
        
        if failed_fields:
            qatar_logger.warning(f"⚠️ Failed fields: {', '.join(failed_fields)}")
        
        qatar_logger.debug("Category B Completed")
        print('Category B Completed')
        
        # Return True if at least one field was processed successfully
        # This allows the process to continue even if some fields timeout
        return successful_fields > 0