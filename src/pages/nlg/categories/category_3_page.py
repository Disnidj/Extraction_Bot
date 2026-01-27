# import asyncio
# from src.utils.load_yaml import MED_SLEEP
# from src.utils.logger import nlg_logger
# import pandas as pd

# class Category3Page:
#     def __init__(self, page):
#         self.page = page

#     async def fill_category_3(self, cat3):
#      # Ensure all values are strings and select options for Category 3

#         # Select Region
#         region = "DXB / NE"
#         nlg_logger.debug(f"Region (Before Apply): {region}")
#         await self.page.locator("#ContentBoady1_ddl_region13").select_option(region)
#         nlg_logger.debug(f"Region (After Apply): {region}")
#         await asyncio.sleep(MED_SLEEP)

#         network = str(cat3['Network'].iloc[0])
#         nlg_logger.debug(f"Network (Before Apply): {network}")
#         await self.page.locator("#ContentBoady1_ddl_nw13").select_option(label=network)
#         nlg_logger.debug(f"Network (After Apply): {network}")
#         await asyncio.sleep(MED_SLEEP)
        
#         annual_limit = str(cat3['Annual Limit'].iloc[0])
#         nlg_logger.debug(f"Annual Limit (Before Apply): {annual_limit}")
#         await self.page.locator("#ContentBoady1_ddl_AL13").select_option(label=annual_limit)
#         nlg_logger.debug(f"Annual Limit (After Apply): {annual_limit}")
#         await asyncio.sleep(MED_SLEEP)
        
#         territory = str(cat3['Territory'].iloc[0])
#         nlg_logger.debug(f"Territory (Before Apply): {territory}")
#         await self.page.locator("#ContentBoady1_ddl_teritory13").select_option(label=territory)
#         nlg_logger.debug(f"Territory (After Apply): {territory}")
#         await asyncio.sleep(MED_SLEEP)
        
#         home_nursing_charges = str(cat3['Home Nursing Charges'].iloc[0])
#         nlg_logger.debug(f"Home Nursing Charges (Before Apply): {home_nursing_charges}")
#         await self.page.locator("#ContentBoady1_ddl_HomeNursing13").select_option(label=home_nursing_charges)
#         nlg_logger.debug(f"Home Nursing Charges (After Apply): {home_nursing_charges}")
#         await asyncio.sleep(MED_SLEEP)

#         hospital_accommodation_room = str(cat3['Hospital accommodation Room'].iloc[0])
#         nlg_logger.debug(f"Hospital accommodation Room (Before Apply): {hospital_accommodation_room}")
#         await self.page.locator("#ContentBoady1_ddl_room13").select_option(label=hospital_accommodation_room)
#         nlg_logger.debug(f"Hospital accommodation Room (After Apply): {hospital_accommodation_room}")
#         await asyncio.sleep(MED_SLEEP)

#         deductable = str(cat3['Deductable'].iloc[0])
#         nlg_logger.debug(f"Deductable (Before Apply): {deductable}")
#         await self.page.locator("#ContentBoady1_ddl_deductable13").select_option(label=deductable)
#         nlg_logger.debug(f"Deductable (After Apply): {deductable}")
#         await asyncio.sleep(MED_SLEEP)

#         specialist_access = str(cat3['Specialist Access'].iloc[0])
#         nlg_logger.debug(f"Specialist Access (Before Apply): {specialist_access}")
#         await self.page.locator("#ContentBoady1_ddl_SPAccess13").select_option(label=specialist_access)
#         nlg_logger.debug(f"Specialist Access (After Apply): {specialist_access}")
#         await asyncio.sleep(MED_SLEEP)

#         op_co_insurance = cat3['Op Co Insurance'].iloc[0]
#         nlg_logger.debug(f"Op Co Insurance (Before Apply): {op_co_insurance}")
#         if str(op_co_insurance).lower() != 'nan' or pd.notna(op_co_insurance):
#             op_co_insurance = (
#             f"{int(op_co_insurance * 100)}%" if isinstance(op_co_insurance, (float, int)) and op_co_insurance != 0 else 
#             ("0%" if op_co_insurance == 0 else str(op_co_insurance))
#             )
#             await self.page.locator("#ContentBoady1_ddl_copay13").select_option(label=op_co_insurance)
#         nlg_logger.debug(f"Op Co Insurance (After Apply): {op_co_insurance}")
#         await asyncio.sleep(MED_SLEEP)

#         limit_of_pharmacy = str(cat3['Limit of Phamacy'].iloc[0])
#         nlg_logger.debug(f"Limit of Pharmacy (Before Apply): {limit_of_pharmacy}")
#         await self.page.locator("#ContentBoady1_ddl_pharmacyLimit13").select_option(label=limit_of_pharmacy)
#         nlg_logger.debug(f"Limit of Pharmacy (After Apply): {limit_of_pharmacy}")
#         await asyncio.sleep(MED_SLEEP)

#         pharmacy = cat3['Pharmacy'].iloc[0]
#         nlg_logger.debug(f"Pharmacy (Before Apply): {pharmacy}")
#         if str(pharmacy).lower() != 'nan' or pd.notna(pharmacy):
#             pharmacy = (
#             f"{int(pharmacy * 100)}%" if isinstance(pharmacy, (float, int)) and pharmacy != 0 else 
#             ("0%" if pharmacy == 0 else str(pharmacy))
#             )
#             await self.page.locator("#ContentBoady1_ddl_pharmacyCopay13").select_option(label=str(pharmacy))
#         nlg_logger.debug(f"Pharmacy (After Apply): {pharmacy}")
#         await asyncio.sleep(MED_SLEEP)

#         physio = str(cat3['Physio'].iloc[0])
#         nlg_logger.debug(f"Physio (Before Apply): {physio}")
#         await self.page.locator("#ContentBoady1_ddl_PhysiotherapyLimit13").select_option(label=physio)
#         nlg_logger.debug(f"Physio (After Apply): {physio}")
#         await asyncio.sleep(MED_SLEEP)

#         physio_co = cat3['Physio Co'].iloc[0]
#         nlg_logger.debug(f"Physio Co (Before Apply): {physio_co}")
#         if str(physio_co).lower() != 'nan' or pd.notna(physio_co):
#             physio_co = (
#             f"{int(physio_co * 100)}%" if isinstance(physio_co, (float, int)) and physio_co != 0 else 
#             ("0%" if physio_co == 0 else str(physio_co))
#             )
#             await self.page.locator("#ContentBoady1_ddl_PhysiotherapyCopay13").select_option(label=physio_co)
#         nlg_logger.debug(f"Physio Co (After Apply): {physio_co}")
#         await asyncio.sleep(MED_SLEEP)

#         maternity_limit = str(cat3['Maternity - Married Females'].iloc[0])
#         nlg_logger.debug(f"Maternity Limit (Before Apply): {maternity_limit}")
#         await self.page.locator("#ContentBoady1_ddl_maternityLimit13").select_option(label=maternity_limit)
#         nlg_logger.debug(f"Maternity Limit (After Apply): {maternity_limit}")
#         await asyncio.sleep(MED_SLEEP)

#         maternity_co = cat3['Maternity - Married Females CO'].iloc[0]
#         nlg_logger.debug(f"Maternity CO (Before Apply): {maternity_co}")
#         if str(maternity_co).lower() != 'nan' or pd.notna(maternity_co):
#             maternity_co = (
#             f"{int(maternity_co * 100)}%" if isinstance(maternity_co, (float, int)) and maternity_co != 0 else 
#             ("0%" if maternity_co == 0 else str(maternity_co))
#             )
#             await self.page.locator("#ContentBoady1_ddl_maternityOPcopay13").select_option(label=maternity_co)
#         nlg_logger.debug(f"Maternity CO (After Apply): {maternity_co}")
#         await asyncio.sleep(MED_SLEEP)

#         maternity_ip_co = cat3['Maternity - Married Females Ip'].iloc[0]
#         nlg_logger.debug(f"Maternity IP CO (Before Apply): {maternity_ip_co}")
#         if str(maternity_ip_co).lower() != 'nan' or pd.notna(maternity_ip_co):
#             maternity_ip_co = (
#             f"{int(maternity_ip_co * 100)}%" if isinstance(maternity_ip_co, (float, int)) and maternity_ip_co != 0 else 
#             ("0%" if maternity_ip_co == 0 else str(maternity_ip_co))
#             )
#             await self.page.locator("#ContentBoady1_ddl_maternityIPcopay13").select_option(label=maternity_ip_co)
#         nlg_logger.debug(f"Maternity IP CO (After Apply): {maternity_ip_co}")
#         await asyncio.sleep(MED_SLEEP)

#         renal_dialysis = str(cat3['Renal Dialysis'].iloc[0])
#         nlg_logger.debug(f"Renal Dialysis (Before Apply): {renal_dialysis}")
#         await self.page.locator("#ContentBoady1_ddl_RenalDialysis13").select_option(label=renal_dialysis)
#         nlg_logger.debug(f"Renal Dialysis (After Apply): {renal_dialysis}")
#         await asyncio.sleep(MED_SLEEP)

#         organ_transplantation = "Covered"
#         nlg_logger.debug(f"Organ Transplantation (Before Apply): {organ_transplantation}")
#         await self.page.locator("#ContentBoady1_ddl_OrganTransplantation13").select_option(label=organ_transplantation)
#         nlg_logger.debug(f"Organ Transplantation (After Apply): {organ_transplantation}")
#         await asyncio.sleep(MED_SLEEP)

#         dental_limit = str(cat3['Dental'].iloc[0])
#         nlg_logger.debug(f"Dental Limit (Before Apply): {dental_limit}")
#         await self.page.locator("#ContentBoady1_ddl_dentalLimit13").select_option(label=dental_limit)
#         nlg_logger.debug(f"Dental Limit (After Apply): {dental_limit}")
#         await asyncio.sleep(MED_SLEEP)

#         dental_co = cat3['Dental CO'].iloc[0]
#         nlg_logger.debug(f"Dental CO (Before Apply): {dental_co}")
#         if str(dental_co).lower() != 'nan' or pd.notna(dental_co):
#             dental_co = (
#             f"{int(dental_co * 100)}%" if isinstance(dental_co, (float, int)) and dental_co != 0 else 
#             ("0%" if dental_co == 0 else str(dental_co))
#             )
#             await self.page.locator("#ContentBoady1_ddl_dentalcopay13").select_option(label=dental_co)
#         nlg_logger.debug(f"Dental CO (After Apply): {dental_co}")
#         await asyncio.sleep(MED_SLEEP)

#         optical_limit = str(cat3['Optical'].iloc[0])
#         nlg_logger.debug(f"Optical Limit (Before Apply): {optical_limit}")
#         await self.page.locator("#ContentBoady1_ddl_opticalLimit13").select_option(label=optical_limit)
#         nlg_logger.debug(f"Optical Limit (After Apply): {optical_limit}")
#         await asyncio.sleep(MED_SLEEP)

#         optical_co = cat3['Optical CO'].iloc[0]
#         nlg_logger.debug(f"Optical CO (Before Apply): {optical_co}")
#         if str(optical_co).lower() != 'nan' or pd.notna(optical_co):
#             optical_co = (
#             f"{int(optical_co * 100)}%" if isinstance(optical_co, (float, int)) and optical_co != 0 else 
#             ("0%" if optical_co == 0 else str(optical_co))
#             )
#             await self.page.locator("#ContentBoady1_ddl_opticalCopay13").select_option(label=optical_co)
#         nlg_logger.debug(f"Optical CO (After Apply): {optical_co}")
#         await asyncio.sleep(MED_SLEEP)

#         alternative_medicine_limit = str(cat3['Alternative Medicine'].iloc[0])
#         nlg_logger.debug(f"Alternative Medicine Limit (Before Apply): {alternative_medicine_limit}")
#         await self.page.locator("#ContentBoady1_ddl_alterMedLim13").select_option(label=alternative_medicine_limit)
#         nlg_logger.debug(f"Alternative Medicine Limit (After Apply): {alternative_medicine_limit}")
#         await asyncio.sleep(MED_SLEEP)

#         alter_med_co = cat3['Alternative Medicine Co'].iloc[0]
#         nlg_logger.debug(f"Alternative Medicine CO (Before Apply): {alter_med_co}")
#         if str(alter_med_co).lower() != 'nan' or pd.notna(alter_med_co):
#             alter_med_co = (
#             f"{int(alter_med_co * 100)}%" if isinstance(alter_med_co, (float, int)) and alter_med_co != 0 else 
#             ("0%" if alter_med_co == 0 else str(alter_med_co))
#             )
#             await self.page.locator("#ContentBoady1_ddl_altrMedCopay13").select_option(label=alter_med_co)
#         nlg_logger.debug(f"Alternative Medicine CO (After Apply): {alter_med_co}")
#         await asyncio.sleep(MED_SLEEP)

#         psychiatry = str(cat3['Psychiatry'].iloc[0])
#         nlg_logger.debug(f"Psychiatry (Before Apply): {psychiatry}")
#         await self.page.locator("#ContentBoady1_ddl_Psychiatric13").select_option(label=psychiatry)
#         nlg_logger.debug(f"Psychiatry (After Apply): {psychiatry}")
#         await asyncio.sleep(MED_SLEEP)

#         repatriation_of_mortal_remains = str(cat3['Repatriation of Mortal remains'].iloc[0])
#         nlg_logger.debug(f"Repatriation of Mortal remains (Before Apply): {repatriation_of_mortal_remains}")
#         await self.page.locator("#ContentBoady1_ddl_Repartiation13").select_option(label=repatriation_of_mortal_remains)
#         nlg_logger.debug(f"Repatriation of Mortal remains (After Apply): {repatriation_of_mortal_remains}")
#         await asyncio.sleep(MED_SLEEP)

#         international_assistance = str(cat3['Assist America'].iloc[0])
#         nlg_logger.debug(f"International Assistance (Before Apply): {international_assistance}")
#         await self.page.locator("#ContentBoady1_ddl_InternationalAssistance13").select_option(label=international_assistance)
#         nlg_logger.debug(f"International Assistance (After Apply): {international_assistance}")
#         await asyncio.sleep(MED_SLEEP)

#         telehealth_consultation = str(cat3['Telehealth Consultation'].iloc[0])
#         nlg_logger.debug(f"Telehealth Consultation (Before Apply): {telehealth_consultation}")
#         await self.page.locator("#ContentBoady1_ddl_Teleconsultation13").select_option(label=telehealth_consultation)
#         nlg_logger.debug(f"Telehealth Consultation (After Apply): {telehealth_consultation}")

#         nlg_logger.debug("Category 3 completed")


import time
import pandas as pd
from src.utils.load_yaml import MED_SLEEP
from src.utils.logger import nlg_logger

class Category3Page:
    def __init__(self, page):
        self.page = page
        
    def get_field_selector(self, field_id):
        """Get a selector by ID."""
        return f"#{field_id}"

    async def select_option_with_error_handling(self, field_name, selector, value):
        """Helper method to select options with consistent error handling and logging."""
        try:
            value= value.strip()
            nlg_logger.debug(f"{field_name} (Before Apply): {value}")
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

    async def fill_category_3(self, cat3):
        """Fill category 3 form fields."""
        nlg_logger.debug("Starting Category 3 form filling")
        
        # Define all fields with their selectors and values
        fields = [
            {
                "name": "Region",
                "selector": self.get_field_selector("ContentBoady1_ddl_region13"),
                "value": "DXB / NE"
            },
            {
                "name": "Network",
                "selector": self.get_field_selector("ContentBoady1_ddl_nw13"),
                "value": str(cat3['Network'].iloc[0])
            },
            {
                "name": "Annual Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_AL13"),
                "value": str(cat3['Annual Limit'].iloc[0])
            },
            {
                "name": "Territory",
                "selector": self.get_field_selector("ContentBoady1_ddl_teritory13"),
                "value": str(cat3['Territory'].iloc[0])
            },
            {
                "name": "Home Nursing Charges",
                "selector": self.get_field_selector("ContentBoady1_ddl_HomeNursing13"),
                "value": str(cat3['Home Nursing Charges'].iloc[0])
            },
            {
                "name": "Hospital Accommodation Room",
                "selector": self.get_field_selector("ContentBoady1_ddl_room13"),
                "value": str(cat3['Hospital accommodation Room'].iloc[0])
            },
            {
                "name": "Deductable",
                "selector": self.get_field_selector("ContentBoady1_ddl_deductable13"),
                "value": str(cat3['Deductable'].iloc[0])
            },
            {
                "name": "Specialist Access",
                "selector": self.get_field_selector("ContentBoady1_ddl_SPAccess13"),
                "value": str(cat3['Specialist Access'].iloc[0])
            },
            {
                "name": "Op Co Insurance",
                "selector": self.get_field_selector("ContentBoady1_ddl_copay13"),
                "value": self.format_percentage_value(cat3['Op Co Insurance'].iloc[0])
            },
            {
                "name": "Limit of Pharmacy",
                "selector": self.get_field_selector("ContentBoady1_ddl_pharmacyLimit13"),
                "value": str(cat3['Limit of Phamacy'].iloc[0])
            },
            {
                "name": "Pharmacy",
                "selector": self.get_field_selector("ContentBoady1_ddl_pharmacyCopay13"),
                "value": self.format_percentage_value(cat3['Pharmacy'].iloc[0])
            },
            {
                "name": "Physiotherapy Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_PhysiotherapyLimit13"),
                "value": str(cat3['Physio'].iloc[0])
            },
            {
                "name": "Physio Co",
                "selector": self.get_field_selector("ContentBoady1_ddl_PhysiotherapyCopay13"),
                "value": self.format_percentage_value(cat3['Physio Co'].iloc[0])
            },
            {
                "name": "Maternity Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_maternityLimit13"),
                "value": str(cat3['Maternity - Married Females'].iloc[0])
            },
            {
                "name": "Maternity CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_maternityOPcopay13"),
                "value": self.format_percentage_value(cat3['Maternity - Married Females CO'].iloc[0])
            },
            {
                "name": "Maternity IP CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_maternityIPcopay13"),
                "value": self.format_percentage_value(cat3['Maternity - Married Females Ip'].iloc[0])
            },
            {
                "name": "Renal Dialysis",
                "selector": self.get_field_selector("ContentBoady1_ddl_RenalDialysis13"),
                "value": str(cat3['Renal Dialysis'].iloc[0])
            },
            {
                "name": "Organ Transplantation",
                "selector": self.get_field_selector("ContentBoady1_ddl_OrganTransplantation13"),
                "value": "Covered"
            },
            {
                "name": "Dental Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_dentalLimit13"),
                "value": str(cat3['Dental'].iloc[0])
            },
            {
                "name": "Dental CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_dentalcopay13"),
                "value": self.format_percentage_value(cat3['Dental CO'].iloc[0])
            },
            {
                "name": "Optical Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_opticalLimit13"),
                "value": str(cat3['Optical'].iloc[0])
            },
            {
                "name": "Optical CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_opticalCopay13"),
                "value": self.format_percentage_value(cat3['Optical CO'].iloc[0])
            },
            {
                "name": "Alternative Medicine Limit",
                "selector": self.get_field_selector("ContentBoady1_ddl_alterMedLim13"),
                "value": str(cat3['Alternative Medicine'].iloc[0])
            },
            {
                "name": "Alternative Medicine CO",
                "selector": self.get_field_selector("ContentBoady1_ddl_altrMedCopay13"),
                "value": self.format_percentage_value(cat3['Alternative Medicine Co'].iloc[0])
            },
            {
                "name": "Psychiatry",
                "selector": self.get_field_selector("ContentBoady1_ddl_Psychiatric13"),
                "value": str(cat3['Psychiatry'].iloc[0])
            },
            {
                "name": "Repatriation of Mortal remains",
                "selector": self.get_field_selector("ContentBoady1_ddl_Repartiation13"),
                "value": str(cat3['Repatriation of Mortal remains'].iloc[0])
            },
            {
                "name": "International Assistance",
                "selector": self.get_field_selector("ContentBoady1_ddl_InternationalAssistance13"),
                "value": str(cat3['Assist America'].iloc[0])
            },
            {
                "name": "Telehealth Consultation",
                "selector": self.get_field_selector("ContentBoady1_ddl_Teleconsultation13"),
                "value": str(cat3['Telehealth Consultation'].iloc[0])
            }
        ]
        
        # Fill each field
        for field in fields:
            success = await self.select_option_with_error_handling(
                field["name"],
                field["selector"],
                field["value"]
            )
            
            if not success:
                nlg_logger.error(f"Failed to fill field {field['name']} with value {field['value']}")
                return False
        
        nlg_logger.debug("Category 3 completed successfully")
        return True