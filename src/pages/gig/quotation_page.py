# src/pages/nlg/quotation_page.py
import asyncio
import asyncio
import os
from src.utils.load_yaml import MED_SLEEP,GIG_GENERATED_CENSUS_DIR
from src.utils.logger import gig_logger
import zipfile
import shutil

# Page object for the quotation download page
# *** This is the standard quotation download page structure add all tasks after benifts mappings to download quotation in here ***
class QuotationPage:
    def __init__(self, page):
        self.page = page

    async def download_quotation(self):
        await self.page.wait_for_load_state('networkidle')

        #Click Next Button
        await self.page.locator('//*[@id="next"]').click()
        print('Next Button Clicked')
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Next Button Clicked")
        await self.page.wait_for_load_state('networkidle')

        gig_logger.debug("Category Page Completed")

        async def excel_open_close():
            import win32com.client
            import asyncio
            import os
            file_path_1 = os.path.join(GIG_GENERATED_CENSUS_DIR, "gig_map.xlsx")
            print("File path: ", file_path_1)

            # Check if the file exists before proceeding
            if not os.path.exists(file_path_1):
                print(f"Error: File not found - {file_path_1}")
                return

            try:
                # Launch Excel
                excel = win32com.client.Dispatch("Excel.Application")
                excel.Visible = True  # Make Excel visible
                print("Launched Excel")

                # Open the workbook
                try:
                    workbook = excel.Workbooks.Open(file_path_1)
                    print("Workbook opened")
                except Exception as e:
                    print(f"Error opening workbook: {e}")
                    excel.Quit()  # Ensure Excel closes if workbook fails to open
                    return

                # Get the active sheet
                worksheet = workbook.ActiveSheet
                print("Active sheet selected")

                # Select cell KK2 and set value
                b2_cell = worksheet.Range("KK2")
                b2_cell.Select()  # Move cursor to the cell
                b2_cell.Value = "New Value"
                print("Value set in KK2")

                # Wait for 3 seconds
                await asyncio.sleep(3)

                # Remove value from KK2
                b2_cell.Value = ""
                print("Cleared KK2 cell")

                # Save the workbook
                workbook.Save()
                print("Workbook saved")

            except Exception as e:
                print(f"Unexpected Error: {e}")

            finally:
                # Ensure Excel closes properly
                try:
                    workbook.Close(SaveChanges=True)
                    excel.Quit()
                    print("Excel closed successfully")
                except Exception as e:
                    print(f"Error closing Excel: {e}")

        # Call the function
        excel_open_close()
        


        #Upload Census
        file_upload_locator = self.page.locator('//*[@id="simulationForm"]/span/label')
        gig_logger.debug("Uploading census file.")
        try:
            await asyncio.sleep(2)
            await file_upload_locator.wait_for(state="visible", timeout=15000)
            await file_upload_locator.set_input_files(os.path.join(GIG_GENERATED_CENSUS_DIR, "gig_map.xlsx"))
            # await file_upload_locator.set_input_files(os.path.join(GIG_GENERATED_CENSUS_DIR, "GIG CensusData.xlsx"))
            gig_logger.debug("Census File uploaded successfully")
            print("Cencus File uploaded successfully")
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(10)

        except TimeoutError as e:
            print(f"Timeout Error: {e}")
            gig_logger.debug(f"Timeout Error: {e}")
        except Exception as e:
            print(f"Failed to upload file: {e}")
            gig_logger.debug(f"Failed to upload file: {e}")

        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(10)


        #Click Next Button
        # Click the next button
        await self.page.locator('//*[@id="next"]').click()
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Next Button Clicked")
        await self.page.wait_for_load_state('networkidle')

        await asyncio.sleep(10)
        # Wait for calculation to complete (replace 'loading_spinner_selector' with actual locator)
        await self.page.wait_for_selector('img[src="/static/images/loader.gif"]', state="hidden")
        gig_logger.debug("Loading completed")
        await asyncio.sleep(MED_SLEEP)


        # # Click the Proposal button and wait for the popup window
        # async with self.page.expect_popup() as popup_info:
        #     await self.page.locator('//*[@id="next"]').click()  # Click Proposal button
        #     gig_logger.debug("Proposal Button Clicked")
        #     await asyncio.sleep(MED_SLEEP)

        # # Get the popup window reference
        # popup = await popup_info.value
        # gig_logger.debug("Popup window detected")

        # # Ensure the popup is fully loaded
        # await popup.wait_for_load_state('domcontentloaded')
        # gig_logger.debug("Popup DOM content loaded")

        # # Optional: Ensure the popup is focused before interacting
        # await popup.bring_to_front()
        # gig_logger.debug("Popup window brought to front")

        # # Wait for the dropdown to appear inside the popup
        # await popup.wait_for_selector('#template_select_13413408-2c70-4274-a598-3f83d60d4ac6', state="visible", timeout=5000)
        # gig_logger.debug("Dropdown found in popup")

        # # Select the 'Commercial Proposal Health GIG UAE' option by text
        # await popup.locator('#template_select_13413408-2c70-4274-a598-3f83d60d4ac6').select_option(label="Commercial Proposal Health GIG_UAE")
        # gig_logger.debug("Dropdown option selected: Commercial Proposal Health GIG UAE")
        # await asyncio.sleep(3)

        # # Wait for the Download button inside the popup
        # await popup.wait_for_selector('//*[@id="next"]', state="visible", timeout=5000)
        # gig_logger.debug("Download button found in popup")



        # # Expect a download when clicking the Download button inside the popup
        # async with popup.expect_download() as download_info:
        #     await popup.locator('//*[@id="next"]').click()
        #     gig_logger.debug("Download button clicked")

        # # Wait for the download to complete
        # download = await download_info.value
        # gig_logger.debug(f"Download started: {download.url}")

        # # Wait for the file path to be available
        # file_path = await download.path()
        # while file_path is None:
        #     file_path = await download.path()

        # # Save the fully downloaded file
        # if file_path:
        #     save_path = os.path.join(GIG_QUOTATION_DIR, "quotation_gig.zip")
        #     await download.save_as(save_path)
        #     gig_logger.debug(f"Zip file Download completed and saved at: {save_path}")
        # else:
        #     gig_logger.error("Download failed: No file path available")

        # # Define paths
        # zip_path = os.path.join(GIG_QUOTATION_DIR, "quotation_gig.zip")  # ZIP file path
        # extract_folder = os.path.join(GIG_QUOTATION_DIR, "extracted_quotation")  # Temporary extraction folder
        # final_pdf_path = os.path.join(GIG_QUOTATION_DIR, "quotation_gig.pdf")  # Final PDF save path

        # # Ensure extraction folder exists
        # os.makedirs(extract_folder, exist_ok=True)

        # # Extract ZIP file
        # with zipfile.ZipFile(zip_path, "r") as zip_ref:
        #     zip_ref.extractall(extract_folder)
        #     gig_logger.debug(f"ZIP extracted to: {extract_folder}")

        # # Search for PDF inside extracted folder
        # pdf_found = False
        # for root, _, files in os.walk(extract_folder):
        #     for file in files:
        #         if file.lower().endswith(".pdf"):
        #             pdf_path = os.path.join(root, file)  # Get the full path of the PDF
        #             shutil.move(pdf_path, final_pdf_path)  # Move the PDF to the final location
        #             pdf_found = True
        #             gig_logger.debug(f"PDF extracted and saved at: {final_pdf_path}")
        #             break  # Stop after moving the first found PDF

        # if not pdf_found:
        #     gig_logger.error("No PDF file found inside the extracted ZIP!")

        # # Cleanup: Remove extracted folder
        # shutil.rmtree(extract_folder)
        # gig_logger.debug("Extracted folder removed")

        