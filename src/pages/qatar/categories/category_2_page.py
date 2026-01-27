import asyncio
from src.utils.support_functions import convert_to_int
from src.utils.logger import qatar_logger

class Category2Page:
    def __init__(self, page):
        self.page = page

    async def fill_category_2(self, df1, catB):
        # Select option for 'Annual Limit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[3]/td[3]/select').select_option(
                label=str(catB['Annual Limit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Annual Limit Filled " + str(catB['Annual Limit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Territory'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[4]/td[3]/select').select_option(
                label=str(catB['Territory'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Territory Filled " + str(catB['Territory'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        
        # # Select option for 'OPD Scope'
        # try:
        #     await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[5]/td[3]/select').select_option(
        #         label=" Only Clinics and Medical Centers")
        #     await asyncio.sleep(0.1)
        
        #     qatar_logger.debug("OPD Scope Filled " + " Only Clinics and Medical Centers")
        
        # except Exception as e:
        #     qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Deductable'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[6]/td[3]/select').select_option(
                label=str(catB['Deductable'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Deductable Filled " + str(catB['Deductable'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        
        # Select option for 'Pharmacy'
        try:
            pharmacy_value = int(catB['Pharmacy'].iloc[0] * 100)
            pharmacy_label = f"{pharmacy_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[7]/td[3]/select').select_option(
                label=pharmacy_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Pharmacy Filled " + pharmacy_label)
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Pharmacy Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[8]/td[3]/select').select_option(
                label=str(catB['Pharmacy Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Pharmacy Sublimit Filled " + str(catB['Pharmacy Sublimit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
            

        # Select option for 'Lab & Diagnostics Co-pay'
        try:
            LabDiagnosticsCoPay_value = int(catB['Lab & Diagnostics Co-pay'].iloc[0] * 100)
            LabDiagnosticsCoPay_label = f"{LabDiagnosticsCoPay_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[9]/td[3]/select').select_option(
                label=LabDiagnosticsCoPay_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Lab & Diagnostics Co-pay Filled " + LabDiagnosticsCoPay_label)
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Lab & Diagnostics Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[10]/td[3]/select').select_option(
                label=str(catB['Lab & Diagnostics Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Lab & Diagnostics Sublimit Filled " + str(catB['Lab & Diagnostics Sublimit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Physio Co'
        try:
            PhysioCo_value = int(catB['Physio Co'].iloc[0] * 100)
            PhysioCo_label = f"{PhysioCo_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[11]/td[3]/select').select_option(
                label=PhysioCo_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Physio Co Filled " + PhysioCo_label)
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Physio'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[12]/td[3]/select').select_option(
                label=str(catB['Physio'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Physio Filled " + str(catB['Physio'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Maternity In-patient Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[13]/td[3]/select').select_option(
                label=str(catB['Maternity In-patient Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Maternity In-patient Sublimit Filled " + str(catB['Maternity In-patient Sublimit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Maternity In-patient Co-pay'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[14]/td[3]/select').select_option(
                label=str(catB['Maternity In-patient Co-pay'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Maternity In-patient Co-pay Filled " + str(catB['Maternity In-patient Co-pay'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
       

        # Select option for 'Maternity Outpatient limit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[15]/td[3]/select').select_option(
                label=str(catB['Maternity Outpatient limit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Maternity Outpatient limit Filled " + str(catB['Maternity Outpatient limit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Maternity Outpatient limit value'
        try:
            MaternityOutpatientLimit_value = int(catB['Maternity Outpatient limit Value'].iloc[0] * 100)
            MaternityOutpatientLimit_label = f"{MaternityOutpatientLimit_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[16]/td[3]/select').select_option(
                label=MaternityOutpatientLimit_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Maternity Outpatient limit Filled " + MaternityOutpatientLimit_label)
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        
        # Select option for 'Repatriation of Mortal remains'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[17]/td[3]/select').select_option(
                label=str(catB['Repatriation of Mortal remains'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Repatriation of Mortal remains Filled " + str(catB['Repatriation of Mortal remains'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Daily Cash Benefit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[18]/td[3]/select').select_option(
                label=str(catB['Daily Cash Benefit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Daily Cash Benefit Filled " + str(catB['Daily Cash Benefit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Home Nursing Charges'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[19]/td[3]/select').select_option(
                label=str(catB['Home Nursing Charges'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Home Nursing Charges Filled " + str(catB['Home Nursing Charges'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Alternative treatment Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[20]/td[3]/select').select_option(
                label=str(catB['Alternative treatment Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Alternative treatment Sublimit Filled " + str(catB['Alternative treatment Sublimit'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Alternative treatment Copay'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[21]/td[3]/select').select_option(
                label=str(catB['Alternative treatment Copay'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Alternative treatment Copay Filled " + str(catB['Alternative treatment Copay'].iloc[0]))
        
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
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[23]/td[3]/select').select_option(
                label=format_value(catB['Dental'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Dental Filled " + str(catB['Dental'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
            
            
        # Select option for 'Dental CO'
        try:
            DentalCO_value = int(catB['Dental CO'].iloc[0] * 100)
            DentalCO_label = f"{DentalCO_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[24]/td[3]/select').select_option(
                label=DentalCO_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Dental CO Filled " + DentalCO_label)

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
            

        # Select option for 'Optical'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[25]/td[3]/select').select_option(
                label=format_value(catB['Optical'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Optical Filled " + str(catB['Optical'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

            
        # Select option for 'Optical CO'
        try:
            OpticalCO_value = int(catB['Optical CO'].iloc[0] * 100)
            OpticalCO_label = f"{OpticalCO_value}%"
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[26]/td[3]/select').select_option(
                label=OpticalCO_label)
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Optical CO Filled " + OpticalCO_label)

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Dialysis Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[27]/td[3]/select').select_option(
                label=str(catB['Dialysis Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Dialysis Sublimit Filled " + str(catB['Dialysis Sublimit'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Congenital Condition Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[28]/td[3]/select').select_option(
                label=str(catB['Congenital Condition Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Congenital Condition Sublimit Filled " + str(catB['Congenital Condition Sublimit'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")


        # Select option for 'Medical Appliances Sublimit'
        try:
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[1]/table/tr[29]/td[3]/select').select_option(
                label=str(catB['Medical Appliances Sublimit'].iloc[0]))
            await asyncio.sleep(0.1)
        
            qatar_logger.debug("Medical Appliances Sublimit Filled " + str(catB['Medical Appliances Sublimit'].iloc[0]))

        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
            
       
        
        qatar_logger.debug("Category 1 Filled")
