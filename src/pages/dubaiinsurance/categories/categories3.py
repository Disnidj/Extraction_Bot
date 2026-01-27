import asyncio
import asyncio
import os
# from src.utils.load_yaml import DUBAIINSURANCE_QUOTATION_DIR
from src.utils.logger import dubaiinsurance_logger as logger

class Categories3:
    def __init__(self, page, df2, cat2):
        self.page = page
        self.df2 = df2

    def get_value(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[0]).strip()
        except KeyError:
            logger.error(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            logger.error(f"IndexError: No data found in column '{column_name}'.")
            return None
        
    def get_value_catB(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[1]).strip()
        except KeyError:
            logger.error(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            logger.error(f"IndexError: No data found in column '{column_name}'.")
            return None
        
    def get_value_catC(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[2]).strip()
        except KeyError:
            logger.error(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            logger.error(f"IndexError: No data found in column '{column_name}'.")
            return None

    async def categories3_information(self):

        logger.info("Started Filling Category 1 Information")

        try:

            # TPA
            tpa = self.get_value("TPA")
            logger.debug(f"TPA (Before Apply): {tpa}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_tpaben31").select_option(tpa)
            logger.debug(f"TPA (After Apply): {tpa}")
            await asyncio.sleep(4)
            
            # Network
            network = self.get_value("Network")
            logger.debug(f"Network (Before Apply): {network}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Prod31").select_option(network)
            logger.debug(f"Network (After Apply): {network}")
            await asyncio.sleep(3)

            # Annual Limit
            annual_limit = self.get_value("Annual Limit")
            logger.debug(f"Annual Limit (Before Apply): {annual_limit}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_AnnualLimitben31").select_option(annual_limit)
            logger.debug(f"Annual Limit (After Apply): {annual_limit}")
            await asyncio.sleep(3)

            # Territory
            territory = self.get_value("Territory")
            logger.debug(f"Territory (Before Apply): {territory}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TerritorialCoverELCben31").select_option(territory)
            logger.debug(f"Territory (After Apply): {territory}")
            await asyncio.sleep(3)

            # Deductable
            deductable = self.get_value("Deductable")
            logger.debug(f"Deductable (Before Apply): {deductable}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_dedben31").select_option(deductable)
            logger.debug(f"Deductable (After Apply): {deductable}")
            await asyncio.sleep(5)

            # Network - Defualt
            op_co_insurance = self.get_value("Op Co Insurance")
            print(op_co_insurance)
            logger.debug(f"Op Co Insurance (Before Apply): {op_co_insurance}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_copayben31").select_option(op_co_insurance)
            logger.debug(f"Op Co Insurance (After Apply): {op_co_insurance}")
            await asyncio.sleep(3)
            print(op_co_insurance)

            # Limit of Phamacy
            limit_of_phamacy = self.get_value("Limit of Phamacy")
            logger.debug(f"Limit of Phamacy (Before Apply): {limit_of_phamacy}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHLimitben31").select_option(limit_of_phamacy)
            logger.debug(f"Limit of Phamacy (After Apply): {limit_of_phamacy}")
            await asyncio.sleep(3)

            # Medicine
            medicine = self.get_value("Medicine")
            logger.debug(f"Medicine (Before Apply): {medicine}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MedTypeben31").select_option(medicine)
            logger.debug(f"Medicine (After Apply): {medicine}")
            await asyncio.sleep(3)

            # Pharmacy
            pharmacy = self.get_value("Pharmacy")
            try:
                pharmacy = float(pharmacy) * 100
                pharmacy = f"{int(pharmacy)}%" 
            except ValueError:
                pass

            logger.debug(f"Pharmacy (Before Apply): {pharmacy}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHCopayben31").select_option(pharmacy)
            logger.debug(f"Pharmacy (After Apply): {pharmacy}")
            await asyncio.sleep(3)
            print(f"Final value sent: {pharmacy}")

            # Physio
            physio = self.get_value("Physio")
            logger.debug(f"Physio (Before Apply): {physio}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physioben31").select_option(physio)
            logger.debug(f"Physio (After Apply): {physio}")
            await asyncio.sleep(3)

            # Physio CO
            physio_co = self.get_value("Physio Co")
            try:
                physio_co = float(physio_co) * 100
                physio_co = f"{int(physio_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Physio CO (Before Apply): {physio_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physiocopay31").select_option(physio_co)
            logger.debug(f"Physio CO (After Apply): {physio_co}")
            await asyncio.sleep(3)
            # print(f"Final value sent: {physio_co}")
            
            # Maternity - Married Females
            married_females = self.get_value("Maternity - Married Females")
            logger.debug(f"Materinity - Married (Before Apply): {married_females}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Matben31").select_option(married_females)
            logger.debug(f"Materinity - Married: {married_females}")
            print(f"Maternity - Married Females (After Apply): {married_females}")
            await asyncio.sleep(3)        

            # Maternity - Married Females CO
            married_females_co = self.get_value("Maternity - Married Females CO")
            try:
                married_females_co = float(married_females_co) * 100
                married_females_co = f"{int(married_females_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Maternity - Married Females CO (Before Apply): {married_females_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MatCopayben31").select_option(married_females_co)
            logger.debug(f"Maternity - Married Females CO (After Apply): {married_females_co}")
            await asyncio.sleep(3)
            print(f"married_females_co is : {married_females_co}")

            # Dental
            dental = self.get_value("Dental")
            logger.debug(f"Dental (Before Apply): {dental}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Dentben31").select_option(dental)
            logger.debug(f"Dental (After Apply): {dental}")
            await asyncio.sleep(1)

            # Dental CO
            dental_co = self.get_value("Dental CO")
            try:
                dental_co = float(dental_co) * 100
                dental_co = f"{int(dental_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Dental CO (Before Apply): {dental_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_DentCopayben31").select_option(dental_co)
            logger.debug(f"Dental CO (After Apply): {dental_co}")
            await asyncio.sleep(3)
            print(f"Denatal CO is : {dental_co}")

            # Optical
            optical = self.get_value("Optical")
            logger.debug(f"Optical (Before Apply): {optical}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Optben31").select_option(optical)
            logger.debug(f"Optical (After Apply): {optical}")
            await asyncio.sleep(1)

            # Optical CO
            optical_co = self.get_value("Optical CO")
            try:
                optical_co = float(optical_co) * 100
                optical_co = f"{int(optical_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Optical CO (Before Apply): {optical_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_OptCopayben31").select_option(optical_co)
            logger.debug(f"Optical CO (After Apply): {optical_co}")
            await asyncio.sleep(3)
            print(f"Optical CO is : {optical_co}")

            # Life benefit - Death due to any cause
            life_benefit = self.get_value("Life benefit - Death due to any cause")
            logger.debug(f"Life benefit - Death due to any cause (Before Apply): {life_benefit}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_lifeLimit31").select_option(life_benefit)
            logger.debug(f"Life benefit - Death due to any cause (After Apply): {life_benefit}")
            await asyncio.sleep(1)

            # Repatriation of Mortal remains
            repatriation = self.get_value("Repatriation of Mortal remains")
            logger.debug(f"Repatriation of Mortal remains (Before Apply): {repatriation}")
            print("Repatriation"+ repatriation)
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_RepatriLimit31").select_option(repatriation)
            logger.debug(f"Repatriation of Mortal remains (After Apply): {repatriation}")
            await asyncio.sleep(1)


            # Telehealth Consultation
        
            tele_consultation = self.get_value("Telehealth Consultation")
            logger.debug(f"Telehealth Consultation (Before Apply): {tele_consultation}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TeleLimit31").select_option(tele_consultation)
            logger.debug(f"Telehealth Consultation (After Apply): {tele_consultation}")
            await asyncio.sleep(1)
        

            # Wellness Package
            wellness_package = self.get_value("Wellness Package")
            logger.debug(f"Wellness Package (Before Apply): {wellness_package}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_WellPa31").select_option(wellness_package)
            logger.debug(f"Wellness Package (After Apply): {wellness_package}")
            await asyncio.sleep(0.5)

            # Assist America
            assist_america = self.get_value("Assist America")
            logger.debug(f"Assist America (Before Apply): {assist_america}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_ISOS31").select_option(assist_america)
            logger.debug(f"Assist America (After Apply): {assist_america}")
            await asyncio.sleep(0.5)

            # Psychiatry
            psychiatry = self.get_value("Psychiatry")
            logger.debug(f"Psychiatry (Before Apply): {psychiatry}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_psch31").select_option(psychiatry)
            logger.debug(f"Psychiatry (After Apply): {psychiatry}")
            await asyncio.sleep(0.5)

            # Alternative Medicine
            alternative_medicine = self.get_value("Alternative Medicine")
            logger.debug(f"Alternative Medicine (Before Apply): {alternative_medicine}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_alterMedben31").select_option(alternative_medicine)
            logger.debug(f"Alternative Medicine (After Apply): {alternative_medicine}")
            await asyncio.sleep(0.5)


        #       ------------------------CAT B------------------------------

            logger.info("Started Filling Category 2 Information")
            # Network
            network = self.get_value_catB("Network")
            logger.debug(f"Network (Before Apply): {network}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Prod32").select_option(network)
            logger.debug(f"Network (After Apply): {network}")
            await asyncio.sleep(3)

            # Annual Limit
            annual_limit = self.get_value_catB("Annual Limit")
            logger.debug(f"Annual Limit (Before Apply): {annual_limit}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_AnnualLimitben32").select_option(annual_limit)
            logger.debug(f"Annual Limit (After Apply): {annual_limit}")
            await asyncio.sleep(3)

            # Territory
            territory = self.get_value_catB("Territory")
            logger.debug(f"Territory (Before Apply): {territory}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TerritorialCoverELCben32").select_option(territory)
            logger.debug(f"Territory (After Apply): {territory}")
            await asyncio.sleep(3)

            # Deductable
            deductable = self.get_value_catB("Deductable")
            logger.debug(f"Deductable (Before Apply): {deductable}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_dedben32").select_option(deductable)
            logger.debug(f"Deductable (After Apply): {deductable}")
            await asyncio.sleep(5)

            # Network - Defualt
            # op_co_insurance = self.get_value_catB("Op Co Insurance")
            # print(op_co_insurance)
            # await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_copayben32").select_option(op_co_insurance)
            # await asyncio.sleep(3)
            # print(op_co_insurance)

            # Limit of Phamacy
            limit_of_phamacy = self.get_value_catB("Limit of Phamacy")
            logger.debug(f"Limit of Phamacy (Before Apply): {limit_of_phamacy}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHLimitben32").select_option(limit_of_phamacy)
            logger.debug(f"Limit of Phamacy (After Apply): {limit_of_phamacy}")
            await asyncio.sleep(3)

            # Medicine
            medicine = self.get_value_catB("Medicine")
            logger.debug(f"Medicine (Before Apply): {medicine}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MedTypeben32").select_option(medicine)
            logger.debug(f"Medicine (After Apply): {medicine}")
            await asyncio.sleep(3)

            # Pharmacy
            pharmacy = self.get_value_catB("Pharmacy")
            try:
                pharmacy = float(pharmacy) * 100
                pharmacy = f"{int(pharmacy)}%" 
            except ValueError:
                pass

            logger.debug(f"Pharmacy (Before Apply): {pharmacy}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHCopayben32").select_option(pharmacy)
            logger.debug(f"Pharmacy (After Apply): {pharmacy}")
            await asyncio.sleep(3)
            print(f"Final value sent: {pharmacy}")

            # Physio
            physio = self.get_value_catB("Physio")
            logger.debug(f"Physio (Before Apply): {physio}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physioben32").select_option(physio)
            logger.debug(f"Physio (After Apply): {physio}")
            await asyncio.sleep(3)

            # Physio CO
            physio_co = self.get_value_catB("Physio Co")
            try:
                physio_co = float(physio_co) * 100
                physio_co = f"{int(physio_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Physio CO (Before Apply): {physio_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physiocopay32").select_option(physio_co)
            logger.debug(f"Physio CO (After Apply): {physio_co}")
            await asyncio.sleep(3)
            print(f"Final value sent: {physio_co}")

            # Maternity - Married Females
            married_females = self.get_value_catB("Maternity - Married Females")
            logger.debug(f"Maternity - Married Females (Before Apply): {married_females}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Matben32").select_option(married_females)
            logger.debug(f"Maternity - Married Females (After Apply): {married_females}")
            await asyncio.sleep(3)

            # Maternity - Married Females CO
            married_females_co = self.get_value_catB("Maternity - Married Females CO")
            try:
                married_females_co = float(married_females_co) * 100
                married_females_co = f"{int(married_females_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Maternity - Married Females CO (Before Apply): {married_females_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MatCopayben32").select_option(married_females_co)
            logger.debug(f"Maternity - Married Females CO (After Apply): {married_females_co}")
            await asyncio.sleep(3)
            print(f"married_females_co is : {married_females_co}")

            # Dental
            dental = self.get_value_catB("Dental")
            logger.debug(f"Dental (Before Apply): {dental}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Dentben32").select_option(dental)
            logger.debug(f"Dental (After Apply): {dental}")
            await asyncio.sleep(1)

            # Dental CO
            dental_co = self.get_value_catB("Dental CO")
            try:
                dental_co = float(dental_co) * 100
                dental_co = f"{int(dental_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Dental CO (Before Apply): {dental_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_DentCopayben32").select_option(dental_co)
            logger.debug(f"Dental CO (After Apply): {dental_co}")
            await asyncio.sleep(3)
            print(f"Denatal CO is : {dental_co}")

            # Optical
            optical = self.get_value_catB("Optical")
            logger.debug(f"Optical (Before Apply): {optical}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Optben32").select_option(optical)
            logger.debug(f"Optical (After Apply): {optical}")
            await asyncio.sleep(1)

            # Optical CO
            optical_co = self.get_value_catB("Optical CO")
            try:
                optical_co = float(optical_co) * 100
                optical_co = f"{int(optical_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Optical CO (Before Apply): {optical_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_OptCopayben32").select_option(optical_co)
            logger.debug(f"Optical CO (After Apply): {optical_co}")
            await asyncio.sleep(3)
            print(f"Optical CO is : {optical_co}")

            # Life benefit - Death due to any cause
            life_benefit = self.get_value_catB("Life benefit - Death due to any cause")
            logger.debug(f"Life benefit - Death due to any cause (Before Apply): {life_benefit}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_lifeLimit32").select_option(life_benefit)             
            logger.debug(f"Life benefit - Death due to any cause (After Apply): {life_benefit}")
            await asyncio.sleep(1)

            # Repatriation of Mortal remains
            repatriation = self.get_value_catB("Repatriation of Mortal remains")
            logger.debug(f"Repatriation of Mortal remains (Before Apply): {repatriation}")
            print("Repatriation"+ repatriation)
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_RepatriLimit32").select_option(repatriation)           
            logger.debug(f"Repatriation of Mortal remains (After Apply): {repatriation}")
            await asyncio.sleep(1)

            # Telehealth Consultation
        
            tele_consultation = self.get_value_catB("Telehealth Consultation")
            logger.debug(f"Telehealth Consultation (Before Apply): {tele_consultation}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TeleLimit32").select_option(tele_consultation)          
            logger.debug(f"Telehealth Consultation (After Apply): {tele_consultation}")
            await asyncio.sleep(1)
        

            # Wellness Package
            wellness_package = self.get_value_catB("Wellness Package")
            logger.debug(f"Wellness Package (Before Apply): {wellness_package}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_WellPa32").select_option(wellness_package)          
            logger.debug(f"Wellness Package (After Apply): {wellness_package}")
            await asyncio.sleep(0.5)

            # Assist America
            assist_america = self.get_value_catB("Assist America")
            logger.debug(f"Assist America (Before Apply): {assist_america}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_ISOS32").select_option(assist_america)          
            logger.debug(f"Assist America (After Apply): {assist_america}")
            await asyncio.sleep(0.5)

            # Psychiatry
            psychiatry = self.get_value_catB("Psychiatry")
            logger.debug(f"Psychiatry (Before Apply): {psychiatry}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_psch32").select_option(psychiatry)          
            logger.debug(f"Psychiatry (After Apply): {psychiatry}")
            await asyncio.sleep(0.5)

            # Alternative Medicine
            alternative_medicine = self.get_value_catB("Alternative Medicine")
            logger.debug(f"Alternative Medicine (Before Apply): {alternative_medicine}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_alterMedben32").select_option(alternative_medicine)
            logger.debug(f"Alternative Medicine (After Apply): {alternative_medicine}")
            await asyncio.sleep(0.5)


        #       ------------------------CAT C------------------------------
            # await asyncio.sleep(1000)
            logger.info("Started Filling Category 3 Information")
            # Network
            network = self.get_value_catC("Network")
            logger.debug(f"Network (Before Apply): {network}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Prod33").select_option(network)
            logger.debug(f"Network (After Apply): {network}")
            await asyncio.sleep(3)

            # Annual Limit
            annual_limit = self.get_value_catC("Annual Limit")
            logger.debug(f"Annual Limit (Before Apply): {annual_limit}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_AnnualLimitben33").select_option(annual_limit)
            logger.debug(f"Annual Limit (After Apply): {annual_limit}")
            await asyncio.sleep(3)

            # Territory
            territory = self.get_value_catC("Territory")
            logger.debug(f"Territory (Before Apply): {territory}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TerritorialCoverELCben33").select_option(territory)
            logger.debug(f"Territory (After Apply): {territory}")
            await asyncio.sleep(3)

            # Deductable
            deductable = self.get_value_catC("Deductable")
            logger.debug(f"Deductable (Before Apply): {deductable}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_dedben33").select_option(deductable)
            logger.debug(f"Deductable (After Apply): {deductable}")
            await asyncio.sleep(5)

            # Network - Defualt
            # op_co_insurance = self.get_value_catC("Op Co Insurance")
            # print(op_co_insurance)
            # await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_copayben33").select_option(op_co_insurance)
            # await asyncio.sleep(3)
            # print(op_co_insurance)

            # Limit of Phamacy
            limit_of_phamacy = self.get_value_catC("Limit of Phamacy")
            logger.debug(f"Limit of Phamacy (Before Apply): {limit_of_phamacy}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHLimitben33").select_option(limit_of_phamacy)
            logger.debug(f"Limit of Phamacy (After Apply): {limit_of_phamacy}")
            await asyncio.sleep(3)

            # Medicine
            medicine = self.get_value_catC("Medicine")
            logger.debug(f"Medicine (Before Apply): {medicine}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MedTypeben33").select_option(medicine)
            logger.debug(f"Medicine (After Apply): {medicine}")
            await asyncio.sleep(3)

            # Pharmacy
            pharmacy = self.get_value_catC("Pharmacy")
            try:
                pharmacy = float(pharmacy) * 100
                pharmacy = f"{int(pharmacy)}%" 
            except ValueError:
                pass

            logger.debug(f"Pharmacy (Before Apply): {pharmacy}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHCopayben33").select_option(pharmacy)
            logger.debug(f"Pharmacy (After Apply): {pharmacy}")
            await asyncio.sleep(3)
            print(f"Final value sent: {pharmacy}")

            # Physio
            physio = self.get_value_catC("Physio")
            logger.debug(f"Physio (Before Apply): {physio}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physioben33").select_option(physio)
            logger.debug(f"Physio (After Apply): {physio}")
            await asyncio.sleep(3)

            # Physio CO
            physio_co = self.get_value_catC("Physio Co")
            try:
                physio_co = float(physio_co) * 100
                physio_co = f"{int(physio_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Physio CO (Before Apply): {physio_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator('//*[@id="ddl_Physiocopay33"]').select_option(physio_co)
            logger.debug(f"Physio CO (After Apply): {physio_co}") #ddl_Physiocopayben33
            await asyncio.sleep(3)
            print(f"Final value sent: {physio_co}")


            # Maternity - Married Females
            married_females = self.get_value_catC("Maternity - Married Females")
            logger.debug(f"Maternity - Married Females (Before Apply): {married_females}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Matben33").select_option(married_females)
            logger.debug(f"Maternity - Married Females (After Apply): {married_females}")
            await asyncio.sleep(3)

            # Maternity - Married Females CO
            married_females_co = self.get_value_catC("Maternity - Married Females CO")
            try:
                married_females_co = float(married_females_co) * 100
                married_females_co = f"{int(married_females_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Maternity - Married Females CO (Before Apply): {married_females_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MatCopayben33").select_option(married_females_co)
            logger.debug(f"Maternity - Married Females CO (After Apply): {married_females_co}")
            await asyncio.sleep(3)
            print(f"married_females_co is : {married_females_co}")

            # Dental
            dental = self.get_value_catC("Dental")
            logger.debug(f"Dental (Before Apply): {dental}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Dentben33").select_option(dental)
            logger.debug(f"Dental (After Apply): {dental}")
            await asyncio.sleep(1)

            # Dental CO
            dental_co = self.get_value_catC("Dental CO")
            try:
                dental_co = float(dental_co) * 100
                dental_co = f"{int(dental_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Dental CO (Before Apply): {dental_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_DentCopayben33").select_option(dental_co)
            logger.debug(f"Dental CO (After Apply): {dental_co}")
            await asyncio.sleep(3)
            print(f"Denatal CO is : {dental_co}")

            # Optical
            optical = self.get_value_catC("Optical")
            logger.debug(f"Optical (Before Apply): {optical}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Optben33").select_option(optical)
            logger.debug(f"Optical (After Apply): {optical}")
            await asyncio.sleep(1)

            # Optical CO
            optical_co = self.get_value_catC("Optical CO")
            try:
                optical_co = float(optical_co) * 100
                optical_co = f"{int(optical_co)}%" 
            except ValueError:
                pass

            logger.debug(f"Optical CO (Before Apply): {optical_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_OptCopayben33").select_option(optical_co)
            logger.debug(f"Optical CO (After Apply): {optical_co}")
            await asyncio.sleep(3)
            print(f"Optical CO is : {optical_co}")

            # Life benefit - Death due to any cause
            life_benefit = self.get_value_catC("Life benefit - Death due to any cause")
            logger.debug(f"Life benefit - Death due to any cause (Before Apply): {life_benefit}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_lifeLimit33").select_option(life_benefit)             
            logger.debug(f"Life benefit - Death due to any cause (After Apply): {life_benefit}")
            await asyncio.sleep(1)

            # Repatriation of Mortal remains
            repatriation = self.get_value_catC("Repatriation of Mortal remains")
            logger.debug(f"Repatriation of Mortal remains (Before Apply): {repatriation}")
            print("Repatriation"+ repatriation)
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_RepatriLimit33").select_option(repatriation)           
            logger.debug(f"Repatriation of Mortal remains (After Apply): {repatriation}")
            await asyncio.sleep(5)

            # Telehealth Consultation
            
            tele_consultation = self.get_value_catC("Telehealth Consultation")
            logger.debug(f"Telehealth Consultation (Before Apply): {tele_consultation}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TeleLimit33").select_option(tele_consultation)          
            logger.debug(f"Telehealth Consultation (After Apply): {tele_consultation}")
            await asyncio.sleep(1)
            

            # Wellness Package
            wellness_package = self.get_value_catC("Wellness Package")
            logger.debug(f"Wellness Package (Before Apply): {wellness_package}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_WellPa33").select_option(wellness_package)          
            logger.debug(f"Wellness Package (After Apply): {wellness_package}")
            await asyncio.sleep(0.5)

            # Assist America
            assist_america = self.get_value_catC("Assist America")
            logger.debug(f"Assist America (Before Apply): {assist_america}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_ISOS33").select_option(assist_america)          
            logger.debug(f"Assist America (After Apply): {assist_america}")
            await asyncio.sleep(0.5)

            # Psychiatry
            psychiatry = self.get_value_catC("Psychiatry")
            logger.debug(f"Psychiatry (Before Apply): {psychiatry}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_psch33").select_option(psychiatry)          
            logger.debug(f"Psychiatry (After Apply): {psychiatry}")
            await asyncio.sleep(0.5)

            # Alternative Medicine
            alternative_medicine = self.get_value_catC("Alternative Medicine")
            logger.debug(f"Alternative Medicine (Before Apply): {alternative_medicine}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_alterMedben33").select_option(alternative_medicine)
            logger.debug(f"Alternative Medicine (After Apply): {alternative_medicine}")
            await asyncio.sleep(0.5)

            # Click Get Quote
            logger.debug("Clicking Get Quote button")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator('//*[@id="btn_quote"]').click()
            await asyncio.sleep(2)

            if not await self.page.locator("iframe[name=\"content\"]").content_frame.locator('#btn_submit').is_visible():
                logger.debug("Get Quote button not visible, clicking again")
                await self.page.locator("iframe[name=\"content\"]").content_frame.locator('//*[@id="btn_quote"]').click()
                logger.debug("Get Quote button clicked again")
                print("get quote")

            # # Download the Quotation
            # download_path = DUBAIINSURANCE_QUOTATION_DIR

            # # Ensure the download directory exists
            # if not os.path.exists(download_path):
            #     os.makedirs(download_path)

            # try:
            #     # Wait for the download to start
            #     async with self.page.expect_download(timeout=120000) as download_info:
            #         logger.info("Clicking submit button to download quotation")
            #         await asyncio.sleep(5)
            #         # Click the download button
            #         await self.page.locator("iframe[name=\"content\"]").content_frame.locator('#btn_submit').click()
            #         logger.info("Download button clicked")

            #         # Wait for the download to complete and save it to the specified path
            #         download = await download_info.value
            #         download_path_full = os.path.join(download_path, "quotation_dubaiinsurance.pdf")
            #         await download.save_as(download_path_full)
            #         logger.info(f"Downloaded quotation PDF to: {download_path_full}")
            #         print(f"Downloaded quotation PDF to: {download_path_full}")

            # except asyncio.TimeoutError:
            #     logger.error("Error: Timeout exceeded while waiting for the download.")
            #     print("Error: Timeout exceeded while waiting for the download.")
            # except Exception as e:
            #     logger.error(f"Unexpected error during download: {e}")
            #     print(f"Unexpected error during download: {e}")

            await asyncio.sleep(10)
            return True
        
        except Exception as e:
            logger.error(f"An error occurred while filling category 3 information: {e}")
            print(f"An error occurred while filling category 3 information: {e}")
            return False