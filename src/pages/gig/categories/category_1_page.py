
import asyncio
from src.utils.load_yaml import MED_SLEEP
from src.utils.logger import gig_logger
import asyncio
from src.utils.support_functions import screenshot_and_compare, extract_region, extract_tpa, extract_network, extract_dropdown_values

# class for the Category 2 benefits mapping
class Category1Page:
    def __init__(self, page):
        self.page = page

    async def fill_category_1(self, cat1):
        portal_name = "GIG Insurance"
        print("Cat 1")
        await self.page.wait_for_load_state('networkidle')

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "gig", "GIG_3")
        except Exception as e:
            gig_logger.error(f"Error during screenshot comparison: {e}")

        # TPA
        tpa = str(cat1['TPA'].iloc[0])
        gig_logger.debug("TPA Value: (Before Apply) " + tpa)

        # Handle TPA logic
        if tpa == "No Cover":
            await self.page.locator("div > input").first.check()
            gig_logger.debug("TPA: No Cover")
        elif tpa.startswith("Plan"):
            # Extract plan number from "Plan X"
            try:
                plan_number = int(tpa.split(" ")[-1])  # Extracts the number after "Plan"
                if 1 <= plan_number <= 8:  # Ensure the plan is between 1 and 8
                    plan_index = plan_number + 2  # Adjust index for CSS nth-child
                    await self.page.locator(f"td:nth-child({plan_index}) > div > input").first.check()
                    gig_logger.debug(f"TPA: {tpa}")
                else:
                    gig_logger.error(f"Invalid TPA: {tpa}")
            except ValueError:
                gig_logger.error(f"Invalid TPA format: {tpa}")

        gig_logger.debug("TPA Value: (After Apply) " + tpa)

        # Using async sleep instead of await asyncio.sleep
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("TPA Filled")



        #Region
        region=str(cat1['Region'].iloc[0])
        gig_logger.debug("Region Value: (Before Apply) " + region)
        dropdown_selector = '[id="emirates"]'
        await extract_region(self.page, portal_name, 'Region', dropdown_selector)

        if region == 'Dubai':
            await self.page.select_option('[id="emirates"]', value='UAE Dubai & NE')
            await asyncio.sleep(MED_SLEEP)
            gig_logger.debug("Region Value: (After Apply) " + 'UAE Dubai & NE')


        network = str(cat1['Network'].iloc[0])

        #Coinsurance option
        coinsurance=str(cat1['Op Co Insurance'].iloc[0])
        selector = '[id="waiver_coins"]'
        gig_logger.debug("Coinsurance Value: (Before Apply) " + coinsurance)
        await extract_dropdown_values(self.page, region, tpa, network,  'Op Co Insurance', selector, portal_name)
        await self.page.select_option('[id="waiver_coins"]', value=coinsurance)       

        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Coinsurance Value: (After Apply) " + coinsurance)

        
        # Network
        network = str(cat1['Network'].iloc[0])
        gig_logger.debug("Network Value: (Before Apply) " + network)
        selector = '[id="waiver_network"]'
        await extract_network(self.page, portal_name, region, tpa, 'Network', selector)
        await self.page.select_option('[id="waiver_network"]', value=network)

        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Network Value: (After Apply) " + network)

        #Dental
        dental= str(cat1['Dental'].iloc[0])
        gig_logger.debug("Dental Value: (Before Apply) " + dental)
        selector = '[id="waiver_dental"]'
        await extract_dropdown_values(self.page, region, tpa, network, 'Dental', selector, portal_name)
        # Handle Dental logic   
        if dental == 'Not Applicable':
            await self.page.select_option('[id="waiver_dental"]', value='AD: Not Applicable/DXB: Option 2')
        elif dental == 'Applicable':
            await self.page.select_option('[id="waiver_dental"]', value='AD: Applicable/DXB: Option 1')

        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Dental Value: (After Apply) " + dental)


        # Optical
        optical= str(cat1['Optical'].iloc[0])
        gig_logger.debug("Optical Value: (Before Apply) " + optical)
        selector = '[id="waiver_optical"]'
        await extract_dropdown_values(self.page, region, tpa, network,  'Optical', selector, portal_name)
        await self.page.select_option('[id="waiver_optical"]', value=optical)
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Optical Value: (After Apply) " + optical)

        #Group Life
        # health_plan=str(cat1[''].iloc[0])
        await self.page.locator("tr:nth-child(10) > td:nth-child(2) > div > input").check()
        gig_logger.debug('Group Life: Not Planned')
        await asyncio.sleep(MED_SLEEP)

        #Personal Accident
        await self.page.locator("tr:nth-child(15) > td:nth-child(2)").click()
        gig_logger.debug('Personal accident: Not Planned')
        await asyncio.sleep(MED_SLEEP)


        


        
      
        
        



    