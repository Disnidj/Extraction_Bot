import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import convert_to_int, extract_dropdown_values
from src.utils.logger import daman_logger

class Category3Page:
    def __init__(self, page):
        self.page = page

    async def fill_category_3(self, catC, salary_C, region, tpa, network):
        daman_logger.debug("Category C Started")
        # Click Add Another Category
        await self.page.wait_for_selector('//input[@type="button" and contains(@value,"Add Another Category")]', timeout=5000)
        await self.page.click('//input[@type="button" and contains(@value,"Add Another Category")]')
        await asyncio.sleep(1)
        daman_logger.debug("Clicked Add Another Category")

        # ----------------------------------------- Select option for 'CAT C' ---------------------------------------------------------
        c_category = "CAT " + str(catC['Category'].iloc[0]).strip()
        daman_logger.info(f"Category C name: {c_category}")
        print("cat value:" + c_category)
        await self.page.fill('input[name="smeQuotationDTO.categories[2].categoryName"]', value=c_category.rstrip())
        await asyncio.sleep(MAX_SLEEP)
        daman_logger.debug("Category C Name filled") 

        visa = str(catC['Region'].iloc[0])
        daman_logger.info(f"Category C visa: {visa}")
        await self.select_option_with_error_handling(region, tpa, network, "Visa", visa, 'select[name="smeQuotationDTO.categories[2].visa"]')
        await asyncio.sleep(MAX_SLEEP)
        daman_logger.debug("Category C visa filled")       
    
        # Select option for 'Plan'
        plan = str(catC['TPA'].iloc[0])
        print("Category C Plan Value:" + plan)
        await self.select_option_with_error_handling(region, tpa, network, "Plan", plan, 'select[name="smeQuotationDTO.categories[2].plan"]')
        await asyncio.sleep(MAX_SLEEP)
        daman_logger.debug("Category C Plan filled")
        
        # Select option for 'Salary Band'
        await self.select_option_with_error_handling(region, tpa, network, "Salary Band", salary_C, 'select[name="smeQuotationDTO.categories[2].salaryBand"]')
        await asyncio.sleep(MAX_SLEEP)
        daman_logger.debug("Category C Salary Band filled")

        # Select option for 'network UAE'
        networkUAE = str(catC['Network'].iloc[0])
        print("Category C Network UAE Value:" + networkUAE)
        await self.select_option_with_error_handling(region, tpa, network, "Network UAE", networkUAE, 'select[name="smeQuotationDTO.categories[2].benefits.networkUAE"]')
        await asyncio.sleep(MAX_SLEEP)
        daman_logger.debug("Category C network UAE filled")
        
        #---------------------------------------------------------------------------#
        
        # Click Customized Benefits
        await self.page.wait_for_selector('//*[@id="sme-benefit-2"]/a/span', timeout=5000)
        await self.page.click('//*[@id="sme-benefit-2"]/a/span')
        await asyncio.sleep(10)
        daman_logger.debug("Clicked Customized Benefits")

        fields_to_fill = [
            ('//*[@id="smeQuotationDTO.categories[2].benefits.annualLimit"]', str(catC['Annual Limit'].iloc[0]), "Annual Limit"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.territorialLimit"]', str(catC['Territory'].iloc[0]), "Territorial Limit"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.nonNetwork"]', str(catC['Reimbursement'].iloc[0]), "Non Network"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.pcDeductible"]', str(catC['Deductable'].iloc[0]), "PC Deductible"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.pcCopay"]', str(catC['Diagnostic/Lab Copay'].iloc[0]), "PC Copay"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.pcOutOfPocket"]', str(catC['Consultation Limit'].iloc[0]), "PC Out of Pocket"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.pharmacyLimit"]', str(catC['Limit of Phamacy'].iloc[0]), "Pharmacy Limit"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.pharmacyCoverage"]', str(catC['Pharmacy'].iloc[0]), "Pharmacy Coverage"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.dentalCoverage"]', str(catC['Dental Copay'].iloc[0]), "Dental Coverage"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.dentalLimit"]', str(catC['Dental'].iloc[0]), "Dental Limit"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.opticalCoverage"]', str(catC['Optical CO'].iloc[0]), "Optical Coverage"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.opticalLimit"]', str(catC['Optical'].iloc[0]), "Optical Limit"),
            ('//*[@id="smeQuotationDTO.categories[2].benefits.ipMat"]', str(catC['Maternity - Married Females'].iloc[0]), "IP Mat"),
        ]

        for xpath, value, field_name in fields_to_fill:
            success = await self.select_option_with_error_handling(region, tpa, network, field_name, value, xpath)
            if success != True:
                daman_logger.error(f"Failed to fill field {field_name} with value {value}")
                daman_logger.error(f"Failed XPath: {xpath}")
                return

        # ...existing code for commented-out maternity fields...

        #---------------------------------------------------------------------#
        
        await self.page.wait_for_selector('//*[@id="sme_plan_benefits_wrap_2"]/div/div[2]/input[3]', timeout=5000)
        await self.page.click('//*[@id="sme_plan_benefits_wrap_2"]/div/div[2]/input[3]')
        await asyncio.sleep(10)
        daman_logger.debug("Clicked Saved Button")
        
        daman_logger.debug("Category C Completed")
        print('Category C Completed')
        return True
    

    async def _fill_field_with_timeout(self, selector, value, field_name):
        pass  # No longer used, kept for backward compatibility if needed

    async def select_option_with_error_handling(self, region, tpa, network, field_name, value, selector, portal_name="DAMAN"):
        try:
            cleaned_value = str(value).strip()
            if cleaned_value.lower() == 'nan' or cleaned_value == '':
                daman_logger.debug(f"Skipping {field_name} as value is empty or NaN")
                return True
            daman_logger.debug(f"{field_name} Value (Before Apply): {cleaned_value}")
            await extract_dropdown_values(self.page, region, tpa, network, field_name, selector, portal_name)
            await self.page.select_option(selector, value=cleaned_value.rstrip(), timeout=3000)
            daman_logger.debug(f"{field_name} Value (After Apply): {cleaned_value}")
            await asyncio.sleep(MAX_SLEEP)
            daman_logger.debug(f"{field_name} Filled")
            return True
        except Exception as e:
            daman_logger.error(f"Error occurred while selecting {field_name}: {e}")
            return False