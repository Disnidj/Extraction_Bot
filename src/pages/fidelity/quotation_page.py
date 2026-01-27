# src/pages/nlg/quotation_page.py
import asyncio
import asyncio
import os
# from src.utils.load_yaml import FIDELITY_QUOTATION_DIR
from src.utils.logger import fidelity_logger

# Page object for the quotation download page
# *** This is the standard quotation download page structure add all tasks after benifts mappings to download quotation in here ***
class QuotationPage:
    def __init__(self, page):
        self.page = page

    async def download_quotation(self):

        # Click Next Button
        await self.page.locator('//*[@id="planDetailsAcc"]/div/div[2]/button').click()
        # await self.page.query_selector(".next-button").click()
        fidelity_logger.debug("Next Button Clicked")
        await asyncio.sleep(5)

        await self.page.wait_for_load_state('networkidle')
        fidelity_logger.debug("Page Loaded")


        # Click Download Quote Button
        # await self.page.locator('//*[@id="planDetailsAcc"]/div/div[2]/button').click()
        # await self.page.locator('//button[contains(text(), "Download Quote")]').click()
        # fidelity_logger.debug("Download Quote Button Clicked")
        # await asyncio.sleep(2)

        # await self.page.locator("img.ms-1.mt-2[role='button']").click()
        # # await self.page.locator('/html/body/ngb-modal-window/div/div/div/div[2]/app-select-quote/div/div[2]/table/tbody/tr/div/div/img').click()
        # fidelity_logger.debug("Quote Sent Clicked")
        # await asyncio.sleep(2)

        # # Ensure the download directory exists
        # if not os.path.exists(FIDELITY_QUOTATION_DIR):
        #     os.makedirs(FIDELITY_QUOTATION_DIR)
        # try:
        #     # Wait for the download to start
        #     async with self.page.expect_download(timeout=120000) as download_info:
        #         # Click the download button
        #         await self.page.get_by_role("button", name="Download Pdf").click()
        #         fidelity_logger.debug("Download pdf Button Clicked")
        #         # Wait for the download to complete and save it to the specified path
        #         download = await download_info.value
        #         download_path_full = os.path.join(FIDELITY_QUOTATION_DIR, "quotation_fidelity.pdf")
        #         await download.save_as(download_path_full)
        #         print(f"Downloaded quotation PDF to: {download_path_full}")
        #         fidelity_logger.debug("Fidelity quotation Download completed")
        # except asyncio.TimeoutError:
        #     print("Error: Timeout exceeded while waiting for the download.")
        # except Exception as e:
        #     print(f"Unexpected error during download: {e}")
        # # context = await browser.new_context(download_path="D:\\AlgoSpring\\python\\Alsagr")
        # await asyncio.sleep(5)       

        # fidelity_logger.debug("Quotation Pdf Downloaded")
        # await self.page.wait_for_load_state('networkidle')



        # # Click Download TOB Button
        # await self.page.locator('//button[contains(text(), "Download TOB")]').click()
        # fidelity_logger.debug("Download TOB Button Clicked")
        # await asyncio.sleep(2)

        # await self.page.locator("img.ms-1.mt-2[role='button']").click()
        # fidelity_logger.debug("Quote Sent Clicked")
        # await asyncio.sleep(2)

        # # Ensure the download directory exists
        # if not os.path.exists(FIDELITY_QUOTATION_DIR):
        #     os.makedirs(FIDELITY_QUOTATION_DIR)
        # try:
        #     # Wait for the download to start
        #     async with self.page.expect_download(timeout=120000) as download_info:
        #         # Click the download button
        #         await self.page.get_by_role("button", name="Download Pdf").click()
        #         fidelity_logger.debug("Download pdf Button Clicked")
        #         # Wait for the download to complete and save it to the specified path
        #         download = await download_info.value
        #         download_path_full = os.path.join(FIDELITY_QUOTATION_DIR, "tob_fidelity.xlsx")
        #         await download.save_as(download_path_full)
        #         print(f"Downloaded quotation PDF to: {download_path_full}")
        #         fidelity_logger.debug("Fidelity quotation Download completed")
        # except asyncio.TimeoutError:
        #     print("Error: Timeout exceeded while waiting for the download.")
        # except Exception as e:
        #     print(f"Unexpected error during download: {e}")
        # await asyncio.sleep(5)


        # fidelity_logger.debug("TOB Pdf Downloaded")
        # await self.page.wait_for_load_state('networkidle')
        



