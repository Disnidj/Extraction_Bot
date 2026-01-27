# src/pages/takaful/categories/category_a_page.py

import asyncio

from src.utils.support_functions import convert_to_int
from src.utils.logger import qatar_logger


class Category1Page:
    def __init__(self, page):
        self.page = page
        

    async def fill_category_1(self, df1, catA):
        
        # Select option for 'Annual Limit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[3]/td[2]/select').select_option(
                label=str(catA['Annual Limit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Annual Limit Filled " + str(catA['Annual Limit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Territory'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[4]/td[2]/select').select_option(
                label=str(catA['Territory'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Territory Filled " + str(catA['Territory'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        
        # # Select option for 'OPD Scope'
        # try:
        #     await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[5]/td[2]/select').select_option(
        #         label=" Only Clinics and Medical Centers")
        #     await asyncio.sleep(0.1)
        
        #     qatar_logger.debug("OPD Scope Filled " + " Only Clinics and Medical Centers")
        
        # except Exception as e:
        #     qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Deductable'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[6]/td[2]/select').select_option(
                label=str(catA['Deductable'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Deductable Filled " + str(catA['Deductable'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Pharmacy'###
        try:
            pharmacy_value = int(catA['Pharmacy'].iloc[0] * 100)
            pharmacy_label = f"{pharmacy_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[7]/td[2]/select').select_option(
                label=pharmacy_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Pharmacy Filled " + pharmacy_label)
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Pharmacy Sublimit'####
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[8]/td[2]/select').select_option(
                label=str(catA['Pharmacy Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Pharmacy Sublimit Filled " + str(catA['Pharmacy Sublimit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
            

        # Select option for 'Lab & Diagnostics Co-pay'###
        try:
            LabDiagnosticsCoPay_value = int(catA['Lab & Diagnostics Co-pay'].iloc[0] * 100)
            LabDiagnosticsCoPay_label = f"{LabDiagnosticsCoPay_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[9]/td[2]/select').select_option(
                label=LabDiagnosticsCoPay_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Lab & Diagnostics Co-pay Filled " + LabDiagnosticsCoPay_label)
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Lab & Diagnostics Sublimit'###
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[10]/td[2]/select').select_option(
                label=str(catA['Lab & Diagnostics Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Lab & Diagnostics Sublimit Filled " + str(catA['Lab & Diagnostics Sublimit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Physio Co'###
        try:
            PhysioCo_value = int(catA['Physio Co'].iloc[0] * 100)
            PhysioCo_label = f"{PhysioCo_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[11]/td[2]/select').select_option(
                label=PhysioCo_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Physio Co Filled " + PhysioCo_label)
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Physio'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[12]/td[2]/select').select_option(
                label=str(catA['Physio'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Physio Filled " + str(catA['Physio'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Maternity In-patient Sublimit'###
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[13]/td[2]/select').select_option(
                label=str(catA['Maternity In-patient Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Maternity In-patient Sublimit Filled " + str(catA['Maternity In-patient Sublimit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Maternity In-patient Co-pay'###
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[14]/td[2]/select').select_option(
                label=str(catA['Maternity In-patient Co-pay'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Maternity In-patient Co-pay Filled " + str(catA['Maternity In-patient Co-pay'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
       

        # Select option for 'Maternity Outpatient limit'###
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[15]/td[2]/select').select_option(
                label=str(catA['Maternity Outpatient limit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Maternity Outpatient limit Filled " + str(catA['Maternity Outpatient limit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Maternity Outpatient limit value'###
        try:
            MaternityOutpatientLimit_value = int(catA['Maternity Outpatient limit Value'].iloc[0] * 100)
            MaternityOutpatientLimit_label = f"{MaternityOutpatientLimit_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[16]/td[2]/select').select_option(
                label=MaternityOutpatientLimit_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Maternity Outpatient limit Filled " + MaternityOutpatientLimit_label)
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        
        # Select option for 'Repatriation of Mortal remains'###
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[17]/td[2]/select').select_option(
                label=str(catA['Repatriation of Mortal remains'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Repatriation of Mortal remains Filled " + str(catA['Repatriation of Mortal remains'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Daily Cash Benefit' (mapping need)###
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[18]/td[2]/select').select_option(
                label=str(catA['Daily Cash Benefit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Daily Cash Benefit Filled " + str(catA['Daily Cash Benefit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Home Nursing Charges' (excel has no value)###
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[19]/td[2]/select').select_option(
                label=str(catA['Home Nursing Charges'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Home Nursing Charges Filled " + str(catA['Home Nursing Charges'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Alternative treatment Sublimit'###
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[20]/td[2]/select').select_option(
                label=str(catA['Alternative treatment Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Alternative treatment Sublimit Filled " + str(catA['Alternative treatment Sublimit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Alternative treatment Copay'###
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[21]/td[2]/select').select_option(
                label=str(catA['Alternative treatment Copay'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Alternative treatment Copay Filled " + str(catA['Alternative treatment Copay'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

      
        #-------------------Tick the Optional Benefits-------------------

        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[22]/td/input').check()
            await asyncio.sleep(0.1)

            qatar_logger.debug("Checkbox Marke")

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        #-----------------------------------------------------------------
            
        # Helper function for formatting numeric values
        def format_value(value):
            if isinstance(value, (int, float)):
                return f"{value:,}"  # Format number with commas
            else:
                return str(value)
            

        # Select option for 'Dental'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[23]/td[2]/select').select_option(
                label=format_value(catA['Dental'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Dental Filled " + str(catA['Dental'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
            
            
        # Select option for 'Dental CO'
        try:
            DentalCO_value = int(catA['Dental CO'].iloc[0] * 100)
            DentalCO_label = f"{DentalCO_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[24]/td[2]/select').select_option(
                label=DentalCO_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Dental CO Filled " + DentalCO_label)

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
            

        # Select option for 'Optical' (excel value has ' ')
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[25]/td[2]/select').select_option(
                label=format_value(catA['Optical'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Optical Filled " + str(catA['Optical'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

            
        # Select option for 'Optical CO'
        try:
            OpticalCO_value = int(catA['Optical CO'].iloc[0] * 100)
            OpticalCO_label = f"{OpticalCO_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[26]/td[2]/select').select_option(
                label=OpticalCO_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Optical CO Filled " + OpticalCO_label)

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Dialysis Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[27]/td[2]/select').select_option(
                label=str(catA['Dialysis Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Dialysis Sublimit Filled " + str(catA['Dialysis Sublimit'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Congenital Condition Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[28]/td[2]/select').select_option(
                label=str(catA['Congenital Condition Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Congenital Condition Sublimit Filled " + str(catA['Congenital Condition Sublimit'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Medical Appliances Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[29]/td[2]/select').select_option(
                label=str(catA['Medical Appliances Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Medical Appliances Sublimit Filled " + str(catA['Medical Appliances Sublimit'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
            
       
        
        qatar_logger.debug("Category 1 Filled")
        