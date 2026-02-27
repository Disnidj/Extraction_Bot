import asyncio
import re
from src.utils.logger import ison_logger
from src.utils.load_yaml import MED_SLEEP
from src.utils.support_functions import extract_dropdown_values, screenshot_and_compare

class Categories1:

    # Centralized selectors/XPaths
    FIELDS = [
        {"name": "TPA", "column": "TPA", "selector": "#ContentBoady1_ddl_tpa1"},
        {"name": "Plan", "column": "Territory", "selector": "#ContentBoady1_ddl_plan1"},
        {"name": "Network", "column": "Network", "selector": "#ContentBoady1_ddl_network1"},
        {"name": "Annual Limit", "column": "Annual Limit", "selector": "#ContentBoady1_ddl_AnnualMaximumLimit1"},
        {"name": "Deductable", "column": "Deductable", "selector": "#ContentBoady1_ddl_ConsultationDeductible1"},
        {"name": "Lab & Diagnostics Sublimit", "column": "Lab & Diagnostics Sublimit", "selector": "#ContentBoady1_ddl_lab1"},
        {"name": "Medicine", "column": "Medicine", "selector": "#ContentBoady1_ddl_Pharmacy1"},
        {"name": "Maternity Outpatient limit", "column": "Maternity Outpatient limit", "selector": "#ContentBoady1_ddl_Maternity1"},
        {"name": "Maternity In-patient Sublimit", "column": "Maternity In-patient Sublimit", "selector": "#ContentBoady1_ddl_Maternity_IP1"},
        {"name": "Dental", "column": "Dental", "selector": "#ContentBoady1_ddl_Dentben1"},
        {"name": "Optical", "column": "Optical", "selector": "#ContentBoady1_ddl_Optben1"},
        {"name": "Psychiatry", "column": "Psychiatry", "selector": "#ContentBoady1_ddl_psch1"},
        {"name": "Physiotherapy", "column": "Physio", "selector": "#ContentBoady1_ddl_phy1"},
        {"name": "Alternative Medicine", "column": "Alternative Medicine", "selector": "#ContentBoady1_ddl_alterMedben1"},
        {"name": "PreExisting and Chronic Conditions", "column": "PreExisting and Chronic Conditions", "selector": "#ContentBoady1_ddl_preexisting1"},
        {"name": "Shiqinx Vaccine", "column": "Shiqinx Vaccine", "selector": "#ContentBoady1_ddl_health1"}

    ]


    def __init__(self, page, df2, cat1=None):
        self.page = page
        self.df2 = df2
        # cat1 parameter is kept for backward compatibility

    def get_value(self, column_name):
        """Fetch value from specified column in the DataFrame."""
        try:
            return str(self.df2[column_name].values[0]).strip()
        except KeyError:
            error_msg = f"KeyError: '{column_name}' column not found in DataFrame."
            print(error_msg)
            ison_logger.error(error_msg)
            return None
        except IndexError:
            error_msg = f"IndexError: No data found in column '{column_name}'."
            print(error_msg)
            ison_logger.error(error_msg)
            return None

    async def check_for_loading(self, selector, loading_keywords=None):
        """
        Check if dropdown currently contains loading keywords.
        
        Returns:
            bool: True if loading keywords found, False otherwise
        """
        if loading_keywords is None:
            loading_keywords = ["Loading", "..."]
        
        try:
            options = await self.page.eval_on_selector_all(
                f"{selector} option",
                """els => els.map(e => {
                    const text = e.textContent || '';
                    return text.replace(/[\\r\\n]+/g, '').replace(/\\s+/g, '').trim();
                })"""
            )
            
            has_loading = any(
                any(keyword.lower() in (opt or "").lower() for keyword in loading_keywords) 
                for opt in options
            )
            
            return has_loading
            
        except Exception as e:
            ison_logger.debug(f"Error checking for loading: {e}")
            return False

    async def wait_for_dropdown_enabled(self, selector, field_name, timeout=40):
        """Wait until dropdown is both loaded and enabled."""
        end_time = asyncio.get_event_loop().time() + timeout
        
        ison_logger.info(f"🔄 Waiting for {field_name} to be enabled...")
        
        while asyncio.get_event_loop().time() < end_time:
            try:
                # Check if dropdown is enabled
                is_enabled = await self.page.eval_on_selector(
                    selector,
                    "el => !el.disabled"
                )
                
                if is_enabled:
                    # Also check for loading keywords
                    has_loading = await self.check_for_loading(selector)
                    if not has_loading:
                        ison_logger.info(f"✅ {field_name} is enabled and loaded")
                        return True
                
                await asyncio.sleep(2)
                
            except Exception as e:
                ison_logger.debug(f"Error while waiting for enable: {e}")
                await asyncio.sleep(2)

        ison_logger.warning(f"⏰ {field_name} timeout while waiting to be enabled")
        return False

    async def _apply_selection(self, field, df2):
        """Helper method to apply selection for a field with smart loading detection."""
        column_name = field["column"]
        selector = field["selector"]
        field_name = field["name"]
        
        try:
            tpa = str(df2['TPA'].values[0]).strip()
            region = str(df2['Region'].values[0]).strip()
            network = str(df2['Network'].values[0]).strip()

            value = self.get_value(column_name)
            
            if value is None:
                ison_logger.warning(f"⚠️ {field_name}: No value found in column '{column_name}', skipping field")
                return False
            
            ison_logger.info(f'{field_name} (Before Apply): {value}')
            
            # Wait for dropdown to be enabled first
            is_ready = await self.wait_for_dropdown_enabled(selector, field_name)
                
            if not is_ready:
                ison_logger.error(f"❌ {field_name} dropdown timeout - skipping this field")
                return False
                    
            # Extract dropdown values ONLY ONCE after it's ready
            try:
                await extract_dropdown_values(self.page, region, tpa, network, field_name, selector, 'ISON')
            except Exception as extract_error:
                ison_logger.warning(f"⚠️ {field_name}: Failed to extract dropdown values - {extract_error}")
                # Continue with selection attempt even if extraction fails
            
            # Apply selection with timeout protection
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=value),
                    timeout=10  # 10 second timeout for selection
                )
                await asyncio.sleep(MED_SLEEP)
                
                ison_logger.info(f"✅ {field_name} (After Apply): {value}")
                return True
                
            except asyncio.TimeoutError:
                ison_logger.error(f"⏰ {field_name}: Selection timeout after 10 seconds - skipping this field")
                return False
            except Exception as select_error:
                ison_logger.error(f"❌ {field_name}: Selection failed - {select_error}")
                return False
            
        except Exception as e:
            ison_logger.error(f"❌ Unexpected error in {field_name}: {e}")
            return False

    async def categories1_information(self, df2):
        """Apply all category selections from dataframe to the page."""
        ison_logger.info("Filling Category A Information")

        # Screenshot before filling fields
        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "ison", "ISON_3")
        except Exception as e:
            ison_logger.error(f"An error occurred while taking screenshot: {e}")

        # Process each field - continue even if some fields fail
        successful_fields = 0
        failed_fields = []
        
        for field in self.FIELDS:
            field_name = field["name"]
            try:
                if await self._apply_selection(field, df2):
                    successful_fields += 1
                    ison_logger.info(f"✅ Successfully processed field: {field_name}")
                else:
                    failed_fields.append(field_name)
                    ison_logger.warning(f"⚠️ Skipping field due to timeout or error: {field_name}")
            except Exception as e:
                failed_fields.append(field_name)
                ison_logger.error(f"❌ Exception while processing field {field_name}: {e}")
        
        # Log summary
        total_fields = len(self.FIELDS)
        ison_logger.info(f"📊 Field processing summary: {successful_fields}/{total_fields} successful")
        
        if failed_fields:
            ison_logger.warning(f"⚠️ Failed fields: {', '.join(failed_fields)}")
        
        # Return True if at least one field was processed successfully
        # This allows the process to continue even if some fields timeout
        return successful_fields > 0