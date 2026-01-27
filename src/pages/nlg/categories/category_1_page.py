import asyncio
import time
from datetime import datetime
import pandas as pd
from src.utils.load_yaml import MED_SLEEP, MAX_SLEEP
from src.utils.logger import nlg_logger
from src.utils.support_functions import extract_region,extract_tpa,extract_network, screenshot_and_compare, extract_dropdown_values


class Category1Page:
    def __init__(self, page):
        self.page = page

    def get_field_selector(self, field_id):
        """Get a selector by ID."""
        return f"#{field_id}"

    async def select_option_with_error_handling(self, region, tpa, network, field_name, selector, value, is_placeholder=False):
        """Helper method to select options with consistent error handling and logging."""
        try:
            value= value.strip()
            nlg_logger.debug(f"{field_name} (Before Apply): {value}")
            await extract_dropdown_values(self.page, region, tpa, network,  field_name, selector, 'NLGIC')
            
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
        
        # Return the value as is if it's already a string
        return str(value)

    def format_date(self, date_value):
        """Format date to required format."""
        try:
            # Try parsing with the expected format '%Y-%m-%d %H:%M:%S'
            return datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').strftime('%d-%b-%Y')
        except ValueError:
            # If it fails, try the alternative format '%m/%d/%Y'
            return datetime.strptime(date_value, '%m/%d/%Y').strftime('%d-%b-%Y')

    async def fill_category_1(self, df1, cat1, region, tpa, network):
        """Fill category 1 form fields."""
        nlg_logger.debug("Starting Category 1 form filling")

        # Add a delay before starting
        nlg_logger.debug("Waiting MAX_SLEEP before starting Category 1 fields")
        time.sleep(MAX_SLEEP)
        nlg_logger.debug("Finished MAX_SLEEP, now waiting 10 seconds (asyncio)")
        await asyncio.sleep(10)

        
        try:
            nlg_logger.debug("Finished initial waits, taking screenshot for NLG_3")
            await screenshot_and_compare(self.page, "nlg", "NLG_3")
        except Exception as e:
            nlg_logger.error(f"An error occurred while taking screenshot: {e}")


        nlg_logger.debug("Screenshot taken, proceeding to fill fields")
        
        # Define all fields with their selectors and values
        fields = [
            {
                "name": "Policy Start Date",
                "selector": "Policy Start (eg: 01-Jan-2021)",
                "value": self.format_date(str(df1[df1['KEY'] =="Effective from"]['VALUE'].values[0])),
                "is_placeholder": True
            },
            {
                "name": "Broker Commission",
                "selector": self.get_field_selector("ContentBoady1_brk_Mar"),
                # "value": str(cat1['Broker Commission'].iloc[0]).strip().replace('%', ' %').strip(),
                "value": "10 %",
                "is_placeholder": False
            },
            {
                "name": "TPA",
                "selector": self.get_field_selector("ContentBoady1_ddl_tpa1"),
                "value": str(cat1['TPA'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Region",
                "selector": self.get_field_selector("ContentBoady1_ddl_region1"),
                "value": "DXB / NE",
                "is_placeholder": False
            },
            {
                "name": "Network",
                "selector": self.get_field_selector("ContentBoady1_ddl_nw1"),
                "value": str(cat1['Network'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Annual Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_AL1"),
                "value": str(cat1['Annual Limit'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Territory",
                "selector": self.get_field_selector("ContentBoady1_ddl_teritory1"),
                "value": str(cat1['Territory'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Home Nursing Charges",
                "selector": self.get_field_selector("ContentBoady1_ddl_HomeNursing1"),
                "value": str(cat1['Home Nursing Charges'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Hospital Accommodation Room",
                "selector": self.get_field_selector("ContentBoady1_ddl_room1"),
                "value": str(cat1['Hospital accommodation Room'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Deductable",
                "selector": self.get_field_selector("ContentBoady1_ddl_deductable1"),
                "value": str(cat1['Deductable'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Specialist Access",
                "selector": self.get_field_selector("ContentBoady1_ddl_SPAccess1"),
                "value": str(cat1['Specialist Access'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Op Co Insurance",
                "selector": self.get_field_selector("ContentBoady1_ddl_copay1"),
                "value": self.format_percentage_value(cat1['Op Co Insurance'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Limit of Pharmacy",
                "selector": self.get_field_selector("ContentBoady1_ddl_pharmacyLimit1"),
                "value": str(cat1['Limit of Phamacy'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Physiotherapy Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_PhysiotherapyLimit1"),
                "value": str(cat1['Physio'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Physio Co",
                "selector": self.get_field_selector("ContentBoady1_ddl_PhysiotherapyCopay1"),
                "value": self.format_percentage_value(cat1['Physio Co'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Maternity Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_maternityLimit1"),
                "value": str(cat1['Maternity - Married Females'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Maternity CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_maternityOPcopay1"),
                "value": self.format_percentage_value(cat1['Maternity - Married Females CO'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Maternity IP CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_maternityIPcopay1"),
                "value": self.format_percentage_value(cat1['Maternity - Married Females Ip'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Renal Dialysis",
                "selector": self.get_field_selector("ContentBoady1_ddl_RenalDialysis1"),
                "value": str(cat1['Renal Dialysis'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Organ Transplantation",
                "selector": self.get_field_selector("ContentBoady1_ddl_OrganTransplantation1"),
                "value": "Covered",
                "is_placeholder": False
            },
            {
                "name": "Dental Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_dentalLimit1"),
                "value": str(cat1['Dental'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Dental CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_dentalcopay1"),
                "value": self.format_percentage_value(cat1['Dental CO'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Optical Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_opticalLimit1"),
                "value": str(cat1['Optical'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Optical CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_opticalCopay1"),
                "value": self.format_percentage_value(cat1['Optical CO'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Alternative Medicine Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_alterMedLim1"),
                "value": str(cat1['Alternative Medicine'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Alternative Medicine CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_altrMedCopay1"),
                "value": self.format_percentage_value(cat1['Alternative Medicine Co'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Psychiatry",
                "selector": self.get_field_selector("ContentBoady1_ddl_Psychiatric1"),
                "value": str(cat1['Psychiatry'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Repatriation of Mortal remains",
                "selector": self.get_field_selector("ContentBoady1_ddl_Repartiation1"),
                "value": str(cat1['Repatriation of Mortal remains'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "International Assistance",
                "selector": self.get_field_selector("ContentBoady1_ddl_InternationalAssistance"),
                "value": str(cat1['Assist America'].iloc[0]),
                "is_placeholder": False
            },
            {
                "name": "Telehealth Consultation",
                "selector": self.get_field_selector("ContentBoady1_ddl_Teleconsultation1"),
                "value": str(cat1['Telehealth Consultation'].iloc[0]),
                "is_placeholder": False
            }
        ]
        
        # Fill each field
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
                nlg_logger.error(f"Failed to fill field {field['name']} with value {field['value']}. Aborting Category 1.")
                return False
        
        nlg_logger.debug("Category 1 completed successfully")
        return True