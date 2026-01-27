# src/pages/nlg/quotation_page.py
import asyncio
import asyncio
import os
# from src.utils.load_yaml import MEDGULF_QUOTATION_DIR
from src.utils.logger import medgulf_logger

# Page object for the quotation download page
# *** This is the standard quotation download page structure add all tasks after benifts mappings to download quotation in here ***
class QuotationPage:
    def __init__(self, page):
        self.page = page

    async def download_quotation(self):
        try: 
            # Click Next Button
            await self.page.locator('//*[@id="planDetailsAcc"]/div/div[2]/button').click()
            # await self.page.query_selector(".next-button").click()
            medgulf_logger.debug("Next Button Clicked")
            await asyncio.sleep(5)

            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)
            medgulf_logger.debug("Page Loaded")

            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)

        #     # Click Download Quote Button
        #     # await self.page.locator('//*[@id="planDetailsAcc"]/div/div[2]/button').click()
        #     await self.page.locator('//button[contains(text(), "Download Quote")]').click()
        #     medgulf_logger.debug("Download Quote Button Clicked")
        #     await asyncio.sleep(2)

        #     await self.page.wait_for_load_state('networkidle')
        #     await asyncio.sleep(5)

        #     await self.page.locator("img.ms-1.mt-2[role='button']").click()
        #     # await self.page.locator('/html/body/ngb-modal-window/div/div/div/div[2]/app-select-quote/div/div[2]/table/tbody/tr/div/div/img').click()
        #     medgulf_logger.debug("Quote Sent Clicked")
        #     await asyncio.sleep(5)

        #     # # Ensure the download directory exists
        #     # if not os.path.exists(MEDGULF_QUOTATION_DIR):
        #     #     os.makedirs(MEDGULF_QUOTATION_DIR)

        #     try:
        #         # Wait for the download to start
        #         async with self.page.expect_download(timeout=120000) as download_info:
                    
        #             # Click the download button
        #             await self.page.get_by_role("button", name="Download Pdf").click()
        #             medgulf_logger.debug("Download pdf Button Clicked")

        #             await asyncio.sleep(5)

        #             # Wait for the download to complete and save it to the specified path
        #             download = await download_info.value
        #             download_path_full = os.path.join(MEDGULF_QUOTATION_DIR, "quotation_medgulf.pdf")
        #             await download.save_as(download_path_full)
        #             medgulf_logger.info(f"Downloaded quotation PDF to: {download_path_full}")
        #             medgulf_logger.debug("Medgulf quotation Download completed")

        #     except asyncio.TimeoutError:
        #         medgulf_logger.info("Error: Timeout exceeded while waiting for the download.")

        #     except Exception as e:
        #         medgulf_logger.info(f"Unexpected error during download: {e}")
                
        #     # context = await browser.new_context(download_path="D:\\AlgoSpring\\python\\Alsagr")
    

        #     medgulf_logger.debug("Quotation Pdf Downloaded")

        #     await self.page.wait_for_load_state('networkidle')
        #     await asyncio.sleep(3)



        #     # Click Download TOB Button
        #     await self.page.locator('//button[contains(text(), "Download TOB")]').click()
        #     medgulf_logger.debug("Download TOB Button Clicked")
        #     await asyncio.sleep(2)

        #     await self.page.locator("img.ms-1.mt-2[role='button']").click()
        #     medgulf_logger.debug("Quote Sent Clicked")
        #     await asyncio.sleep(2)

        #     # Ensure the download directory exists
        #     if not os.path.exists(MEDGULF_QUOTATION_DIR):
        #         os.makedirs(MEDGULF_QUOTATION_DIR)
        #     try:
        #         # Wait for the download to start
        #         async with self.page.expect_download(timeout=120000) as download_info:
        #             # Click the download button
        #             await self.page.get_by_role("button", name="Download Pdf").click()
        #             medgulf_logger.debug("Download pdf Button Clicked")
        #             # Wait for the download to complete and save it to the specified path
        #             download = await download_info.value
        #             download_path_full = os.path.join(MEDGULF_QUOTATION_DIR, "tob_medgulf.xlsx")
        #             await download.save_as(download_path_full)
        #             medgulf_logger.info(f"Downloaded quotation PDF to: {download_path_full}")
        #             medgulf_logger.debug(" quotation Download completed")
                    
        #     except asyncio.TimeoutError:
        #         medgulf_logger.info("Error: Timeout exceeded while waiting for the download.")
        #     except Exception as e:
        #         medgulf_logger.info(f"Unexpected error during download: {e}")
        #     await asyncio.sleep(5)


        #     medgulf_logger.debug("TOB Pdf Downloaded")
        #     await self.page.wait_for_load_state('networkidle')

        except Exception as e:
            medgulf_logger.info(f"Unexpected error during download: {e}")



