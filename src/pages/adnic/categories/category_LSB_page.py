import asyncio
from datetime import datetime
from src.utils.load_yaml import MED_SLEEP, MAX_SLEEP
from src.utils.logger import adnic_logger

# class for the Category 1 benefits mapping
class CategoryLSBPage:
    def __init__(self, page):
        self.page = page

    async def fill_category_LSB(self):
        # Add a delay before starting
        await asyncio.sleep(MAX_SLEEP)
        adnic_logger.info("Category LSB started")

        #Plan Type
        await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_productebp"]').select_option("Basic EBP Plan")
        adnic_logger.debug("Plan Type : Basic EBP Plan")
        await asyncio.sleep(MED_SLEEP)

        #Network Provider
        await self.page.locator('//*[@id="ContentPlaceHolder1_ddl_tpaebp"]').select_option("Ecare")
        adnic_logger.debug("Network Provider : Ecare")
        await asyncio.sleep(MED_SLEEP)

        adnic_logger.info("Category LSB completed")