import yaml
import os
from datetime import datetime

# Define the path to the configuration yaml file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../config.yaml')
# CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

# Load the configuration from the YAML file once
with open(CONFIG_PATH, "r") as file:
    config = yaml.safe_load(file)


# for extracted data file
EXTRACTED_DATA_DIR = ""  # default is None
def set_extracted_data_file():
    global EXTRACTED_DATA_DIR
    today = datetime.now().strftime("%Y%m%d")
    folder = "extracted_data"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"extracted_data_{today}.txt")
    # Create the file if it doesn't exist
    with open(path, "a"):
        pass
    EXTRACTED_DATA_DIR = path
    print(f"Extracted data will be saved to: {EXTRACTED_DATA_DIR}")
    return path

BROKER_ID = config['api']['broker_id']
API_BASE_URL = config['api']['base_url']

ATTACHMENTS_SAVE_DIR= config['paths']['attachments_save_dir']
# EXTRACTED_DATA_DIR = config['paths']['extracted_data_dir']
LOGS_PATH = config['paths']['logs_dir']
BASE_PATH = config['paths']['base_path']
REFERRAL_FILE_STORE_DIR = config['paths']['referral_file_store_dir']
DATABASE_PATH = config['paths']['database_path']
SCREENSHOTS_DIR = config['paths']['screenshots_dir']
DB_UPDATE_DIR = config['paths']['db_update']
IQ2HEALTH_GENERATED_CENSUS_DIR = config['iq2health']['generated_census_dir']
IQ2HEALTH_TEMPLATES_DIR = config['iq2health']['template_dir']
 
AURA_GENERATED_CENSUS_DIR = config['aura']['generated_census_dir']

ALSAGR_USERNAME = config['alsagr']['username']
ALSAGR_PASSWORD = config['alsagr']['password']
ALSAGR_GENERATED_CENSUS_DIR = config['alsagr']['generated_census_dir']
ALSAGR_TEMPLATES_DIR = config['alsagr']['templates_dir']
ALSAGR_DEFAULT_QUOTATION_ID = config['alsagr'].get('default_quotation_id', None)
 
ORIENT_EMIAL = config['orient']['email']
ORIENT_PASSWORD = config['orient']['password']
ORIENT_QUOTATION_DIR = config['orient']['quotation_download_dir']

ORIENT_AURA_EMAIL = config['orient_aura']['email']
ORIENT_AURA_PASSWORD = config['orient_aura']['password']
ORIENT_AURA_QUOTATION_DIR = config['orient_aura']['quotation_download_dir']
ORIENT_AURA_GENERATED_CENSUS_DIR = config['orient_aura']['generated_census_dir']
ORIENT_AURA_TEMPLATES_DIR = config['orient_aura']['templates_dir']

NLGI_AURA_EMAIL = config['nlgi_aura']['email']
NLGI_AURA_PASSWORD = config['nlgi_aura']['password']
NLGI_AURA_QUOTATION_DIR = config['nlgi_aura']['quotation_download_dir']
NLGI_AURA_GENERATED_CENSUS_DIR = config['nlgi_aura']['generated_census_dir']
NLGI_AURA_TEMPLATES_DIR = config['nlgi_aura']['templates_dir']

QIC_HEALTHX_EMAIL = config['qic_healthx']['email']
QIC_HEALTHX_PASSWORD = config['qic_healthx']['password']
QIC_HEALTHX_QUOTATION_DIR = config['qic_healthx']['quotation_download_dir']
QIC_HEALTHX_GENERATED_CENSUS_DIR = config['qic_healthx']['generated_census_dir']
QIC_HEALTHX_TEMPLATES_DIR = config['qic_healthx']['templates_dir']
 
RAK_EMAIL = config['rak']['email']
RAK_PASSWORD = config['rak']['password']
RAK_QUOTATION_DIR = config['rak']['quotation_download_dir']
 
TAKAFUL_EMAIL = config['takaful']['email']
TAKAFUL_PASSWORD = config['takaful']['password']
TAKAFUL_QUOTATION_DIR = config['takaful']['quotation_download_dir']
 
NLG_USERNAME = config['NLG']['username']
NLG_PASSWORD = config['NLG']['password']
NLG_GENERATED_CENSUS_DIR = config['NLG']['generated_census_dir']
NLG_TEMPLATES_DIR = config['NLG']['templates_dir']
NLG_QUOTATION_DIR = config['NLG']['quotation_download_dir']
 
LIVA_INSURANCE_USERNAME = config['liva_insurance']['username']
LIVA_INSURANCE_PASSWORD = config['liva_insurance']['password']
LIVA_INSURANCE_GENERATED_CENSUS_DIR = config['liva_insurance']['generated_census_dir']
 
DUBAIINSURANCE_USERNAME = config['dubaiinsurance']['username']
DUBAIINSURANCE_PASSWORD = config['dubaiinsurance']['password']
DUBAIINSURANCE_GENERATED_CENSUS_DIR = config['dubaiinsurance']['generated_census_dir']
DUBAIINSURANCE_TEMPLATES_DIR = config['dubaiinsurance']['templates_dir']
DUBAIINSURANCE_QUOTATION_DIR = config['dubaiinsurance']['quotation_download_dir']
 
ISON_EMAIL = config['ison']['email']
ISON_PASSWORD = config['ison']['password']
ISON_GENERATED_CENSUS_DIR = config['ison']['generated_census_dir']
ISON_TEMPLATES_DIR = config['ison']['templates_dir']
ISON_QUOTATION_DIR = config['ison']['quotation_download_dir']
 
SUKOON_EMAIL = config['sukoon']['email']
SUKOON_PASSWORD = config['sukoon']['password']
SUKOON_GENERATED_CENSUS_DIR = config['sukoon']['generated_census_dir']
SUKOON_TEMPLATES_DIR = config['sukoon']['templates_dir']
SUKOON_QUOTATION_DIR = config['sukoon']['quotation_download_dir']
SUKOON_TEMP_IMG_DIR = config['sukoon']['temp_img_dir']
 
MAXHEALTH_EMAIL = config['maxHealth']['email']
MAXHEALTH_PASSWORD = config['maxHealth']['password']
MAXHEALTH_GENERATED_CENSUS_DIR = config['maxHealth']['generated_census_dir']
MAXHEALTH_TEMPLATES_DIR = config['maxHealth']['templates_dir']
MAXHEALTH_QUOTATION_DIR = config['maxHealth']['quotation_download_dir']
 
DNI_EMAIL = config['dni']['email']
DNI_PASSWORD = config['dni']['password']
DNI_QUOTATION_DIR = config['dni']['quotation_download_dir']
 
QATAR_EMAIL = config['qatar']['email']
QATAR_PASSWORD = config['qatar']['password']
QATAR_QUOTATION_DIR = config['qatar']['quotation_download_dir']
 
ADNIC_USERNAME = config['adnic']['username']
ADNIC_PASSWORD = config['adnic']['password']
ADNIC_GENERATED_CENSUS_DIR = config['adnic']['generated_census_dir']
ADNIC_TEMPLATES_DIR = config['adnic']['templates_dir']
ADNIC_QUOTATION_DIR = config['adnic']['quotation_download_dir']
 
NGI_TOOL_DIR = config['ngi']['tool_dir']
NGI_QUOTATION_DIR = config['ngi']['quotation_download_dir']
 
WATANIATAKAFUL_USERNAME = config['wataniatakaful']['email']
WATANIATAKAFUL_PASSWORD = config['wataniatakaful']['password']
WATANIATAKAFUL_QUOTATION_DIR = config['wataniatakaful']['quotation_download_dir']
 
FIDELITY_USERNAME = config['FIDELITY']['username']
FIDELITY_PASSWORD = config['FIDELITY']['password']
FIDELITY_QUOTATION_DIR = config['FIDELITY']['quotation_download_dir']
 
GIG_USERNAME = config['GIG']['username']
GIG_PASSWORD = config['GIG']['password']
GIG_GENERATED_CENSUS_DIR = config['GIG']['generated_census_dir']
GIG_TEMPLATES_DIR = config['GIG']['templates_dir']
GIG_QUOTATION_DIR = config['GIG']['quotation_download_dir']
 
DAMAN_USERNAME = config['daman']['username']
DAMAN_PASSWORD = config['daman']['password']
DAMAN_GENERATED_CENSUS_DIR = config['daman']['generated_census_dir']
DAMAN_TEMPLATES_DIR = config['daman']['templates_dir']
DAMAN_QUOTATION_DIR = config['daman']['quotation_download_dir']
 
MEDGULF_USERNAME = config['medgulf']['email']
MEDGULF_PASSWORD = config['medgulf']['password']
MEDGULF_QUOTATION_DIR = config['medgulf']['quotation_download_dir']
 
ALITTIHAD_ALWATANI_USERNAME = config['AI_ITTIHAD_AI_WATANI']['username']
ALITTIHAD_ALWATANI_PASSWORD = config['AI_ITTIHAD_AI_WATANI']['password']
ALITTIHAD_ALWATANI_QUOTATION_DIR = config['AI_ITTIHAD_AI_WATANI']['quotation_download_dir']
 
MEDGULFEXCEL_TOOL_DIR = config['medgulf_excel']['tool_dir']
MEDGULFEXCEL_QUOTATION_DIR = config['medgulf_excel']['quotation_download_dir']
 
ORIENTEXCEL_TOOL_DIR = config['orient_excel']['tool_dir']
ORIENTEXCEL_QUOTATION_DIR = config['orient_excel']['quotation_download_dir']
 
APRILEXCEL_TOOL_DIR = config['april_excel']['tool_dir']
APRILEXCEL_QUOTATION_DIR = config['april_excel']['quotation_download_dir']
 
EMAIL_GENERATED_CENSUS_DIR = config['email_portals']['generated_census_dir']
EMAIL_CENCUS_TEMPLATE_DIR = config['email_portals']['templates_dir']
 
# *** ALLIANZ configuration ***
ALLIANZ_EMAIL_TO = config['ALLIANZ']['email_to']
ALLIANZ_EMAIL_CC = config['ALLIANZ']['email_cc']
 
# *** BUPA configuration ***
BUPA_EMAIL_TO = config['BUPA']['email_to']
BUPA_EMAIL_CC = config['BUPA']['email_cc']
 
# *** CIGNA configuration ***
CIGNA_EMAIL_TO = config['CIGNA']['email_to']
CIGNA_EMAIL_CC = config['CIGNA']['email_cc']
 
# *** HANSE_MERKUR configuration ***
HANSE_MERKUR_EMAIL_TO = config['HANSE_MERKUR']['email_to']
HANSE_MERKUR_EMAIL_CC = config['HANSE_MERKUR']['email_cc']
 
# *** NOW_HEALTH configuration ***
NOW_HEALTH_EMAIL_TO = config['NOW_HEALTH']['email_to']
NOW_HEALTH_EMAIL_CC = config['NOW_HEALTH']['email_cc']
 
# *** APRIL_INTERNATIONAL configuration ***
APRIL_INTERNATIONAL_EMAIL_TO = config['APRIL_INTERNATIONAL']['email_to']
APRIL_INTERNATIONAL_EMAIL_CC = config['APRIL_INTERNATIONAL']['email_cc']
 
# *** QATAR_INSURANCE configuration ***
QATAR_INSURANCE_EMAIL_TO = config['QATAR_INSURANCE']['email_to']
QATAR_INSURANCE_EMAIL_CC = config['QATAR_INSURANCE']['email_cc']
 
COMPARISON_GENERATED_DIR = config['comparison']['generated_comparison_dir']
COMPARISON_TEMPLATE = config['comparison']['template']
 
POPPLER_PATH = config['poppler']['path']
 
TWO_CAPTCHA_API_KEY = config['captcha']['api_key']
 
IS_HEADLESS = config['modes']['headless']
IS_PARALLEL = config['modes']['parallel']
 
MIN_SLEEP = config['sleep']['min']
MED_SLEEP = config['sleep']['med']
MAX_SLEEP = config['sleep']['max']
 
MAX_RETRIES = config['retry']['max_attempts']
 
MAX_REFERRAL_MINUTES = config['referrals']['max_minutes']
IS_REFERRAL_ACTIVE = config['referrals']['active']

# *** EXTRACTION NOTIFICATIONS configuration ***
EXTRACTION_NOTIFICATIONS_ENABLED = config.get('extraction_notifications', {}).get('enabled', False)
OUTLOOK_CLIENT_ID = config.get('extraction_notifications', {}).get('outlook', {}).get('client_id', '')
OUTLOOK_TENANT_ID = config.get('extraction_notifications', {}).get('outlook', {}).get('tenant_id', '')
OUTLOOK_TOKEN_CACHE_PATH = config.get('extraction_notifications', {}).get('outlook', {}).get('token_cache_path', 'config/outlook_token_cache.json')
NOTIFICATION_RECIPIENTS_TO = config.get('extraction_notifications', {}).get('recipients', {}).get('to_recipients', [])
NOTIFICATION_RECIPIENTS_CC = config.get('extraction_notifications', {}).get('recipients', {}).get('cc_recipients', [])