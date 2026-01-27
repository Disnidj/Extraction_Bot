# src/pages/takaful/categories/category_a_page.py

import asyncio

from src.utils.logger import qatar_logger
from src.utils.support_functions import extract_region, extract_tpa, extract_network


class Category1Page_p1:
    def __init__(self, page):
        self.page = page
        

    async def fill_category_1_p1(self, df1, catA,portal_name):
        
        TPA_Value = str(catA['TPA'].iloc[0])
        
        # Select option for 'Emirates'
        try:
            field= 'Region'
            dropdown_selector = '//*[@id="censusDetailsAcc"]/div/form/table/tr[4]/td[2]/select'
            
            # Wait for the dropdown to be available
            await self.page.wait_for_selector(dropdown_selector, timeout=60000)
            dropdown_element = self.page.locator(dropdown_selector)
            await dropdown_element.wait_for(state="visible", timeout=60000)
            
            await extract_region(self.page, portal_name, field, dropdown_selector)
            await asyncio.sleep(2)
            
            await dropdown_element.select_option(
                label=str(df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]))
            await asyncio.sleep(3)
        
            qatar_logger.debug("Emirates Filled " + str(df1[df1['KEY'] == "Emirates"]['VALUE'].values[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        # Select option for 'TPA'
        try:
            field= 'TPA'
            region=str(df1[df1['KEY'] == "Emirates"]['VALUE'].values[0])
            dropdown_selector = '//*[@id="censusDetailsAcc"]/div/form/table/tr[5]/td[2]/select'
            
            # Wait for the TPA dropdown to be available
            await self.page.wait_for_selector(dropdown_selector, timeout=60000)
            tpa_dropdown = self.page.locator(dropdown_selector)
            await tpa_dropdown.wait_for(state="visible", timeout=60000)
            
            await extract_tpa(self.page, portal_name,region, field, dropdown_selector)
            await asyncio.sleep(2)
            
            await tpa_dropdown.select_option(
                label=str(catA['TPA'].iloc[0]))
            await asyncio.sleep(3)
        
            qatar_logger.debug("TPA Filled")
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")

        # Select option for 'Plans'
        try:
            field= 'Plan'
            network_dropdown_selector = '//*[@id="censusDetailsAcc"]/div/form/table/tr[6]/td[2]/select'
            
            # Wait for the Network dropdown to be available
            await self.page.wait_for_selector(network_dropdown_selector, timeout=60000)
            network_dropdown = self.page.locator(network_dropdown_selector)
            await network_dropdown.wait_for(state="visible", timeout=60000)
            
            await extract_network(self.page, portal_name, region, TPA_Value, field, network_dropdown_selector)
            await asyncio.sleep(2)
            
            print(str(catA['Network'].iloc[0]))
            await network_dropdown.select_option(
                label=str(catA['Network'].iloc[0]))
            await asyncio.sleep(3)
        
            qatar_logger.debug("Network Filled " + str(catA['Network'].iloc[0]))
        
        except Exception as e:
            qatar_logger.error(f"An error occurred: {e}")
            