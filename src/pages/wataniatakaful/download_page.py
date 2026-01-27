# # src/pages/takaful/download_page.py

# import os
# import time
# import asyncio

# from src.utils.logger import logger

# class DownloadPage:
#     def __init__(self, page, download_dir):
#         self.page = page
#         self.download_dir = download_dir

#     async def download_pdf(self):



import os
import asyncio
import asyncio
# from src.utils.load_yaml import WATANIATAKAFUL_QUOTATION_DIR

from src.utils.logger import wataniatakaful_logger

class DownloadPage:
    def __init__(self, page):
        self.page = page

    async def download_pdf(self):
        # Click Next Button
        await self.page.locator('//*[@id="planDetailsAcc"]/div/div[2]/button').click()
        wataniatakaful_logger.debug("Next Button Clicked")
        await asyncio.sleep(5)

        await self.page.wait_for_load_state('networkidle')
        wataniatakaful_logger.debug("Page Loaded")


        # # Click Download Quote Button
        # await self.page.locator('//button[contains(text(), "Download Quote")]').click()
        # wataniatakaful_logger.debug("Download Quote Button Clicked")
        # await asyncio.sleep(2)

        # await self.page.locator("img.ms-1.mt-2[role='button']").click()
        # wataniatakaful_logger.debug("Quote Sent Clicked")
        # await asyncio.sleep(2)

        # # Ensure the download directory exists
        # if not os.path.exists(WATANIATAKAFUL_QUOTATION_DIR):
        #     os.makedirs(WATANIATAKAFUL_QUOTATION_DIR)
        # try:
        #     # Wait for the download to start
        #     async with self.page.expect_download(timeout=120000) as download_info:
        #         # Click the download button
        #         await self.page.get_by_role("button", name="Download Pdf").click()
        #         wataniatakaful_logger.debug("Download pdf Button Clicked")
        #         # Wait for the download to complete and save it to the specified path
        #         download = await download_info.value
        #         download_path_full = os.path.join(WATANIATAKAFUL_QUOTATION_DIR, "quotation_wataniatakaful.pdf")
        #         await download.save_as(download_path_full)
        #         print(f"Downloaded quotation PDF to: {download_path_full}")
        #         wataniatakaful_logger.debug("Wataniatakaful quotation Download completed")
        # except asyncio.TimeoutError:
        #     print("Error: Timeout exceeded while waiting for the download.")
        # except Exception as e:
        #     print(f"Unexpected error during download: {e}")
        # await asyncio.sleep(5)       

        # wataniatakaful_logger.debug("Quotation Pdf Downloaded")
        # await self.page.wait_for_load_state('networkidle')



        # # Click Download TOB Button
        # await self.page.locator('//button[contains(text(), "Download TOB")]').click()
        # wataniatakaful_logger.debug("Download TOB Button Clicked")
        # await asyncio.sleep(2)

        # await self.page.locator("img.ms-1.mt-2[role='button']").click()
        # wataniatakaful_logger.debug("Quote Sent Clicked")
        # await asyncio.sleep(2)

        # # Ensure the download directory exists
        # if not os.path.exists(WATANIATAKAFUL_QUOTATION_DIR):
        #     os.makedirs(WATANIATAKAFUL_QUOTATION_DIR)
        # try:
        #     # Wait for the download to start
        #     async with self.page.expect_download(timeout=120000) as download_info:
        #         # Click the download button
        #         await self.page.get_by_role("button", name="Download Pdf").click()
        #         wataniatakaful_logger.debug("Download pdf Button Clicked")
        #         # Wait for the download to complete and save it to the specified path
        #         download = await download_info.value
        #         download_path_full = os.path.join(WATANIATAKAFUL_QUOTATION_DIR, "tob_wataniatakaful.xlsx")
        #         await download.save_as(download_path_full)
        #         print(f"Downloaded quotation PDF to: {download_path_full}")
        #         wataniatakaful_logger.debug("Wataniatakaful quotation Download completed")
        # except asyncio.TimeoutError:
        #     print("Error: Timeout exceeded while waiting for the download.")
        # except Exception as e:
        #     print(f"Unexpected error during download: {e}")
        # await asyncio.sleep(5)


        # wataniatakaful_logger.debug("TOB Pdf Downloaded")
        # await self.page.wait_for_load_state('networkidle')
     