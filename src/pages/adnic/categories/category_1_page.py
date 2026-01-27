import asyncio
from datetime import datetime
from src.utils.load_yaml import MED_SLEEP, MAX_SLEEP
from src.utils.logger import adnic_logger
from src.utils.support_functions import extract_dropdown_values, screenshot_and_compare

class Category1Page:
    def __init__(self, page):
        self.page = page

    def get_field_selector(self, field_id):
        """Get selector by field ID."""
        return f'//*[@id="{field_id}"]'

    async def select_option_with_error_handling(self, portal_name, tpa, region, network, field_name, field_id, value, use_label=True):
        """
        Select option with comprehensive error handling.
        
        Args:
            field_name: Human readable field name for logging
            field_id: The HTML element ID
            value: Value to select
            use_label: Whether to use label selection (True) or value selection (False)
        """
        try:
            selector = self.get_field_selector(field_id)
            adnic_logger.debug(f"{field_name} (Before Apply): {value}")
            
            await extract_dropdown_values(self.page, region, tpa, network,  field_name, selector, portal_name)
            if use_label:
                await self.page.locator(selector).select_option(label=value, timeout=5000)
            else:
                await self.page.locator(selector).select_option(value=value, timeout=5000)
                
            adnic_logger.debug(f"{field_name} (After Apply): {value}")
            await asyncio.sleep(MED_SLEEP)
            return True
            
        except Exception as e:
            adnic_logger.error(f"Error occurred while selecting {field_name}: {e}")
            return False

    def normalize_value(self, value):
        """Normalize value for processing by converting to string and stripping whitespace."""
        if value is None:
            return ""
        return str(value).strip()

    async def fill_category_1(self, cat1):
        print(f"Filling Category 1 with data: {cat1}")

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "adnic", "ADNIC_3")
        except Exception as e:
            adnic_logger.error(f"An error occurred while taking screenshot: {e}")

        tpa = cat1['TPA'].iloc[0]
        network = cat1['Network'].iloc[0]
        region = cat1['Region'].iloc[0]
        portal_name = "ADNIC"


        """Fill Category 1 form with improved error handling and structure."""
        await asyncio.sleep(MAX_SLEEP)
        adnic_logger.info("Category 1 Started")

        # Define all fields to be filled with their configurations
        fields = [
            {
                "name": "TPA (Network provider)",
                "field_id": "ContentPlaceHolder1_ddl_tpaben1",
                "value": self.normalize_value(cat1['TPA'].iloc[0]),
                "use_label": True,
                "sleep_after": MAX_SLEEP
            },
            {
                "name": "Network Type",
                "field_id": "ContentPlaceHolder1_ddl_Prod1",
                "value": self.normalize_value(cat1['Network'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Annual Limit",
                "field_id": "ContentPlaceHolder1_ddl_AnnualLimitben1",
                "value": self.normalize_value(cat1['Annual Limit'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Territorial Cover - Elective",
                "field_id": "ContentPlaceHolder1_ddl_TerritorialCoverELCben1",
                "value": self.normalize_value(cat1['Territory'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Territorial Cover - Emergency",
                "field_id": "ContentPlaceHolder1_ddl_TerritorialCoverEMRben1",
                "value": self.normalize_value(cat1['Territory'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Deductible",
                "field_id": "ContentPlaceHolder1_ddl_dedben1",
                "value": self.normalize_value(cat1['Deductable'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Pharmacy Limit",
                "field_id": "ContentPlaceHolder1_ddl_Pharmacylimit",
                "value": self.normalize_value(cat1['Limit of Phamacy'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Co-Payment on Outpatient Drugs",
                "field_id": "ContentPlaceHolder1_ddl_copayben1",
                "value": self.normalize_value(cat1['Pharmacy'].iloc[0]),
                "use_label": False,  # This field uses value selection
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Co-payment on Diagnostics",
                "field_id": "ContentPlaceHolder1_ddl_Copaymentdiagnostics",
                "value": self.normalize_value(cat1['Diagnostic/Lab Copay'].iloc[0]),
                "use_label": False,  # This field uses value selection
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Maternity - Married Females",
                "field_id": "ContentPlaceHolder1_ddl_Matben1",
                "value": self.normalize_value(cat1['Maternity - Married Females'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Dental",
                "field_id": "ContentPlaceHolder1_ddl_Dentben1",
                "value": self.normalize_value(cat1['Dental'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Optical",
                "field_id": "ContentPlaceHolder1_ddl_Optben1",
                "value": self.normalize_value(cat1['Optical'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Alternative Medicine",
                "field_id": "ContentPlaceHolder1_ddl_alterMedben1",
                "value": self.normalize_value(cat1['Alternative Medicine'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Psychiatry",
                "field_id": "ContentPlaceHolder1_ddl_Psychiatry1",
                "value": self.normalize_value(cat1['Psychiatry'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            }
        ]

        # Process each field - stop on first error
        for field in fields:
            success = await self.select_option_with_error_handling(
                portal_name,
                tpa,
                region,
                network,
                field["name"],
                field["field_id"],
                field["value"],
                field["use_label"]
            )
            
            if success:
                # Use custom sleep time if specified, otherwise use MED_SLEEP
                sleep_time = field.get("sleep_after", MED_SLEEP)
                if sleep_time != MED_SLEEP:  # Only sleep extra if different from default
                    await asyncio.sleep(sleep_time - MED_SLEEP)
            else:
                adnic_logger.error(f"Failed to fill field {field['name']} with value {field['value']}. Stopping execution.")
                return False

        adnic_logger.info("Category 1 completed successfully")
        return True

    async def get_field_options(self, field_id):
        """Get available options for a dropdown field (useful for debugging)."""
        try:
            selector = self.get_field_selector(field_id)
            options = await self.page.locator(selector).evaluate('''(element) => {
                return Array.from(element.options).map(opt => ({
                    text: opt.text.trim(),
                    value: opt.value
                }));
            }''')
            return options
        except Exception as e:
            adnic_logger.error(f"Error getting options for field {field_id}: {e}")
            return []

    async def validate_field_value(self, field_id, expected_value):
        """Validate that a field has been set to the expected value."""
        try:
            selector = self.get_field_selector(field_id)
            actual_value = await self.page.locator(selector).input_value()
            return actual_value == expected_value
        except Exception as e:
            adnic_logger.error(f"Error validating field {field_id}: {e}")
            return False