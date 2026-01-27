import asyncio
from src.utils.support_functions import extract_region, extract_tpa, extract_network
from src.utils.logger import qatar_logger

class Category2Page_p1:
    def __init__(self, page):
        self.page = page

    async def fill_category_2_p1(self, df1, catB, catA, portal_name):
        TPA_Value = str(catB['TPA'].iloc[0])
        region = str(df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])

        # Select option for 'Emirates'
        try:
            dropdown_selector = '//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[3]/select'
            field = 'Region'
            await extract_region(self.page, portal_name, field, dropdown_selector)
            await self.page.locator(dropdown_selector).select_option(
                label=str(df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]))
            await asyncio.sleep(3)
            qatar_logger.debug("Emirates Filled " + str(df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]))
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        # Select option for 'TPA'
        try:
            dropdown_selector = '//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[3]/select'
            field = 'TPA'
            await extract_tpa(self.page, portal_name, region, field, dropdown_selector)
            await self.page.locator(dropdown_selector).select_option(
                label=TPA_Value)
            await asyncio.sleep(3)
            qatar_logger.debug("TPA Filled " + TPA_Value)
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        # Select option for 'Plans' (catB)
        try:
            dropdown_selector = '//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select'
            field = 'Plan'
            await extract_network(self.page, portal_name, region, TPA_Value, field, dropdown_selector)
            await self.page.locator(dropdown_selector).select_option(
                label=str(catB['Network'].iloc[0]))
            await asyncio.sleep(3)
            qatar_logger.debug("Network Filled " + str(catB['Network'].iloc[0]))
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        # Select option for 'Plans' (catA)
        try:
            TPA_Value_A = str(catA['TPA'].iloc[0])
            dropdown_selector = '//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select'
            field = 'Plan'
            await extract_network(self.page, portal_name, region, TPA_Value_A, field, dropdown_selector)
            print(str(catA['Network'].iloc[0]))
            await self.page.locator(dropdown_selector).select_option(
                label=str(catA['Network'].iloc[0]))
            await asyncio.sleep(3)
            qatar_logger.debug("Network Filled " + str(catA['Network'].iloc[0]))
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")