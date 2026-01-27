import asyncio
import os
from src.utils.logger import ison_logger
from src.utils.load_yaml import MED_SLEEP

class Categories3:

    
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
    
    # Download related selectors
    DOWNLOAD_SELECTORS = {
        "get_quote_button": "#ContentBoady1_btn_quote",
        "download_button": "#ContentBoady1_btn_submit"
    }

    def __init__(self, page, df2, cat3=None):
        self.page = page
        self.df2 = df2
        # cat3 parameter is kept for backward compatibility

    def get_value(self, column_name):
        """Fetch value from specified column in the DataFrame."""
        try:
            # Fetch value from the specific column and convert to string
            # Note: Using index 1 for Category C (same as Category B)
            return str(self.df2[column_name].values[1]).strip()
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

    async def _apply_selection(self, field):
        try:
            """Helper method to apply selection for a field."""
            column_name = field["column"]
            selector = field["selector"]
            field_name = field["name"]
            
            value = self.get_value(column_name)
            
            if value is None:
                return False
            
            ison_logger.info(f'{field_name} (Before Apply): {value}')
            await self.page.select_option(selector, value=value)
            await asyncio.sleep(MED_SLEEP)  # Use standardized wait time
            ison_logger.info(f"{field_name} (After Apply): {value}")
            return True
        except Exception as e:
            ison_logger.error(f"Error occurred while selecting {field_name}: {e}")
            return False

    async def _download_quotation(self):
        """Helper method to handle the quotation download process."""
        try:
            await asyncio.sleep(2)  # Wait for the page to load


        except asyncio.TimeoutError:
            error_msg = "Error: Timeout exceeded while waiting for the download."
            print(error_msg)
            ison_logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Unexpected error during download: {e}"
            print(error_msg)
            ison_logger.error(error_msg)
            return False
            
        return True

    async def categories3_information(self):
        """Apply all category selections from dataframe to the page."""
        ison_logger.info("Filling Category C Information")
        
        # Process each field
        for field in self.FIELDS:
            if not await self._apply_selection(field):
                return False
        
        # The download functionality is currently commented out in the original code
        # Uncomment the line below to enable download functionality
        # await self._download_quotation()
            
        return True