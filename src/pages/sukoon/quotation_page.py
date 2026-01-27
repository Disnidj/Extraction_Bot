# src/pages/nlg/quotation_page.py
import asyncio
import os
# from src.utils.load_yaml import SUKOON_QUOTATION_DIR
from src.utils.logger import sukoon_logger


class QuotationPage:
    def __init__(self, page):
        self.page = page

    async def download_quotation(self):

        # Wait for the page to load completely
        await self.page.wait_for_load_state('networkidle')

        # await self.page.get_by_role("button", name="SAVE AND UPDATE TOTAL").click()
        # await self.page.locator('//*[@id="ContentPlaceHolder1_btnQuote"]').click()
        # await self.page.locator('//*[@id="ContentPlaceHolder1_btnIssueQuote"]').click()
       
        # # Expect a download
        # async with self.page.expect_download() as download_info:
        #     # Click the button to trigger the download
        #     await self.page.locator('//*[@id="ContentPlaceHolder1_btnPrintQuoteUp"]').click()
        #     download = await download_info.value
        #     sukoon_logger.debug("SUKOON quotation Download started")

        # # Save the file to a local path
        # if download:
        #     await download.save_as(os.path.join(SUKOON_QUOTATION_DIR, "quotation_sukoon.pdf"))
        #     sukoon_logger.debug("SUKOON quotation Download completed")

        # await asyncio.sleep(3)