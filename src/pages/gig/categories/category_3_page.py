import asyncio
from src.utils.load_yaml import MED_SLEEP
from src.utils.logger import gig_logger
import asyncio

# class for the Category 3 benefits mapping
class Category3Page:
    def __init__(self, page):
        self.page = page

    async def fill_category_3(self, cat3):
        print('Cat 3')
        # Ensure all values are strings and select options for Category 3

        await self.page.locator('//*[@id="add_class"]').click()

        gig_logger.debug("Add Category 2")
        await self.page.wait_for_load_state('networkidle')

        # TPA
        tpa = str(cat3['TPA'].iloc[0])
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
        region=str(cat3['Region'].iloc[0])
        gig_logger.debug("Region Value: (Before Apply) " + region)

        if region == 'Dubai':
            await self.page.select_option('[id="emirates"]', value='UAE Dubai & NE')
            await asyncio.sleep(MED_SLEEP)
            gig_logger.debug("Region Value: (After Apply) " + 'UAE Dubai & NE')


        #Coinsurance option
        coinsurance=str(cat3['Op Co Insurance'].iloc[0])
        gig_logger.debug("Coinsurance Value: (Before Apply) " + coinsurance)
        await self.page.select_option('[id="waiver_coins"]', value=coinsurance)       

        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Coinsurance Value: (After Apply) " + coinsurance)

        
        # Network
        network = str(cat3['Network'].iloc[0])
        gig_logger.debug("Network Value: (Before Apply) " + network)
        await self.page.select_option('[id="waiver_network"]', value=network)

        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Network Value: (After Apply) " + network)

        #Dental
        dental= str(cat3['Dental'].iloc[0])
        gig_logger.debug("Dental Value: (Before Apply) " + dental)
        if dental == 'Not Applicable':
            await self.page.select_option('[id="waiver_dental"]', value='AD: Not Applicable/DXB: Option 2')
        elif dental == 'Applicable':
            await self.page.select_option('[id="waiver_dental"]', value='AD: Applicable/DXB: Option 1')

        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Dental Value: (After Apply) " + dental)


        # Optical
        optical= str(cat3['Optical'].iloc[0])
        gig_logger.debug("Optical Value: (Before Apply) " + optical)
        await self.page.select_option('[id="waiver_optical"]', value=optical)
        await asyncio.sleep(MED_SLEEP)
        gig_logger.debug("Optical Value: (After Apply) " + optical)

        #Group Life
        # health_plan=str(cat3[''].iloc[0])
        await self.page.locator("tr:nth-child(10) > td:nth-child(2) > div > input").check()
        gig_logger.debug('Group Life: Not Planned')

        #Personal Accident
        await self.page.locator("tr:nth-child(15) > td:nth-child(2)").click()
        gig_logger.debug('Personal accident: Not Planned')