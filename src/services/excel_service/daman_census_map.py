import openpyxl
import pandas as pd
import os
import time
import win32com.client as win32  # Import the win32com.client module
from src.utils.load_yaml import ATTACHMENTS_SAVE_DIR, DAMAN_TEMPLATES_DIR, REFERRAL_FILE_STORE_DIR, DAMAN_GENERATED_CENSUS_DIR
from src.utils.support_functions import get_replaced_referral_id
from datetime import datetime

def daman_map_census_data(id):
    if id == 'default':
        census_filename = ""
        request_filename = ""

        # Identify the required files in ATTACHMENTS_SAVE_DIR
        for file_name in os.listdir(ATTACHMENTS_SAVE_DIR):
            if file_name.startswith("Medical_") and file_name.endswith(".xlsx"):
                request_filename = file_name  # File starting with 'Medical_'
            elif not file_name.startswith("Medical__") and file_name.endswith(".xlsx"):
                census_filename = file_name  # File NOT starting with 'Medical__'

        # Load the census and nationality data
        excel_data_df = pd.read_excel(os.path.join(ATTACHMENTS_SAVE_DIR, census_filename), sheet_name='Sheet1')
        nationality_df = pd.read_excel(os.path.join(ATTACHMENTS_SAVE_DIR, census_filename), sheet_name='Nationality_Updated')

        # Load the request data from 'Medical_' file
        request_data_df1 = pd.read_excel(os.path.join(ATTACHMENTS_SAVE_DIR, request_filename), sheet_name='Sheet1')
        request_data_df2 = pd.read_excel(os.path.join(ATTACHMENTS_SAVE_DIR, request_filename), sheet_name='Sheet2')
        
        print(excel_data_df)

    else:
        for file_name in os.listdir(os.path.join(REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(id))):
            if not file_name.startswith("Medical__") and file_name.endswith(".xlsx"):
                census_filename = file_name

        excel_data_df = pd.read_excel(os.path.join(REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(id), census_filename), sheet_name='Sheet1')
        nationality_df = pd.read_excel(os.path.join(REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(id), census_filename), sheet_name='National_Updated')

    merged_df = pd.merge(excel_data_df, nationality_df, left_on='Nationality', right_on='AL SAGR', how='left')

    # Load the template workbook using openpyxl
    template_path = os.path.join(DAMAN_TEMPLATES_DIR, "SME_Member_Details_Template.xlsx")
    wb = openpyxl.load_workbook(template_path)
    ws = wb['Member_Details']
    
    # Extract Effective from date
    if 'KEY' in request_data_df1.columns and 'VALUE' in request_data_df1.columns:
        effective_from_row = request_data_df1[request_data_df1['KEY'] == 'Effective from']
        if not effective_from_row.empty:
            effective_from_date = effective_from_row.iloc[0]['VALUE']
            print(effective_from_date)
            ws['B16'] = effective_from_date  # Writing the Effective from date to E15
            
    # Get unique categories from the 'Category' column
    unique_categories = excel_data_df['Category'].unique()

    # Write the associated values (Salary Type, Visa Issued Emirates, Network) for each unique category to the Excel sheet
    for i, category in enumerate(unique_categories):
        # Extract associated values for the category
        category_data = excel_data_df[excel_data_df['Category'] == category]
        salary_type = category_data['Salary Type'].iloc[0]  # Assuming the first row contains the value
        visa_issued = category_data['Visa Issued Emirates'].iloc[0]  # Similarly, for Visa Issued Emirates

        # Extract the Network value for this category from request_data_df2
        network_value = request_data_df2[request_data_df2['Category'] == category]['Network'].values
        network = network_value[0] if len(network_value) > 0 else "Not Available"

        # Write the values into the Excel sheet (A10, A11, etc.)
        ws.cell(row=21 + i, column=2).value = f"CAT {category}"  # Write Category (A, B, C, ...)
        ws.cell(row=21 + i, column=3).value = visa_issued  # Write Visa Issued Emirates for the category
        ws.cell(row=21 + i, column=4).value = network  # Write Network for the category (NEW ADDITION)
        ws.cell(row=21 + i, column=5).value = salary_type  # Write Salary Type for the category

    for index, row in merged_df.iterrows():
        ws.cell(row=index+52, column=1).value = row['Beneficiary First Name']
        ws.cell(row=index+52, column=2).value = row['DOB']
        ws.cell(row=index+52, column=3).value = row['Gender']
        ws.cell(row=index+52, column=4).value = row['Marital status']
        ws.cell(row=index+52, column=5).value = row['Relation']
        ws.cell(row=index+52, column=6).value = f"CAT {row['Category']}"
        ws.cell(row=index+52, column=7).value = row['Visa Issued Emirates']

    # Save the workbook using openpyxl
    output_path = os.path.join(DAMAN_GENERATED_CENSUS_DIR, "SME_Member_Details_Template.xlsx")
    wb.save(output_path)

    # Open the Excel file using pywin32
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = True  # Make Excel visible
    workbook = excel.Workbooks.Open(output_path)
    
    time.sleep(5)

    # Save and close the workbook
    workbook.Save()
    workbook.Close()
    excel.Quit()