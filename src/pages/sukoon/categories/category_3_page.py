import asyncio
from src.utils.load_yaml import MED_SLEEP
from src.utils.logger import sukoon_logger

class Category3Page:
    def __init__(self, page, df3, cat3):
        self.page = page
        self.df3 = df3

    def get_value(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df3[column_name].values[2])
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            return None
        
    async def fill_category_3(self):
      
        # Indemnity Limit
        indemnity_Limit = self.get_value("TPA")
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_2_UCCategory_0_ddlIndemnity_0', value=indemnity_Limit, timeout=90000) # Increase timeout to 90 seconds
        await asyncio.sleep(3)

        # Geographical Area (Territory)
        geographical_Area = self.get_value("Territory")
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_2_UCCategory_0_ddlGeographicalArea_0', value=geographical_Area)
        await asyncio.sleep(2)

        # Applicable Network
        applicable_Network = self.get_value("Network")
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_2_UCCategory_0_ddlNetwork_0', value=applicable_Network)
        await asyncio.sleep(2)
       
        # Deductible
        deductable = self.get_value("Deductable")
        print(type(deductable))
        sukoon_logger.debug('Deductable (Before Apply):'+deductable)
        deductable = int(float(deductable))
        print(deductable)
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_2_UCCategory_0_ddlDedcuctible_0', value=str(deductable))
        sukoon_logger.debug(f"Deductible Filled:::{deductable}")
        await asyncio.sleep(2)

        # Co-Insurance
        insurance = self.get_value("Op Co Insurance")
        print(insurance)
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_2_UCCategory_0_ddlCoinsurance_0', value=insurance)
        sukoon_logger.debug(f"Co-Insurance Filled:::{insurance}")
        await asyncio.sleep(2)
            
        # Co-Insurance
        insurance = self.get_value("Op Co Insurance")
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_2_UCCategory_0_ddlCoinsurance_0', value=insurance)
        await asyncio.sleep(2)

        # Dental Cover
        dental_Cover = self.get_value("Dental").capitalize()
        await self.page.locator('//*[@id="ContentPlaceHolder1_rptCategory_rptCategoryList_2_UCCategory_0_ddlDentalCover_0"]').select_option(value=dental_Cover)
        await asyncio.sleep(2)

        # Optical Cover
        optical_Cover = self.get_value("Optical").capitalize()
        await self.page.locator("#ContentPlaceHolder1_rptCategory_rptCategoryList_2_UCCategory_0_ddlOpticalCover_0").select_option(value=optical_Cover)
        
        await asyncio.sleep(6)

        lab_xray_cover = self.get_value("Lab & X-Ray").capitalize()
        sukoon_logger.debug(f"Lab & X-Ray Filled:::{lab_xray_cover}")
        if lab_xray_cover != 'Nan' :
            await self.page.locator('//*[@id="ContentPlaceHolder1_rptCategory_rptCategoryList_2_UCCategory_0_ddlLabXRay_0"]').select_option(value=lab_xray_cover)
        await asyncio.sleep(2.5)
    
        await asyncio.sleep(5)

     
        


        

   