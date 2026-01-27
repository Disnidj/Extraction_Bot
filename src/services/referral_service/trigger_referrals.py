from datetime import datetime, timedelta
from patchright.async_api import async_playwright
from src.services.referral_service.referral_page import go_to_iq_referrals_page
from src.services.db_service.read import read_pending_referrals
from src.utils.load_yaml import MAX_REFERRAL_MINUTES,MED_SLEEP,MAX_RETRIES
from src.utils.logger import logger
import time

async def trigger_referrals():
    while True:
        # Read pending referrals from the database
        pending_referrals = read_pending_referrals()

        # Check if there are any pending referrals not checked in the last MAX_REFERRAL_MINUTES
        recently_unchecked_referrals = []
        for referral in pending_referrals:
            referral_time = datetime.strptime(referral[5], '%Y-%m-%d %H:%M:%S')
            
            if datetime.now() - referral_time > timedelta(minutes=MAX_REFERRAL_MINUTES):
                recently_unchecked_referrals.append(referral)

        # Exit the loop if there are no more unchecked referrals
        if not recently_unchecked_referrals:
            print("No recent pending referrals")
            logger.info("No recent pending referrals")
            break

        # Extract iq_quotation_no values from each tuple in the list
        iq_quotation_numbers = [referral[2] for referral in recently_unchecked_referrals]

        # Use Playwright to go to the referrals page
        async with async_playwright() as playwright:
            for attempt in range(MAX_RETRIES):  # Use the dynamic attempt count
                try:
                    await go_to_iq_referrals_page(playwright, iq_quotation_numbers)
                    break  # Exit the loop if successful
                except Exception as e:
                    print(f"Error in go_to_iq_referrals_page on attempt {attempt + 1}: {e}")
                    logger.error(f"Error in go_to_iq_referrals_page on attempt {attempt + 1}: {e}")
                    if attempt == MAX_RETRIES - 1:  # Last attempt
                        print("Failed after all attempts.")
                        logger.error("Failed after all attempts.")
                        # update final status to fail on all pending referrals loop

                        
                    
        #add a delay before the next iteration to avoid overloading 
        await time.sleep(MED_SLEEP)

