import asyncio
import os
# from src.utils.load_yaml import ORIENT_QUOTATION_DIR
from src.services.referral_service.referrals_store import save_for_referral
from src.services.db_service.update import update_iq_quotation_status
from src.services.excel_service.read_excel import get_app_key
from src.utils.enums import Final_Status,Orient_Status
from src.utils.logger import orient_logger
from src.utils.support_functions import screenshot_and_compare


class DownloadPage:
    def __init__(self, page):
        self.page = page

    async def download_quotation(self, quotation_no ,unique_categories_list,df2):

        category_a_available = category_b_available = category_c_available = False

        if unique_categories_list:
            category_a_available = True
            if len(unique_categories_list) > 1:
                category_b_available = True
            if len(unique_categories_list) > 2:
                category_c_available = True

        try:
            await self.page.get_by_role("button", name="Proceed").click()
        except Exception as e:
            orient_logger.error(f"Proceed button click failed: {e}")
            await asyncio.sleep(30)
            return False

        await asyncio.sleep(30)
        return False

        await self.page.get_by_role("button", name="Proceed to Submission ").hover()
        # await asyncio.sleep(10)
        # await screenshot_and_compare(self.page, "orient", "ORIENT_3")

        await self.page.get_by_role("button", name="Proceed to Submission ").click()
        await asyncio.sleep(1)
        
        orient_logger.debug("Proceed to Submission Button Clicked")
        
#         # List to hold available categories and their corresponding locators
#         available_categories = []

#         if category_a_available:
#             available_categories.append(('A', '//*[@id="collapse_1"]/div/div/div/table/tbody/tr[1]/td[2]/dx-number-box/div/div[1]/input'))
#             # catA = df2[df2['Category'] == unique_categories_list[0]]
#         if category_b_available:
#             available_categories.append(('B', '//*[@id="collapse_1"]/div/div/div/table/tbody/tr[2]/td[2]/dx-number-box/div/div[1]/input'))
#             # catB = df2[df2['Category'] == unique_categories_list[1]]
#         if category_c_available:
#             available_categories.append(('C', '//*[@id="collapse_1"]/div/div/div/table/tbody/tr[3]/td[2]/dx-number-box/div/div[1]/input'))
#             # catC = df2[df2['Category'] == unique_categories_list[2]]

#         # Define category labels
#         category_labels = ['A', 'B', 'C']

#         # Dynamically store available category DataFrames in a dictionary
#         category_dataframes = {
#             category_labels[i]: df2[df2['Category'] == unique_categories_list[i]]
#             for i in range(len(unique_categories_list))
# }

#         # Iterate over the available categories and fill the respective fields
#         for index, (category, locator) in enumerate(available_categories):
#             await self.page.locator(locator).click()
#             await asyncio.sleep(1)
            
#             # Fill the value, assuming it's 10.00% for every category
#             selected_category_df = category_dataframes[category]
#             # Extract the broker commission value
#             broker_commision = selected_category_df['Broker Commission'].iloc[0]
#             broker_commision = broker_commision.replace("%", ".00%")
#             await self.page.locator(locator).fill(broker_commision)
#             await asyncio.sleep(1)
            
#             orient_logger.debug(f"Category {category} filled with {broker_commision}")
        
        
#         await self.page.get_by_role("button", name=" Calculate").click()
#         await asyncio.sleep(1)
        
#         orient_logger.debug("Calculate Button Clicked")
        
#         # await self.page.get_by_role("button", name="Submit ").click()
#         await self.page.get_by_role("button", name="Submit", exact=True).click()
#         await asyncio.sleep(1)
        
#         orient_logger.debug("Submit Button Clicked")
        
#         await self.page.get_by_label("Yes").click()
#         await asyncio.sleep(1)
        
#         orient_logger.debug("Yes Button Clicked")
#         # await self.page.locator('//div[@class="dx-button-content"]/span[text()="Yes"]').click()
        
#         await self.page.get_by_role("button", name="OK").click()
#         await asyncio.sleep(1)
        
#         orient_logger.debug("OK Button Clicked")
        
        # --------------------- download quotation sheet --------------------- #

        # # Wait for the page to load completely
        # await self.page.wait_for_load_state('networkidle')
        # # await asyncio.sleep(10)
        # # await self.page.reload()
        # # # Optionally, wait for the page to load again after refresh (if necessary)
        # # await self.page.wait_for_load_state('networkidle')
        # await asyncio.sleep(5)

        # orient_logger.debug('Quotation No: '+quotation_no)

        # quo_status = await self.page.get_by_role("row", name=quotation_no).locator('[aria-colindex="8"]').text_content()
        
        
        # # send to refferal if needed
        # if quo_status.startswith("Under Review"):
        #     await self.page.wait_for_selector('.dx-datagrid-table.dx-datagrid-table-fixed')
        #     print(f"Quotation No: {quotation_no} send to refferal")
        #     orient_logger.info(f"Quotation No: {quotation_no} send to refferal")
        #     update_iq_quotation_status(get_app_key(), quotation_no, Orient_Status.REFERRAL.value , Final_Status.PENDING.value)
        #     save_for_referral(quotation_no)
        #     return "referral"
        
        # else:
        #     if quo_status.startswith("PROCESSING"):
        #         # EVERY 10 SECONDS CHECK THE STATUS OF THE QUOTATION UNTILL IT IS APPROVED
        #         while True:
        #             print("sleeping for 10 seconds until the quotation is approved")
        #             await asyncio.sleep(10)

        #             await self.page.reload()
        #             await self.page.wait_for_load_state('networkidle')
        #             orient_logger.debug("Page Reloaded for Quotation Status Check")
        #             await asyncio.sleep(1)

        #             new_quo_status = await self.page.get_by_role("row", name=quotation_no).locator('[aria-colindex="8"]').text_content()
        #             if new_quo_status.startswith("APPROVED"):
        #                 break
        #             elif new_quo_status.startswith("REJECTED"):
        #                 orient_logger.error(f"Quotation No: {quotation_no} is REJECTED By ORIENT please check data...")
        #                 raise Exception(f"Quotation No: {quotation_no} is REJECTED By ORIENT please check data...")
                    
        #     # Perform tasks using the dynamic Quotation No
        #     await self.page.get_by_role("gridcell", name=quotation_no).click()
        #     await asyncio.sleep(1)

        #     orient_logger.debug("Quotation No Clicked")
        
        #     # Perform the action on the row with the saved Quotation No
        #     await self.page.get_by_role("row", name=f"{quotation_no} 1").get_by_label("Action").click()
        #     await asyncio.sleep(1)

        #     orient_logger.debug("Action Button Clicked")

        #     async with self.page.expect_download() as download_info:
        #         await self.page.get_by_text("Download Quotation").click()
        #         download = await download_info.value

        #         orient_logger.debug("Download Quotation Button Clicked")

        #     # Save the file to a local path
        #     if download:
        #         # Specify the local path where you want to save the file
        #         await download.save_as(os.path.join(ORIENT_QUOTATION_DIR, "quotation_orient.pdf"))
        #         update_iq_quotation_status(get_app_key(), quotation_no, Orient_Status.APPROVED.value , Final_Status.PENDING.value)
        #         orient_logger.debug("File saved successfully and status updated")

        #     await asyncio.sleep(5)