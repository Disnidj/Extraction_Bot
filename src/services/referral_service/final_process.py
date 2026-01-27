from patchright.async_api import async_playwright
from src.utils.move_for_electroneek import move_files_to_electroneek_dir
from src.services.comparison_service.trigger_comparison import trigger_comparison
from src.services.db_service.update import update_final_status
from src.utils.restart_portals import login_with_retry
from src.services.excel_service.aura_census_map import aura_map_census_data
from src.services.excel_service.nlg_census_map import nlg_map_census_data
from src.pages.takaful.takafulmain import login_takaful
from src.pages.nlg.nlg_main import login_nlg
from src.utils.enums import Final_Status
from src.services.db_service.update import update_iq_status
from src.utils.enums import Final_Status
import time

async def run_portals(quatation_no, orient_status):
        #map census data
        aura_map_census_data(quatation_no)

        # map census data
        nlg_map_census_data(quatation_no)

        async with async_playwright() as playwright:

            # Retry NLG login
            nlg_success = await login_with_retry(login_nlg, "NLG", playwright, quatation_no)

            # Retry NLG login
            takaful_success = await login_with_retry(login_takaful, "takaful", playwright, quatation_no)

            # Final result of the tasks
            if nlg_success or takaful_success:
                print("All portals logged in successfully!")
                # Move files to ElectronEEK directory for comparison process
                move_files_to_electroneek_dir()
                # Trigger the comparison
                await trigger_comparison(quatation_no)
                # update iq status
                update_iq_status(quatation_no, orient_status)
                # update final playwright status
                update_final_status(quatation_no, Final_Status.COMPLETED.value, "iq_quotation_no")
            else:
                print(f"Failed portals: {'NLG' if not nlg_success else ''} {'TAKAFUL' if not takaful_success else ''}".strip())