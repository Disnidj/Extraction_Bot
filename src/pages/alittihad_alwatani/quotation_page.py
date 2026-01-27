# src/pages/nlg/quotation_page.py
import asyncio
import asyncio
import os
# from src.utils.load_yaml import ALITTIHAD_ALWATANI_QUOTATION_DIR
from src.utils.logger import alittihad_logger

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
            alittihad_logger.debug("Next Button Clicked")
            await asyncio.sleep(5)

            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)
            alittihad_logger.debug("Page Loaded")

            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)

            # # Click Download Quote Button
            # # await self.page.locator('//*[@id="planDetailsAcc"]/div/div[2]/button').click()
            # await self.page.locator('//button[contains(text(), "Download Quote")]').click()
            # alittihad_logger.debug("Download Quote Button Clicked")
            # await asyncio.sleep(2)

            # await self.page.wait_for_load_state('networkidle')
            # await asyncio.sleep(5)

            # await self.page.locator("img.ms-1.mt-2[role='button']").click()
            # # await self.page.locator('/html/body/ngb-modal-window/div/div/div/div[2]/app-select-quote/div/div[2]/table/tbody/tr/div/div/img').click()
            # alittihad_logger.debug("Quote Sent Clicked")
            # await asyncio.sleep(10)

            # # # Ensure the download directory exists
            # # if not os.path.exists(ALITTIHAD_ALWATANI_QUOTATION_DIR):
            # #     os.makedirs(ALITTIHAD_ALWATANI_QUOTATION_DIR)

            # try:
            #     # Wait for the download to start
            #     async with self.page.expect_download(timeout=120000) as download_info:
                    
            #         # Click the download button
            #         await self.page.get_by_role("button", name="Download Pdf").click()
            #         alittihad_logger.debug("Download pdf Button Clicked")

            #         await asyncio.sleep(5)

            #         # Wait for the download to complete and save it to the specified path
            #         download = await download_info.value
            #         download_path_full = os.path.join(ALITTIHAD_ALWATANI_QUOTATION_DIR, "quotation_al_ittihad_al_watani.pdf")
            #         await download.save_as(download_path_full)
            #         alittihad_logger.info(f"Downloaded quotation PDF to: {download_path_full}")
            #         alittihad_logger.debug("AL_Ittihad_Alwatani quotation Download completed")

            # except asyncio.TimeoutError:
            #     alittihad_logger.error("Error: Timeout exceeded while waiting for the download.")

            # except Exception as e:
            #     alittihad_logger.error(f"Unexpected error during download: {e}")
                
            # # context = await browser.new_context(download_path="D:\\AlgoSpring\\python\\Alsagr")
            # await asyncio.sleep(5)       

            # alittihad_logger.debug("Quotation Pdf Downloaded")

            # await asyncio.sleep(5)
            # await self.page.wait_for_load_state('networkidle')
            # await asyncio.sleep(3)
            # await self.page.wait_for_load_state('networkidle')
            # await asyncio.sleep(2)


            # # Click Download TOB Button
            # await self.page.locator('//button[contains(text(), "Download TOB")]').click()
            # alittihad_logger.debug("Download TOB Button Clicked")
            # await asyncio.sleep(2)

            # await self.page.locator("img.ms-1.mt-2[role='button']").click()
            # alittihad_logger.debug("Quote Sent Clicked")
            # await asyncio.sleep(2)

            # # Ensure the download directory exists
            # if not os.path.exists(ALITTIHAD_ALWATANI_QUOTATION_DIR):
            #     os.makedirs(ALITTIHAD_ALWATANI_QUOTATION_DIR)
            # try:
            #     # Wait for the download to start
            #     async with self.page.expect_download(timeout=120000) as download_info:
            #         # Click the download button
            #         await self.page.get_by_role("button", name="Download Pdf").click()
            #         alittihad_logger.debug("Download pdf Button Clicked")
            #         # Wait for the download to complete and save it to the specified path
            #         download = await download_info.value
            #         download_path_full = os.path.join(ALITTIHAD_ALWATANI_QUOTATION_DIR, "tob_alittihad_alwatani.xlsx")
            #         await download.save_as(download_path_full)
            #         alittihad_logger.info(f"Downloaded quotation PDF to: {download_path_full}")
            #         alittihad_logger.debug("AlIttihad_Alwatani quotation Download completed")
                    
            # except asyncio.TimeoutError:
            #     alittihad_logger.error("Error: Timeout exceeded while waiting for the download.")
            # except Exception as e:
            #     alittihad_logger.error(f"Unexpected error during download: {e}")
            # await asyncio.sleep(5)


            # alittihad_logger.debug("TOB Pdf Downloaded")
            # await self.page.wait_for_load_state('networkidle')

        except Exception as e:
            alittihad_logger.error(f"Unexpected error during download: {e}")





