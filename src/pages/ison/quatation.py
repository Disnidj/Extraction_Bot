import asyncio
import os
import asyncio
# from src.utils.load_yaml import ISON_QUOTATION_DIR
from src.utils.logger import ison_logger


class DownloadPage:
    def __init__(self, page):
        self.page = page

    async def download_quotation(self):

        # # Click Get quote button
        # await self.page.locator('#ContentBoady1_btn_quote').click()
        # ison_logger.info("Get Quote button clicked")
        # await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        # # Click the download button
        # await self.page.locator('#ContentBoady1_btn_submit').click()

        # # Download the Quotation
        # try:
        #     # Wait for the download to start
        #     async with self.page.expect_download(timeout=120000) as download_info:
                

        #         # Wait for the download to complete and save it to the specified path
        #         download = await download_info.value
        #         download_path_full = os.path.join(ISON_QUOTATION_DIR, "quotation_ison.pdf")
        #         await download.save_as(download_path_full)
        #         print(f"Downloaded quotation PDF to: {download_path_full}")
        #         ison_logger.info(f"Downloaded quotation PDF to: {download_path_full}")

        # except asyncio.TimeoutError:
        #     print("Error: Timeout exceeded while waiting for the download.")
        #     ison_logger.error("Error: Timeout exceeded while waiting for the download.")
        # except Exception as e:
        #     print(f"Unexpected error during download: {e}")
        #     ison_logger.error(f"Unexpected error during download: {e}")

        # await asyncio.sleep(10) 