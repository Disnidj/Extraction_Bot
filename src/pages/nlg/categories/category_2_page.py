import asyncio
import time
from datetime import datetime
import pandas as pd
from src.utils.load_yaml import MED_SLEEP, MAX_SLEEP
from src.utils.logger import nlg_logger
from src.utils.support_functions import extract_region,extract_tpa,extract_network, screenshot_and_compare, extract_dropdown_values

class Category2Page:
    def __init__(self, page):
        self.page = page

    def get_field_selector(self, field_id):
        """Get a selector by ID."""
        return f"#{field_id}"

    async def select_option_with_error_handling(self, region, tpa, network, field_name, selector, value, is_placeholder=False):
        """Helper method to select options with consistent error handling and logging."""
        try:
            value = value.strip()
            nlg_logger.debug(f"{field_name} (Before Apply): {value}")
            await extract_dropdown_values(self.page, region, tpa, network, field_name, selector, 'NLGIC')
            if is_placeholder:
                await self.page.get_by_placeholder(selector).fill(value, timeout=3000)
            else:
                await self.page.locator(selector).select_option(label=value, timeout=3000)
            nlg_logger.debug(f"{field_name} (After Apply): {value}")
            time.sleep(MED_SLEEP)
            nlg_logger.debug(f"{field_name} completed")
            return True
        except Exception as e:
            nlg_logger.error(f"Error occurred while selecting {field_name}: {e}")
            return False

    def format_percentage_value(self, value):
        """Format value as percentage if applicable."""
        if str(value).lower() == 'nan' or pd.isna(value):
            return "0%"
        if isinstance(value, (float, int)):
            if value == 0:
                return "0%"
            return f"{int(value * 100)}%"
        return str(value)

    def format_date(self, date_value):
        """Format date to required format."""
        try:
            return datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').strftime('%d-%b-%Y')
        except ValueError:
            return datetime.strptime(date_value, '%m/%d/%Y').strftime('%d-%b-%Y')

    async def fill_category_2(self, df2, cat2, region, tpa, network):
        """Fill category 2 form fields."""
        nlg_logger.debug("Starting Category 2 form filling")

        nlg_logger.debug("Waiting MAX_SLEEP before starting Category 2 fields")
        time.sleep(MAX_SLEEP)
        nlg_logger.debug("Finished MAX_SLEEP, now waiting 10 seconds (asyncio)")
        await asyncio.sleep(10)
        nlg_logger.debug("Proceeding to fill fields")

        fields = [
            {
                "name": "Region",
                "selector": self.get_field_selector("ContentBoady1_ddl_region12"),
                "value": "DXB / NE",
                "is_placeholder": False
            },
            {
                "name": "Network",
                "selector": self.get_field_selector("ContentBoady1_ddl_nw12"),
                "value": str(cat2['Network'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Annual Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_AL12"),
                "value": str(cat2['Annual Limit'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Territory",
                "selector": self.get_field_selector("ContentBoady1_ddl_teritory12"),
                "value": str(cat2['Territory'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Home Nursing Charges",
                "selector": self.get_field_selector("ContentBoady1_ddl_HomeNursing12"),
                "value": str(cat2['Home Nursing Charges'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Hospital Accommodation Room",
                "selector": self.get_field_selector("ContentBoady1_ddl_room12"),
                "value": str(cat2['Hospital accommodation Room'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Deductable",
                "selector": self.get_field_selector("ContentBoady1_ddl_deductable12"),
                "value": str(cat2['Deductable'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Specialist Access",
                "selector": self.get_field_selector("ContentBoady1_ddl_SPAccess12"),
                "value": str(cat2['Specialist Access'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Op Co Insurance",
                "selector": self.get_field_selector("ContentBoady1_ddl_copay12"),
                "value": self.format_percentage_value(cat2['Op Co Insurance'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Limit of Pharmacy",
                "selector": self.get_field_selector("ContentBoady1_ddl_pharmacyLimit12"),
                "value": str(cat2['Limit of Phamacy'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Pharmacy",
                "selector": self.get_field_selector("ContentBoady1_ddl_pharmacyCopay12"),
                "value": self.format_percentage_value(cat2['Pharmacy'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Physiotherapy Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_PhysiotherapyLimit12"),
                "value": str(cat2['Physio'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Physio Co",
                "selector": self.get_field_selector("ContentBoady1_ddl_PhysiotherapyCopay12"),
                "value": self.format_percentage_value(cat2['Physio Co'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Maternity Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_maternityLimit12"),
                "value": str(cat2['Maternity - Married Females'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Maternity CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_maternityOPcopay12"),
                "value": self.format_percentage_value(cat2['Maternity - Married Females CO'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Maternity IP CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_maternityIPcopay12"),
                "value": self.format_percentage_value(cat2['Maternity - Married Females Ip'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Renal Dialysis",
                "selector": self.get_field_selector("ContentBoady1_ddl_RenalDialysis12"),
                "value": str(cat2['Renal Dialysis'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Organ Transplantation",
                "selector": self.get_field_selector("ContentBoady1_ddl_OrganTransplantation12"),
                "value": "Covered",
                "is_placeholder": False
            },
            {
                "name": "Dental Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_dentalLimit12"),
                "value": str(cat2['Dental'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Dental CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_dentalcopay12"),
                "value": self.format_percentage_value(cat2['Dental CO'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Optical Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_opticalLimit12"),
                "value": str(cat2['Optical'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Optical CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_opticalCopay12"),
                "value": self.format_percentage_value(cat2['Optical CO'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Alternative Medicine Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_alterMedLim12"),
                "value": str(cat2['Alternative Medicine'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Alternative Medicine CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_altrMedCopay12"),
                "value": self.format_percentage_value(cat2['Alternative Medicine Co'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Psychiatry",
                "selector": self.get_field_selector("ContentBoady1_ddl_Psychiatric12"),
                "value": str(cat2['Psychiatry'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Repatriation of Mortal remains",
                "selector": self.get_field_selector("ContentBoady1_ddl_Repartiation12"),
                "value": str(cat2['Repatriation of Mortal remains'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "International Assistance",
                "selector": self.get_field_selector("ContentBoady1_ddl_InternationalAssistance12"),
                "value": str(cat2['Assist America'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Telehealth Consultation",
                "selector": self.get_field_selector("ContentBoady1_ddl_Teleconsultation12"),
                "value": str(cat2['Telehealth Consultation'].iloc[0]),
                "is_placeholder": False
            }
        ]

        for field in fields:
            nlg_logger.debug(f"Filling field: {field['name']} with value: {field['value']}")
            success = await self.select_option_with_error_handling(
                region,
                tpa,
                network,
                field["name"],
                field["selector"],
                field["value"],
                field["is_placeholder"]
            )
            if not success:
                nlg_logger.error(f"Failed to fill field {field['name']} with value {field['value']}. Aborting Category 2.")
                return False
        nlg_logger.debug("Category 2 completed successfully")
        return True