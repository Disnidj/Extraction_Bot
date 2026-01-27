import asyncio
import os
import requests
# from src.utils.load_yaml import DAMAN_QUOTATION_DIR
from src.utils.logger import daman_logger

class DownloadPage:
    
    def __init__(self, page):
        self.page = page
        daman_logger.debug("Initialized DownloadPage class")

    async def get_reference_number_from_session_storage(self):
        daman_logger.debug("Retrieving reference number from session storage")
        try:
            reference_number = await self.page.evaluate("sessionStorage.getItem('quotation_ref');")
            if reference_number:
                daman_logger.info(f"Using Stored Reference Number: {reference_number}")
                return reference_number.strip()
            else:
                daman_logger.warning("No reference number found in session storage.")
                return None
        except Exception as e:
            daman_logger.error(f"Error retrieving reference number from session storage: {e}")
            return None

    async def check_status(self):
        await asyncio.sleep(4)
        await self.page.reload()

        daman_logger.info("Checking quotation status...")

        select_download_quotations = await self.page.wait_for_selector('//div[contains(text(), "Quotations")]')
        await select_download_quotations.click()
        await asyncio.sleep(0.5)

        select_sme_element = await self.page.wait_for_selector('//a[contains(text(), "SME")]', timeout=10000)
        await select_sme_element.click()
        await asyncio.sleep(0.5)

        reference_number = await self.get_reference_number_from_session_storage()
        if not reference_number:
            daman_logger.warning("No reference number found in session storage.")
            return None

        select_reference_element = await self.page.wait_for_selector('//input[@id="smeQuoteReferenceNumber"]', timeout=10000)
        await select_reference_element.fill(reference_number)
        await asyncio.sleep(0.5)
        await self.page.wait_for_timeout(3000)

        select_apply_element = await self.page.wait_for_selector('//input[@id="sme_quotation_search"]')
        await select_apply_element.click()
        await asyncio.sleep(0.5)

        status_element = await self.page.query_selector('//*[@id="smeQuotationResults"]/tbody/tr/td[10]/span')
        if status_element:
            status_text = await status_element.inner_text()
            daman_logger.info(f"Current Status: {status_text.strip()}")

            if status_text in ["Pending", "In Processing"]:
                daman_logger.info(f"Status is '{status_text}'. Proceeding with document download.")
                return reference_number
            else:
                daman_logger.info(f"Status is '{status_text}'. Refreshing and checking again...")
                return await self.check_status()
        else:
            daman_logger.warning("No status found.")
            return await self.check_status()

    async def download(self):
        reference_number = await self.check_status()
        if not reference_number:
            daman_logger.error("Aborting download due to missing reference number or status.")
            return await self.check_status()
        
        select_doc_view_element = await self.page.wait_for_selector('//a[@title="View"]')
        await select_doc_view_element.click()

        await asyncio.sleep(10)

        # try:
        #     iframe = self.page.frame("docFrame")
        #     download_selectors = ['a.pdf-download']

        #     for selector in download_selectors:
        #         try:
        #             download_button = iframe.locator(selector).first
        #             if await download_button.is_visible():
        #                 daman_logger.info(f"Found download button with selector: {selector}")
        #                 async with self.page.expect_download() as download_info:
        #                     await download_button.click()
        #                     download = await download_info.value
        #                 await download.save_as(f"{DAMAN_QUOTATION_DIR}\\quotation_daman.pdf")
        #                 daman_logger.info(f"Download completed: {DAMAN_QUOTATION_DIR}\\quotation_daman.pdf")
        #                 return
        #         except Exception as e:
        #             daman_logger.warning(f"Attempt with selector {selector} failed: {e}")
        #             continue

        #     pdf_url = await self.page.evaluate('''() => {
        #         const iframe = document.getElementById('docFrame');
        #         return iframe ? iframe.src : null;
        #     }''')

        #     if pdf_url:
        #         daman_logger.info(f"Found PDF URL: {pdf_url}")
        #         await asyncio.to_thread(self.download_pdf, pdf_url, f"quotation_daman.pdf")

        # except Exception as e:
        #     daman_logger.error(f"Error during download attempt: {str(e)}")
        #     raise e

    # def download_pdf(self, pdf_url, output_filename):
    #     daman_logger.debug("Downloading PDF from URL...")
    #     response = requests.get(pdf_url)
    #     if response.status_code == 200:
    #         with open(f"{DAMAN_QUOTATION_DIR}\\{output_filename}", 'wb') as file:
    #             file.write(response.content)
    #         daman_logger.info(f"PDF downloaded successfully: {DAMAN_QUOTATION_DIR}\\{output_filename}")
    #         return True
    #     else:
    #         daman_logger.error(f"Failed to download PDF. Status code: {response.status_code}")

