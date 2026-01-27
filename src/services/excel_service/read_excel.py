import pandas as pd
import os
from src.utils.load_yaml import ATTACHMENTS_SAVE_DIR, REFERRAL_FILE_STORE_DIR
from src.utils.support_functions import get_replaced_referral_id
from src.utils.logger import logger


def read_excel(company_name, id, return_path=False):

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

    df1 = pd.read_excel(mp_data_filepath, sheet_name='Sheet1', keep_default_na=False, na_values=[''])
    df2 = pd.read_excel(mp_data_filepath, sheet_name='Sheet2', keep_default_na=False, na_values=[''])
    df2_filtered = df2[df2['Company'] == company_name]

    logger.debug(f"Excel file loaded successfully for records: {company_name}")

    if return_path:
        return df1, df2_filtered, mp_data_filepath
    return df1, df2_filtered


def get_all_comapnies():
    medical_file_name = ""
    for file_name in os.listdir(ATTACHMENTS_SAVE_DIR):
        if file_name.startswith("Medical__"):
            medical_file_name = file_name

    mp_data_filepath = os.path.join(ATTACHMENTS_SAVE_DIR, medical_file_name)
    df2 = pd.read_excel(mp_data_filepath, sheet_name='Sheet2')
    return df2['Company'].unique().tolist()


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


def get_excel_data_for_compare(id):

    try:
        directory = ATTACHMENTS_SAVE_DIR if id == 'default' else os.path.join(
            REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(id))
        
        medical_file_name = None
        census_file_name = None

        for file_name in os.listdir(directory):
            if file_name.endswith(".xlsx"):
                if file_name.startswith("Medical__"):
                    medical_file_name = file_name
                else:
                    census_file_name = file_name

        if not medical_file_name or not census_file_name:
            logger.error("Required Excel files not found for comparison")
            raise Exception("Required Excel files not found for comparison")

        logger.debug(f"Found Excel files for census regions")
            
        # full file path
        census_filepath = os.path.join(directory, census_file_name)
        medical_filepath = os.path.join(directory, medical_file_name)

        # Load the Excel file and get unique values for both columns
        census_df = pd.read_excel(census_filepath, sheet_name='Sheet1')
        medical_df = pd.read_excel(medical_filepath, sheet_name='Sheet2')
        
        mp_data_filepath = os.path.join(
            ATTACHMENTS_SAVE_DIR, medical_file_name)
        
        df1 = pd.read_excel(mp_data_filepath, sheet_name='Sheet1')
        logger.debug("Excel file loaded successfully for census regions")

        # Get unique Visa Issued Emirates values as a string
        census_regions = ', '.join(census_df['Visa Issued Emirates'].dropna().unique().astype(str))

        # Get unique Category values as a list
        unique_categories = census_df['Category'].dropna().unique().tolist()

        #Get Comapany List
        company_list = medical_df['Company'].unique().tolist()
        
        #Get Comapany List
        recipient_email = df1[df1['KEY'] == "Email"]['VALUE'].values[0]

        # Get Quotation id from the file name
        quotation_id = medical_file_name.split("Medical__")[1].replace('.xlsx', '')

        return census_regions, unique_categories, company_list, quotation_id , recipient_email
    
    except Exception as e:
        logger.error(f"Comparison Error: {e}")
        raise e