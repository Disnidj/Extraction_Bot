import asyncio
import asyncio
import os
from src.utils.logger import takaful_logger

class DownloadPage:
    def __init__(self, page):
        self.page = page

    async def download_pdf(self):

        # Tick the SME QUOTE checkbox
        await self.page.get_by_label("Choose Plans").get_by_role("button", name="Next").click()
        takaful_logger.debug("Next Button Clicked")
        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(10)

        # await self.page.wait_for_load_state('networkidle')
        # await self.page.locator("//html/body/app-root/div/app-quotes-flow/div/div/div[2]/div/div[3]/div[2]/span/button[2]").click()
        # takaful_logger.debug("Download PDF Button Clicked")
        # await asyncio.sleep(5)
        # await self.page.locator("//html/body/ngb-modal-window/div/div/div/div[2]/app-select-quote/div/div[2]/table/tbody/tr/div/div/img").click()
        # print("Tick the Quote Generate.") 
        # await asyncio.sleep(5)
        
        # if not os.path.exists(TAKAFUL_QUOTATION_DIR):
        #     os.makedirs(TAKAFUL_QUOTATION_DIR)

        # download = None
        # for _ in range(5):  # Try multiple times
        #     try:
        #         async with self.page.expect_download(timeout=60000) as download_info:
        #             await self.page.locator("//html/body/ngb-modal-window/div/div/div/div[2]/app-select-quote/div/div[3]/button[2]").click()
        #             download = await download_info.value
        #             break  # Exit loop if download starts
        #     except asyncio.TimeoutError:
        #         print("Retrying download...")

        # if not download:
        #     print("Failed to start the download after multiple attempts.")
        # else:
        #     download_path_full = os.path.join(TAKAFUL_QUOTATION_DIR, "quotation_takaful.pdf")
        #     await download.save_as(download_path_full)
        #     print(f"Downloaded quotation PDF to: {download_path_full}")
        #     takaful_logger.debug("Takaful quotation Download completed")


        # await asyncio.sleep(10)
