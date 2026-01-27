import asyncio
from src.utils.load_yaml import MED_SLEEP, MAX_SLEEP
from src.utils.logger import adnic_logger

class Category3Page:
    def __init__(self, page):
        self.page = page

    def get_field_selector(self, field_id):
        """Get selector by field ID."""
        return f'//*[@id="{field_id}"]'

    async def select_option_with_error_handling(self, field_name, field_id, value, use_label=True):
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

    async def handle_network_field(self, field_name, field_id, value, custom_sleep=None):
        """Handle network fields that require special interaction (hover, click)."""
        try:
            selector = self.get_field_selector(field_id)
            adnic_logger.debug(f"{field_name} (Before Apply): {value}")
            
            await self.page.locator(selector).hover()
            await asyncio.sleep(3)
            await self.page.locator(selector).select_option(label=value, timeout=5000)
            await self.page.locator(selector).click()
            
            adnic_logger.debug(f"{field_name} (After Apply): {value}")
            
            # Use custom sleep if provided, otherwise MED_SLEEP
            sleep_time = custom_sleep if custom_sleep else MED_SLEEP
            await asyncio.sleep(sleep_time)
            return True
            
        except Exception as e:
            adnic_logger.error(f"Error occurred while selecting {field_name}: {e}")
            return False

    def normalize_value(self, value):
        """Normalize value for processing by converting to string and stripping whitespace."""
        if value is None:
            return ""
        return str(value).strip()

    def get_category_fields(self, category_data, field_suffix):
        """Get field configuration for a category section."""
        # Special handling for Category 1 fields with different psychiatry field ID
        psychiatry_field_id = f"ContentPlaceHolder1_ddl_PsycMed{field_suffix}" if field_suffix == "31" else f"ContentPlaceHolder1_ddl_PsycMed{field_suffix}"
        
        return [
            {
                "name": "TPA (Network provider)",
                "field_id": f"ContentPlaceHolder1_ddl_tpaben{field_suffix}",
                "value": self.normalize_value(category_data['TPA'].iloc[0]),
                "use_label": True,
                "sleep_after": 5 if field_suffix == "31" else MAX_SLEEP  # Special sleep for first category
            },
            {
                "name": "Network Type",
                "field_id": f"ContentPlaceHolder1_ddl_Prod{field_suffix}",
                "value": self.normalize_value(category_data['Network'].iloc[0]),
                "special_handling": "network",
                "sleep_after": 5 if field_suffix == "31" else MAX_SLEEP  # Special sleep for first category
            },
            {
                "name": "Annual Limit",
                "field_id": f"ContentPlaceHolder1_ddl_AnnualLimitben{field_suffix}",
                "value": self.normalize_value(category_data['Annual Limit'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Territorial Cover - Elective",
                "field_id": f"ContentPlaceHolder1_ddl_TerritorialCoverELCben{field_suffix}",
                "value": self.normalize_value(category_data['Territory'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Territorial Cover - Emergency",
                "field_id": f"ContentPlaceHolder1_ddl_TerritorialCoverEMRben{field_suffix}",
                "value": self.normalize_value(category_data['Territory'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Deductible",
                "field_id": f"ContentPlaceHolder1_ddl_dedben{field_suffix}",
                "value": self.normalize_value(category_data['Deductable'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Pharmacy Limit",
                "field_id": f"ContentPlaceHolder1_ddl_Pharmacylimit{field_suffix}",
                "value": self.normalize_value(category_data['Limit of Phamacy'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Co-Payment on Outpatient Drugs",
                "field_id": f"ContentPlaceHolder1_ddl_copayben{field_suffix}",
                "value": self.normalize_value(category_data['Pharmacy'].iloc[0]),
                "use_label": True if field_suffix == "31" else False,  # Category 1 uses label, others use value
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Co-payment on Diagnostics",
                "field_id": f"ContentPlaceHolder1_ddl_Copaymentdiagnostics{field_suffix}",
                "value": self.normalize_value(category_data['Diagnostic/Lab Copay'].iloc[0]),
                "use_label": False,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Maternity - Married Females",
                "field_id": f"ContentPlaceHolder1_ddl_Matben{field_suffix}",
                "value": self.normalize_value(category_data['Maternity - Married Females'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Dental",
                "field_id": f"ContentPlaceHolder1_ddl_Dentben{field_suffix}",
                "value": self.normalize_value(category_data['Dental'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Optical",
                "field_id": f"ContentPlaceHolder1_ddl_Optben{field_suffix}",
                "value": self.normalize_value(category_data['Optical'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Alternative Medicine",
                "field_id": f"ContentPlaceHolder1_ddl_alterMed{field_suffix}",
                "value": self.normalize_value(category_data['Alternative Medicine'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Psychiatry",
                "field_id": psychiatry_field_id,
                "value": self.normalize_value(category_data['Psychiatry'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            }
        ]

    async def fill_category_section(self, category_data, category_name, field_suffix):
        """Fill a category section with the given data and field suffix."""
        adnic_logger.info(f"{category_name} Started")

        # Get fields configuration for this category
        fields = self.get_category_fields(category_data, field_suffix)

        # Process each field - stop on first error
        for field in fields:
            if field.get("special_handling") == "network":
                # Handle network fields with custom sleep
                custom_sleep = field.get("sleep_after")
                success = await self.handle_network_field(
                    field["name"],
                    field["field_id"],
                    field["value"],
                    custom_sleep
                )
            else:
                success = await self.select_option_with_error_handling(
                    field["name"],
                    field["field_id"],
                    field["value"],
                    field["use_label"]
                )
            
            if success:
                # Use custom sleep time if specified and not already handled
                if not field.get("special_handling") == "network":
                    sleep_time = field.get("sleep_after", MED_SLEEP)
                    if sleep_time != MED_SLEEP:  # Only sleep extra if different from default
                        await asyncio.sleep(sleep_time - MED_SLEEP)
            else:
                adnic_logger.error(f"Failed to fill field {field['name']} with value {field['value']}. Stopping execution.")
                return False

        adnic_logger.info(f"{category_name} completed successfully")
        return True

    async def fill_category_3(self, cat1, cat2, cat3):
        """Fill Category 3 form with improved error handling and structure."""
        await asyncio.sleep(MAX_SLEEP)
        
        # Fill Category 1 section (using cat1 data with field suffix 31)
        success = await self.fill_category_section(cat1, "Category 1", "31")
        if not success:
            return False

        await asyncio.sleep(MAX_SLEEP)
        
        # Fill Category 2 section (using cat2 data with field suffix 32)
        success = await self.fill_category_section(cat2, "Category 2", "32")
        if not success:
            return False

        await asyncio.sleep(MAX_SLEEP)
        
        # Fill Category 3 section (using cat3 data with field suffix 33)
        success = await self.fill_category_section(cat3, "Category 3", "33")
        if not success:
            return False

        adnic_logger.info("Category 3 page completed successfully")
        return True