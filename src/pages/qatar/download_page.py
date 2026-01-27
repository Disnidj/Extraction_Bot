# src/pages/takaful/download_page.py

import os
import asyncio
import asyncio

from src.utils.logger import qatar_logger

class DownloadPage:
    def __init__(self, page, download_dir):
        self.page = page
        self.download_dir = download_dir

    async def download_pdf(self):
        await self.page.get_by_label("Choose Plans").get_by_role("button", name="Next").click()
        await asyncio.sleep(1.2)
        
        qatar_logger.debug("Choose Plans Button Clicked")

        await asyncio.sleep(5)

        await self.page.wait_for_load_state('networkidle')
        await self.page.locator('//button[text()="Download Quote"]').click()
        await asyncio.sleep(3)
        
        qatar_logger.debug("Download PDF Button Clicked")
        
        await self.page.wait_for_load_state('load')
        await asyncio.sleep(1.2)

        # Attempt to select the button in the row named "Binding No"
        try:
            await self.page.get_by_role("row", name="Binding No").get_by_role("button").click()
            qatar_logger.debug("Clicked button in the row with 'Binding No'")

        except Exception as e:
            qatar_logger.debug("Row with 'Binding No' not found, trying row with '1'")

            # Attempt to select the button in the row named "1"
            try:
                await self.page.get_by_role("row", name="1").get_by_role("button").click()
                qatar_logger.debug("Clicked button in the row with '1'")

            except Exception as e:
                qatar_logger.debug("Neither 'Binding No' nor '1' rows found, proceeding without click.")

        await asyncio.sleep(2)

        
        qatar_logger.debug("Binding No Radio Button Clicked")

        await self.page.wait_for_load_state('networkidle')
        await self.page.wait_for_selector("button:has-text('Download')", state='visible')
        
        qatar_logger.debug("Download Button Clicked")

        try:
            # Handle the download action
            async with self.page.expect_download(timeout=60000) as download_info:
                print("Downloading PDF")  # Debug: Ensure this line prints
                # Wait for the button to be visible
                await self.page.locator("button.cancel-buttons-popup.medium.px-3:has-text('Download')").wait_for()
                print("Button located, attempting to click.")  # Debug: Ensure button is found
                
                # Click the download button
                await self.page.locator("button.cancel-buttons-popup.medium.px-3:has-text('Download')").click()
                print("Button clicked, waiting for download to start.")  # Debug: Ensure the click is executed

                # Add a delay for download initialization
                await asyncio.sleep(10)

            # Retrieve the download object
            download = await download_info.value
            await asyncio.sleep(5)  # Allow time for the file to be fully downloaded

            # Save the file if the download object exists
            if download:
                file_path = os.path.join(self.download_dir, "quotation_qatar.pdf")
                await download.save_as(file_path)
                print(f"File saved as {file_path}")
            else:
                print("Download object not found.")  # Debug: Check if download event failed

        except Exception as e:
            print(f"An error occurred: {e}")


#   page.get_by_role("button", name="Download PDF").click()
#     page.get_by_role("row", name="1 13762 294,436.94 Indicative").get_by_role("button").click()
#     page.get_by_role("button", name="Download").click()