import asyncio
import os
from src.utils.load_yaml import MIN_SLEEP,MED_SLEEP,MAX_SLEEP
from src.utils.logger import gig_logger
from datetime import datetime
from src.utils.support_functions import screenshot_and_compare, extract_dropdown_values



# process page
# *** This is the standard process page structure for the company portal add all process untill benifis mapping here ***
class MissingFieldException(Exception):
    pass

class ProcessPage:
    def __init__(self, page):
        self.page = page

    async def fill_process_form(self, df1, cat1, portal_name=None):
        gig_logger.debug("Process page started")

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "gig", "GIG_1")
        except Exception as e:
            gig_logger.error("Error occurred while taking screenshot: " + str(e))


        await self.page.locator("#product_radio_Product01").click()
        await asyncio.sleep(MAX_SLEEP)
        await self.page.locator("#createQuote").click()
        await asyncio.sleep(MAX_SLEEP)


        #Create Quote

        #Proposed Effective / Renewal Date:
        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "gig", "GIG_2")
        except Exception as e:
            gig_logger.error("Error occurred while taking screenshot: " + str(e))

        effective_from = (df1[df1['KEY'] == "Effective from"]['VALUE'].values[0])
        gig_logger.debug("Effective date given: "+effective_from)

        date_obj = datetime.strptime(effective_from, "%m/%d/%Y")
        # Convert the datetime object to dd/mm/yyyy format
        effective_from = date_obj.strftime("%d/%m/%Y")
        gig_logger.debug("Formatted Effective date: "+effective_from)

        input_locator = self.page.locator('//*[@id="input_effective_date"]')
        await input_locator.evaluate("element => element.removeAttribute('readonly')")
        await input_locator.fill(effective_from)
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Proposed Effective / Renewal Date: " + effective_from)

        #Company Name
        company_name = (df1[df1['KEY'] == "Company Name"]['VALUE'].values[0])
        await self.page.locator('//*[@id="input_client_name"]').fill(company_name)
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Company Name: " + company_name)

        #Business Nature
        business_nature= str(cat1['Business Nature'].iloc[0])
        # business_nature = str(self.df2['Business Nature'].iloc[0])
        gig_logger.debug('Businesss Nature (Before Apply) :'+business_nature)

        # Extract dropdown values for Business Nature
        region = df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]
        selector = "#select_client_business_sector"
        field_name = "Business Nature"
        await extract_dropdown_values(self.page, region, '', '', field_name, selector, portal_name)

        # business_nature=(df1[df1['KEY'] == "Businesss Nature"]['VALUE'].values[0])
        # if business_nature == "Others":
        #     business_nature = "Utilities"
            
        await self.page.locator("#select_client_business_sector").select_option(business_nature)
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Business Nature (After Apply): " + business_nature)

        
        #Contact
        await self.page.locator("#select_client_contact_title").select_option("title_ms")
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Contatct Person Title")

        contact_person = (df1[df1['KEY'] == "Contatct Person"]['VALUE'].values[0])
        await self.page.locator('//*[@id="input_client_contact_firstname"]').fill(contact_person)
        await asyncio.sleep(MED_SLEEP)
        await self.page.locator('//*[@id="input_client_contact_lastname"]').fill(contact_person)
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Contatct Person: " + contact_person)

        #Phone Number
        phone_number = (df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0])
        await self.page.locator('//*[@id="input_client_phone1"]').fill(str(phone_number))
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug(f"Phone Number: {phone_number}")

        #Office Number
        office_number = (df1[df1['KEY'] == "Contact  Number"]['VALUE'].values[0])
        await self.page.locator('//*[@id="input_client_phone2"]').fill(str(office_number))
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug(f"Office Number: {office_number}")


        #email
        email = (df1[df1['KEY'] == "Email"]['VALUE'].values[0])
        await self.page.locator('//*[@id="input_client_email"]').fill(email)
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Email: " + email)

        #city
        city = (df1[df1['KEY'] == "City"]['VALUE'].values[0])
        await self.page.locator('//*[@id="input_client_city"]').fill(city)
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("City: " + city)

        #country

        #start button
        await self.page.locator('//*[@id="next"]').click()  
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Start Button Clicked")
        await self.page.wait_for_load_state('networkidle')


        print('Process page Done')









        


        


 