import asyncio
from src.utils.support_functions import convert_to_int
from src.utils.logger import qatar_logger

class Category3Page_p1:
    def __init__(self, page):
        self.page = page

    async def fill_category_3_p1(self, df1, catC , catA , catB):
        TPA_Value = str(catC['TPA'].iloc[0])

        # Select option for 'Emirates'
        try:
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[4]/select').select_option(
                label=str(df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]))
            await asyncio.sleep(3)
            qatar_logger.debug("Emirates Filled")
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        # Select option for 'TPA'
        try:
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[4]/select').select_option(
                label=TPA_Value)
            await asyncio.sleep(3)
            qatar_logger.debug("TPA Filled")
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        # Select option for 'Plans'
        try:
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[4]/select').select_option(
                label=str(catC['Network'].iloc[0]))
            await asyncio.sleep(3)
            qatar_logger.debug("Network Filled")
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        
        # Select option for 'Plans'
        try:
            print(str(catA['Network'].iloc[0]))
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select').select_option(
                label=str(catA['Network'].iloc[0]))
            await asyncio.sleep(3)
        
            qatar_logger.debug("Network Filled " + str(catA['Network'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        # Select option for 'Plans'
        try:
            await self.page.locator('//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[3]/select').select_option(
                label=str(catB['Network'].iloc[0]))
            await asyncio.sleep(3)
            qatar_logger.debug("Network Filled " + str(catB['Network'].iloc[0]))
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")