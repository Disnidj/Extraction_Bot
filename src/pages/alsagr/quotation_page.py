import asyncio
import time
import os
# from src.utils.load_yaml import ALSAGR_QUOTATION_DIR
from src.utils.logger import alsagr_logger

class QuotationPage:
    def __init__(self, page):
        self.page = page

    async def download_quotation(self):
        # click Print button
        alsagr_logger.debug("Downloading quotation(Alsagr)")
        # await self.page.locator('//*[@id="tooltip-container2"]/div/button').click()
        # time.sleep(2)
        
        # # Tick the SME QUOTE checkbox
        # await self.page.get_by_label("SME QUOTE").check()
        # alsagr_logger.debug("SME QUOTE checkbox ticked")
        # time.sleep(2)

        # downloads = []

        # async with self.page.expect_download(timeout=120000) as download_info1:
        #     await self.page.get_by_role("button", name=" Generate Report").click()
        #     downloads.append(await download_info1.value)
        #     download_path_full = os.path.join(ALSAGR_QUOTATION_DIR, f"quotation_alsagr_1.pdf")
        #     await downloads[0].save_as(download_path_full)
        #     alsagr_logger.debug(f"Alsagr quotation 1 Download completed")

        # # Un Tick the SME QUOTE checkbox
        # await self.page.get_by_label("SME QUOTE").uncheck()
        # alsagr_logger.debug("SME QUOTE checkbox ticked")
        # time.sleep(2)

        # await self.page.locator("#customCheck1_1261").click()
        # alsagr_logger.debug("TOB checkbox ticked")
        # time.sleep(2)
        
        # async with self.page.expect_download(timeout=120000) as download_info2:
        #     await self.page.get_by_role("button", name=" Generate Report").click()
        #     downloads.append(await download_info2.value)
        #     download_path_full = os.path.join(ALSAGR_QUOTATION_DIR, f"quotation_alsagr_2.pdf")
        #     await downloads[1].save_as(download_path_full)
        #     alsagr_logger.debug(f"Alsagr quotation 2 Download completed")
        
        # # Ensure the download directory exists
        # if not os.path.exists(ALSAGR_QUOTATION_DIR):
        #     os.makedirs(ALSAGR_QUOTATION_DIR)
        
        # # try:
        # #     downloads = []
            
        # #     async with self.page.expect_download(timeout=120000) as download_info1:
        # #         await self.page.get_by_role("button", name=" Generate Report").click()
        # #         downloads.append(await download_info1.value)
        # #         download_path_full = os.path.join(ALSAGR_QUOTATION_DIR, f"quotation_alsagr_1.pdf")
        # #         await downloads[0].save_as(download_path_full)
        # #         alsagr_logger.debug(f"Alsagr quotation 1 Download completed")

                
        # #     async with self.page.expect_download(timeout=120000) as download_info2:
        # #         await self.page.get_by_role("button", name=" Generate Report").click()
        # #         downloads.append(await download_info2.value)
        # #         download_path_full = os.path.join(ALSAGR_QUOTATION_DIR, f"quotation_alsagr_2.pdf")
        # #         await downloads[1].save_as(download_path_full)
        # #         alsagr_logger.debug(f"Alsagr quotation 2 Download completed")

            
        #     # for index, download in enumerate(downloads, start=1):
        #     #     download_path_full = os.path.join(ALSAGR_QUOTATION_DIR, f"quotation_alsagr_{index}.pdf")
        #     #     await download.save_as(download_path_full)
        #     #     alsagr_logger.debug(f"Alsagr quotation {index} Download completed")
        
        # # except asyncio.TimeoutError:
        # #     print("Error: Timeout exceeded while waiting for the download.")
        # # except Exception as e:
        # #     print(f"Unexpected error during download: {e}")
        
        # time.sleep(10)