import pandas as pd
import os
from src.utils.load_yaml import ATTACHMENTS_SAVE_DIR, REFERRAL_FILE_STORE_DIR
from src.utils.support_functions import get_replaced_referral_id
from src.utils.logger import logger

def read_excel(company_name, id):

    logger.debug(f"Reading Excel file for records: {company_name}")

    if id == 'default':
        # Read the Excel file
        medical_file_name = ""
        for file_name in os.listdir(ATTACHMENTS_SAVE_DIR):
            if file_name.startswith("Medical__"):
                medical_file_name = file_name

        mp_data_filepath = os.path.join(
            ATTACHMENTS_SAVE_DIR, medical_file_name)

    else:
        # Read the Excel file
        medical_file_name = ""
        for file_name in os.listdir(os.path.join(REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(id))):
            if file_name.startswith("Medical__"):
                medical_file_name = file_name

        mp_data_filepath = os.path.join(
            REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(id), medical_file_name)

    df1 = pd.read_excel(mp_data_filepath, sheet_name='Sheet1')
    df3 = pd.read_excel(mp_data_filepath, sheet_name='pioneer_plus')
    df4 = pd.read_excel(mp_data_filepath, sheet_name='custom_group')
    df3_filtered = df3[df3['Company'] == company_name]
    df4_filtered = df4[df4['Company'] == company_name]

    logger.debug(f"Excel file loaded successfully for records: {company_name}")

    return df1, df3_filtered, df4_filtered


def get_all_comapnies():
    medical_file_name = ""
    for file_name in os.listdir(ATTACHMENTS_SAVE_DIR):
        if file_name.startswith("Medical__"):
            medical_file_name = file_name

    mp_data_filepath = os.path.join(ATTACHMENTS_SAVE_DIR, medical_file_name)
    df3 = pd.read_excel(mp_data_filepath, sheet_name='pioneer_plus')
    df4 = pd.read_excel(mp_data_filepath, sheet_name='custom_group')
    companies = set(df3['Company'].unique()).union(df4['Company'].unique())
    return list(companies)

def get_broker_unique_name():
    app_key = ""
    for file_name in os.listdir(ATTACHMENTS_SAVE_DIR):
        if file_name.startswith("Medical__"):
            app_key = file_name.split("Medical__")[1].replace('.xlsx', '')
            return app_key


def get_app_key():
    app_key = ""
    for file_name in os.listdir(ATTACHMENTS_SAVE_DIR):
        if file_name.startswith("Medical__"):
            app_key = file_name.split("Medical__")[1].replace('.xlsx', '')
            return app_key
