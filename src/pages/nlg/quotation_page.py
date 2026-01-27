# src/pages/nlg/quotation_page.py
import asyncio
import os
# from src.utils.load_yaml import NLG_QUOTATION_DIR
from src.utils.logger import nlg_logger

class QuotationPage:
    def __init__(self, page):
        self.page = page

    async def download_quotation(self):
        # Wait for the page to load completely
        await self.page.wait_for_load_state('networkidle')
        nlg_logger.debug("Quotation page loaded")

        is_visible = await self.page.is_visible('text=DOWNLOAD TOB PDF (DXB / NE)', timeout=5000)
        if not is_visible:
            return False

        # Expect a download
        try:
            async with self.page.expect_download() as download_info:
                # Click the button to trigger the download
                await self.page.click('text=DOWNLOAD TOB PDF (DXB / NE)')
                download = await download_info.value
                nlg_logger.debug("NLG quotation Download started")
                return True
        except Exception as e:
            nlg_logger.error(f"Download failed: {e}")
            return False

        await asyncio.sleep(3)

