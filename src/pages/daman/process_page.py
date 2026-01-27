# import asyncio
# import os
# from src.utils.load_yaml import ALSAGR_UPLOAD_CENSUS_DIR, ALSAGR_GENERATED_CENSUS_DIR, MED_SLEEP,MAX_SLEEP
# from src.utils.logger import daman_logger
# from datetime import datetime


# # process page
# # *** This is the standard process page structure for the company portal add all process untill benifis mapping here ***
# class MissingFieldException(Exception):
#     pass

# class ProcessPage:
#     def __init__(self, page):
#         self.page = page

#     async def fill_process_form(self, df1, cat1):

#         await self.page.get_by_role("button", name="󰍜").click()
#         await self.page.get_by_role("link", name=" Medical Portal 󰅂").click()
#         await self.page.get_by_role("link", name="SME/Group/EBP B2B 󰅂").click()
#         await self.page.get_by_role("link", name="Quotation Information").click()
#         await asyncio.sleep(MAX_SLEEP)
#         await self.page.get_by_role("button", name=" New Quotation").click()
#         await asyncio.sleep(MED_SLEEP)
       
        

#         # # Uplaod Censuse file
#         # file_input_locator = self.page.locator("input[type='file'][accept*='.xlsx']")
#         # await file_input_locator.wait_for(state="attached", timeout=10000) 

#         # # Set the file
#         # await file_input_locator.set_input_files("D:\\AlgoSpring\\python\\MaxHealth\\MaxHealth.xlsx")
        
#         # Branch
#         await self.page.locator("#CollapseQuoteInformation #branch").select_option("DUBAI")
#         await asyncio.sleep(MAX_SLEEP)
#         await self.page.wait_for_load_state('networkidle')

#         # Client Type 
#         client_type = (df1[df1['KEY'] == "New-Renew"]['VALUE'].values[0])
#         print(client_type)
#         if client_type == "New":
#             await self.page.locator("#client").select_option("New Client")
#         else:
#             await self.page.locator("#client").select_option("Existing Client")
#         print(client_type)
        
#         await asyncio.sleep(MED_SLEEP)

#         # Product Type
#         await self.page.locator("#CollapseQuoteInformation #productType").select_option("SME")
#         print("Product Type: SME")
#         await asyncio.sleep(MED_SLEEP)

#         # Click Add Prospect Button
#         await self.page.get_by_role("button", name="Add Prospect").click()
#         await asyncio.sleep(MED_SLEEP)

# #-------------------------------------------------Insured Information-------------------------------------------------#
#         # Insured Type
#         insured_type = (df1[df1['KEY'] == "Insured Type"]['VALUE'].values[0])
#         await self.page.locator("#insuredType").select_option(insured_type)
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.wait_for_load_state('networkidle')

#         # Company CR Number
#         company_CR_number = (df1[df1['KEY'] == "Company CR Number"]['VALUE'].values[0])
#         await self.page.locator("#companyCRNumber").fill(str(company_CR_number))
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.wait_for_load_state('networkidle')

#         # Insured / Company Name
#         company_name = (df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
#         print(company_name)
#         await self.page.locator("#fullName").fill(company_name)
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.wait_for_load_state('networkidle')

#         # Email
#         email = (df1[df1['KEY'] == "Email"]['VALUE'].values[0])
#         await self.page.locator("#policyEmail").fill(email)
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.wait_for_load_state('networkidle')

#         # Trade License Number
#         trade_licence_number = (df1[df1['KEY'] == "Trade License Number"]['VALUE'].values[0])
#         print(trade_licence_number)
#         await self.page.locator("#tradeLicenseNo").fill(str(trade_licence_number))
#         print(trade_licence_number)
#         await asyncio.sleep(MED_SLEEP)

#              # Trade License Expiry Date - Change date format parsing to match the Excel format
#         trade_licence_ex_date = (df1[df1['KEY'] == "Trade License Expiry Date"]['VALUE'].values[0])
#         print(trade_licence_ex_date)

#         # Correct format for day/month/year
#         formatted_date = datetime.strptime(trade_licence_ex_date, '%d/%m/%Y').strftime('%Y-%m-%d')
#         print(formatted_date)

#         await self.page.locator("#tradeLicenseExpiryDate").fill(formatted_date)
#         await asyncio.sleep(MAX_SLEEP)



#         # Telephone Number
#          # No need to fill this field

#         # Entity Type
#         entity_type = str(cat1['Entity Type'].iloc[0])
#         await self.page.locator("#entityType").select_option(entity_type)
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.wait_for_load_state('networkidle')

#         # Entity ID
#         entity_id = str(cat1['Entity ID'].iloc[0])
#         await self.page.locator("#fullNaentityIdme").fill(entity_id)
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.wait_for_load_state('networkidle')

#         # Click Save Button
#         await self.page.locator("//*[@id='CollapseCustomerInfo']/div[2]/button").click()
#         await asyncio.sleep(MAX_SLEEP)

#         # Click Pop-up Window Ok Button
#         await self.page.get_by_role("button", name="Ok S").click()
#         await asyncio.sleep(MAX_SLEEP)


#         # Insured Type
#         tpa = str(cat1['TPA'].iloc[0])
#         print(tpa)
#         await self.page.wait_for_load_state('networkidle')
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.locator("#CollapseQuoteInformation #tpa").select_option(tpa)
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.wait_for_load_state('networkidle')

#         # Currency - Autofilled
#         # Maternity Age Min - Autofilled
#         # Maternity Age Max - Autofilled
#         # Child Min Age - Autofilled
#         # Child Max Age - Autofilled

#         # Nature of Group
#         nature_of_group = (df1[df1['KEY'] == "Businesss Nature"]['VALUE'].values[0])
#         await self.page.locator("#natureOfGroup").select_option(nature_of_group)
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.wait_for_load_state('networkidle')


#         # Effective Date
#         effective_from = (df1[df1['KEY'] == "Effective from"]['VALUE'].values[0])
#         print(effective_from)
        
#         # Correct format for day/month/year
#         effective_from = datetime.strptime(effective_from, '%d/%m/%Y').strftime('%Y-%m-%d')
#         print(effective_from)
        
#         await self.page.locator("#effectiveDate").fill(effective_from)
#         await asyncio.sleep(MAX_SLEEP)

#         # effective_from = self.fetch_value(self.df1, "Effective from")
#         # print(effective_from)
#         # await self.page.locator("#effectiveDate").fill("2025-01-09")
#         # print(effective_from)
#         # await asyncio.sleep(0.5)

#         # Expiry Date -Autofilled

#         # Click  I agree to all terms and Conditions as per Guidelines.
#         await self.page.wait_for_load_state('networkidle')
#         await asyncio.sleep(MED_SLEEP)
#         await self.page.locator("#agreeTerms").click()
#         daman_logger.debug("Agreed")
#         await asyncio.sleep(MED_SLEEP)

#         # Click Yes Button
#         await self.page.get_by_role("button", name="Yes S").click()
#         daman_logger.debug("Clicked Yes")
#         await asyncio.sleep(MED_SLEEP)

#         # click Save Button
#         await self.page.get_by_role("button", name="󰆓 Save").click()
#         daman_logger.debug("Clicked Save")
#         await asyncio.sleep(MED_SLEEP)

#         # Click Pop-up Window Ok Button
#         await self.page.get_by_role("button", name="Ok S").click()
#         daman_logger.debug("Clicked Ok")
#         await asyncio.sleep(MED_SLEEP)

#         # Click Next Button
#         await self.page.get_by_role("button", name="Next m").click()
#         daman_logger.debug("Clickded Next")
#         await asyncio.sleep(MED_SLEEP)

#         # Click Uplaod Button
#         await self.page.get_by_role("button", name="2").click()
#         daman_logger.debug("Clickde Upload Button")
#         await asyncio.sleep(MED_SLEEP)

    
#         # Set file to upload
#         file_path = (os.path.join(ALSAGR_GENERATED_CENSUS_DIR,"MemberUpload.xlsx"))
#         await self.page.get_by_label("Select Excel File:").set_input_files(file_path)
#         daman_logger.debug("File Uploaded")
#         await asyncio.sleep(MED_SLEEP)

#         # Click Uplaod Button
#         await self.page.get_by_role("button", name="Upload").click()
#         daman_logger.debug("Cliced upload button after file upload")
#         await asyncio.sleep(MED_SLEEP)

#         # Click Proceed button
#         await self.page.get_by_text("Proceed").click()
#         daman_logger.debug("Clicked proceed button")
#         await asyncio.sleep(MED_SLEEP)


#         # Click Next Button
#         await self.page.get_by_role("button", name="Next m").click()
#         daman_logger.debug("Clicked Next")
#         await asyncio.sleep(MED_SLEEP)


#         await asyncio.sleep(MAX_SLEEP)
#         await asyncio.sleep(MAX_SLEEP)

 