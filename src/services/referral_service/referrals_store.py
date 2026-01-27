from src.utils.load_yaml import REFERRAL_FILE_STORE_DIR,ATTACHMENTS_SAVE_DIR
from src.utils.support_functions import get_replaced_referral_id
from src.utils.logger import logger
import os
import shutil

def save_for_referral(referral_id):
#   save attachements in referral file store with referral_id as folder name
    try:
        referral_dir = os.path.join(REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(referral_id))
        if not os.path.exists(referral_dir):
            os.makedirs(referral_dir)
        for file_name in os.listdir(ATTACHMENTS_SAVE_DIR):
            file_path = os.path.join(ATTACHMENTS_SAVE_DIR, file_name)
            shutil.copy(file_path, referral_dir)
        logger.info(f"Files saved for referral in {referral_dir}")
        
    except Exception as e:
        print(f"Error saving files for referral in {referral_dir}: {e}")



