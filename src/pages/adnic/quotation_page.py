import time
import os
# from src.utils.load_yaml import ADNIC_QUOTATION_DIR
# from src.utils.load_yaml import ADNIC_HTML_DIR
from src.utils.logger import adnic_logger

# Page object for the quotation download page
class QuotationPage:
    def __init__(self, page):
        self.page = page

        

    async def download_quotation(self):

        
        # Navigate to the quotation page
        await self.page.wait_for_load_state('networkidle')
        await self.page.locator('//*[@id="ContentPlaceHolder1_btn_quote"]').click()

        # Wait for the page to load completely
        await self.page.wait_for_load_state('networkidle')
        adnic_logger.debug("Quotation page loaded")
        time.sleep(5)

        # Click the button to open the new page 
        await self.page.locator('//*[@id="ContentPlaceHolder1_btn_quote"]').click()
        adnic_logger.debug("Print quote button clicked")
        await self.page.wait_for_load_state('networkidle')
        time.sleep(5)
        # await self.page.locator('//*[@id="ContentPlaceHolder1_btn_quote"]').click()
        adnic_logger.debug("Print quote button clicked")
        await self.page.wait_for_load_state('networkidle')
        # Wait for the new page to open
        # new_page = await self.page.context.wait_for_event('page')

        # # Wait for the new page to load completely
        # await new_page.wait_for_load_state('networkidle')
        # adnic_logger.debug("New page loaded")

        # # Take a screenshot of the new page
        # screenshot_path = os.path.join(ADNIC_QUOTATION_DIR, 'quotation_adnic_screenshot_quote.png')
        # await new_page.screenshot(path=screenshot_path)
        # adnic_logger.debug(f"Screenshot saved to {screenshot_path}")

        # #Extracting HTML Content
        # html_content = await  new_page.content()
        # # Save to file
        # html_file = ADNIC_HTML_DIR + '/output_quote.html'
        # with open(html_file, "w", encoding="utf-8") as f:
        #       f.write(html_content)
        
        # time.sleep(5)

        # # Save the new page as a PDF
        # pdf_path = os.path.join(ADNIC_QUOTATION_DIR, 'quotation_adnic_quote.pdf')
        # await new_page.pdf(path=pdf_path)
        # adnic_logger.debug(f"PDF saved to {pdf_path}")
        # time.sleep(3)

        # # Click the button to open the new page
        # await self.page.locator('//*[@id="ContentPlaceHolder1_btn_Quote2"]').click()
        # adnic_logger.debug("Print quote button clicked")
        # await self.page.wait_for_load_state('networkidle')
        # time.sleep(5)
        # adnic_logger.debug("Print quote button clicked")
        # await self.page.wait_for_load_state('networkidle')
        # # Wait for the new page to open
        # new_page = await self.page.context.wait_for_event('page')

        # # Wait for the new page to load completely
        # await new_page.wait_for_load_state('networkidle')

        # new_url = new_page.url
        # await new_page.goto(new_url)
        # adnic_logger.debug("New page loaded")
        # time.sleep(5)
        # # await self.page.locator('//*[@id="div_Print"]').highlight()
        # # benifit = await self.page.locator('//*[@id="div_Print"]').inner_text()
        # # print(benifit)

        # # Take a screenshot of the new page
        # screenshot_path = os.path.join(ADNIC_QUOTATION_DIR, 'quotation_adnic_screenshot_tob.png')
        # await new_page.screenshot(path=screenshot_path)
        # adnic_logger.debug(f"Screenshot saved to {screenshot_path}")

        # # Get the HTML content        
        # html_content = await  new_page.content()
        # # Save to file
        # html_file = ADNIC_HTML_DIR + '/output_tob.html'
        # with open(html_file, "w", encoding="utf-8") as f:
        #       f.write(html_content)
        
        # time.sleep(5)

        # # # Save the source of the new page
        # # html_path = os.path.join(ADNIC_QUOTATION_DIR, 'quotation_adnic_tob.html')
        # # await new_page.screenshot(path=html_path)
        # # adnic_logger.debug("HTML source of the new page obtained")

        # # Save the new page as a PDF
        # pdf_path = os.path.join(ADNIC_QUOTATION_DIR, 'quotation_adnic_tob.pdf')
        # await new_page.pdf(path=pdf_path)
        # adnic_logger.debug(f"PDF saved to {pdf_path}")
        # time.sleep(3)