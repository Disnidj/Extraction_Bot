import asyncio
from src.utils.load_yaml import MED_SLEEP
from src.utils.logger import sukoon_logger
from src.utils.support_functions import extract_dropdown_values

class Category2Page:
    def __init__(self, page, df3, cat2, portal_name):
        self.page = page
        self.df3 = df3
        self.portal_name = portal_name

    def get_value(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df3[column_name].values[1])
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            return None
        
    async def fill_category_2(self, cat2):
        region = str(cat2['Region'].iloc[0])
        applicable_Network = self.get_value("Network")
        indemnity_Limit = self.get_value("TPA")
      
        # Indemnity Limit
        selector = '#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlIndemnity_0'        
        field_name = "TPA"
        await extract_dropdown_values(self.page, region, indemnity_Limit, applicable_Network, field_name, selector, self.portal_name)
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlIndemnity_0', value=indemnity_Limit)
        sukoon_logger.debug(f"Indemnity Limit Filled:::{indemnity_Limit}")
        await asyncio.sleep(4)

        # Geographical Area (Territory)
        geographical_Area = self.get_value("Territory") 
        selector = '#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlGeographicalArea_0'
        field_name = "Geographical Area"
        await extract_dropdown_values(self.page, region, indemnity_Limit, applicable_Network, field_name, selector, self.portal_name)
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlGeographicalArea_0', value=geographical_Area)
        sukoon_logger.debug(f"Geographical Area Filled:::{geographical_Area}")
        await asyncio.sleep(2)

        # Applicable Network
        applicable_Network = self.get_value("Network")
        selector = '#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlNetwork_0'
        # field_name = "Applicable Network"
        # await extract_dropdown_values(self.page, region, indemnity_Limit, applicable_Network, field_name, selector, self.portal_name)
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlNetwork_0', value=applicable_Network)
        sukoon_logger.debug(f"Applicable Network Filled:::{applicable_Network}")
        await asyncio.sleep(2)

        # Deductible
        deductable = self.get_value("Deductable")
        sukoon_logger.debug('Deductable (Before Apply):'+deductable)
        deductable = int(float(deductable))
        print(deductable)

        selector = '#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlDedcuctible_0'
        field_name = "Deductible"
        await extract_dropdown_values(self.page, region, indemnity_Limit, applicable_Network, field_name, selector, self.portal_name)
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlDedcuctible_0', value=str(deductable))
        sukoon_logger.debug(f"Deductible Filled:::{deductable}")
        await asyncio.sleep(2)

        # Co-Insurance
        insurance = self.get_value("Op Co Insurance")
        print(insurance)
        selector ='#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlCoinsurance_0'
        field_name = 'Co-Insurance'
        await extract_dropdown_values(self.page, region, indemnity_Limit, applicable_Network, field_name, selector, self.portal_name)
        await self.page.select_option('#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlCoinsurance_0', value=insurance)
        sukoon_logger.debug(f"Co-Insurance Filled:::{insurance}")
        await asyncio.sleep(2)

        # Dental Cover
        dental_Cover = self.get_value("Dental").capitalize()
        print(dental_Cover)
        selector = '//*[@id="ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlDentalCover_0"]'
        field_name = 'Dental Cover'
        await extract_dropdown_values(self.page, region, indemnity_Limit, applicable_Network, field_name, selector, self.portal_name)
        await self.page.locator('//*[@id="ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlDentalCover_0"]').select_option(value=dental_Cover)
        sukoon_logger.debug(f"Dental Cover Filled:::{dental_Cover}")
        await asyncio.sleep(2)

        # Optical Cover
        optical_Cover = self.get_value("Optical").capitalize()
        selector = "#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlOpticalCover_0"
        field_name = "Optical Cover"
        await extract_dropdown_values(self.page, region, indemnity_Limit, applicable_Network, field_name, selector, self.portal_name)
        await self.page.locator("#ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlOpticalCover_0").select_option(value=optical_Cover)
        sukoon_logger.debug(f"Optical Cover Filled:::{optical_Cover}")
        await asyncio.sleep(2)

        lab_xray_cover = self.get_value("Lab & X-Ray").capitalize()
        sukoon_logger.debug(f"Lab & X-Ray Filled:::{lab_xray_cover}")
        if lab_xray_cover != 'Nan' :
            selector = '//*[@id="ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlLabXRay_0"]'
            field_name = 'Lab & X-Ray'
            await extract_dropdown_values(self.page, region, indemnity_Limit, applicable_Network, field_name, selector, self.portal_name)
            await self.page.locator('//*[@id="ContentPlaceHolder1_rptCategory_rptCategoryList_1_UCCategory_0_ddlLabXRay_0"]').select_option(value=lab_xray_cover)
        await asyncio.sleep(2.5)