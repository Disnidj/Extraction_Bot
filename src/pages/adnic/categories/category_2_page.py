import asyncio
from src.utils.load_yaml import MED_SLEEP, MAX_SLEEP
from src.utils.logger import adnic_logger
from src.utils.support_functions import extract_dropdown_values, screenshot_and_compare

class Category2Page:
    def __init__(self, page):
        self.page = page

    def get_field_selector(self, field_id):
        """Get selector by field ID."""
        return f'//*[@id="{field_id}"]'

    async def select_option_with_error_handling(self, portal_name, tpa, region, network, field_name, field_id, value, use_label=True):
        """
        Select option with comprehensive error handling and extract dropdown values.
        """
        try:
            selector = self.get_field_selector(field_id)
            adnic_logger.debug(f"{field_name} (Before Apply): {value}")
            await extract_dropdown_values(self.page, region, tpa, network, field_name, selector, portal_name)
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

    async def fill_category_2(self, cat2):
        print(f"Filling Category 2 with data: {cat2}")

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "adnic", "ADNIC_3")
        except Exception as e:
            adnic_logger.error(f"An error occurred while taking screenshot: {e}")


        tpa = cat2['TPA'].iloc[0]
        network = cat2['Network'].iloc[0]
        region = cat2['Region'].iloc[0]
        portal_name = "ADNIC"

        await asyncio.sleep(MAX_SLEEP)
        adnic_logger.info("Category 2 Started")

        fields = [
            {
                "name": "TPA (Network provider)",
                "field_id": "ContentPlaceHolder1_ddl_tpaben2",
                "value": self.normalize_value(cat2['TPA'].iloc[0]),
                "use_label": True,
                "sleep_after": MAX_SLEEP
            },
            {
                "name": "Network Type",
                "field_id": "ContentPlaceHolder1_ddl_Prod2",
                "value": self.normalize_value(cat2['Network'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Annual Limit",
                "field_id": "ContentPlaceHolder1_ddl_AnnualLimitben2",
                "value": self.normalize_value(cat2['Annual Limit'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Territorial Cover - Elective",
                "field_id": "ContentPlaceHolder1_ddl_TerritorialCoverELCben2",
                "value": self.normalize_value(cat2['Territory'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Territorial Cover - Emergency",
                "field_id": "ContentPlaceHolder1_ddl_TerritorialCoverEMRben2",
                "value": self.normalize_value(cat2['Territory'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Deductible",
                "field_id": "ContentPlaceHolder1_ddl_dedben2",
                "value": self.normalize_value(cat2['Deductable'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Pharmacy Limit",
                "field_id": "ContentPlaceHolder1_ddl_Pharmacylimit2",
                "value": self.normalize_value(cat2['Limit of Phamacy'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Co-Payment on Outpatient Drugs",
                "field_id": "ContentPlaceHolder1_ddl_copayben2",
                "value": self.normalize_value(cat2['Pharmacy'].iloc[0]),
                "use_label": False,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Co-payment on Diagnostics",
                "field_id": "ContentPlaceHolder1_ddl_Copaymentdiagnostics2",
                "value": self.normalize_value(cat2['Diagnostic/Lab Copay'].iloc[0]),
                "use_label": False,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Maternity - Married Females",
                "field_id": "ContentPlaceHolder1_ddl_Matben2",
                "value": self.normalize_value(cat2['Maternity - Married Females'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Dental",
                "field_id": "ContentPlaceHolder1_ddl_Dentben2",
                "value": self.normalize_value(cat2['Dental'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Optical",
                "field_id": "ContentPlaceHolder1_ddl_Optben2",
                "value": self.normalize_value(cat2['Optical'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Alternative Medicine",
                "field_id": "ContentPlaceHolder1_ddl_alterMedben2",
                "value": self.normalize_value(cat2['Alternative Medicine'].iloc[0]),
                "use_label": True,
                "sleep_after": MED_SLEEP
            },
            {
                "name": "Psychiatry",
                "field_id": "ContentPlaceHolder1_ddl_Psychiatry2",
                "value": self.normalize_value(cat2['Psychiatry'].iloc[0]),
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
                sleep_time = field.get("sleep_after", MED_SLEEP)
                if sleep_time != MED_SLEEP:
                    await asyncio.sleep(sleep_time - MED_SLEEP)
            else:
                adnic_logger.error(f"Failed to fill field {field['name']} with value {field['value']}. Stopping execution.")
                return False

        adnic_logger.info("Category 2 completed successfully")
        return True