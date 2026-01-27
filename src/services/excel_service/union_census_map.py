import openpyxl 
import pandas as pd  # Renamed for clarity
import os
from src.utils.load_yaml import (
    ATTACHMENTS_SAVE_DIR, 
 
    REFERRAL_FILE_STORE_DIR
)
from src.utils.support_functions import get_replaced_referral_id
from datetime import datetime
from openpyxl.styles import numbers  # Import for number formatting
import win32com.client
import time


def union_map_census_data(id):
    census_filename = ""
    
    # Determine the directory based on the provided ID
    if id == 'default':
        search_dir = ATTACHMENTS_SAVE_DIR
    else:
        replaced_id = get_replaced_referral_id(id)
        search_dir = os.path.join(REFERRAL_FILE_STORE_DIR, replaced_id)
    
    # Search for the appropriate census file
    for file_name in os.listdir(search_dir):
        if not file_name.startswith("Medical__") and file_name.endswith(".xlsx"):
            census_filename = file_name
            break  # Assuming only one relevant file exists
    
    if not census_filename:
        raise FileNotFoundError(f"No suitable census file found in {search_dir}")
    
    # Read the Excel data into a pandas DataFrame
    excel_path = os.path.join(search_dir, census_filename)
    try:
        excel_data_df = pd.read_excel(excel_path, sheet_name='Sheet1')
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")
    
    # Directly use excel_data_df without merging
    merged_df = excel_data_df.copy()
    
    # Relation mapping
    relation_mapping = {
        "Principal": "Employee",
        "Spouse": "Dependent",
        "Child": "Dependent"
    }
    merged_df['Relation'] = merged_df['Relation'].map(relation_mapping).fillna(merged_df['Relation'])
    
    # Convert Gender to 'M' or 'F'
    merged_df['Gender'] = merged_df['Gender'].apply(
        lambda gender: 'M' if gender == 'Male' else ('F' if gender == 'Female' else gender)
    )
    print("After Converting Gender:")
    print(merged_df.head())
    
    # Convert Salary Type to 'Yes' or 'No'
    merged_df['Salary Type'] = merged_df['Salary Type'].apply(
        lambda salary_type: 'Yes' if salary_type == 'LSB' else ('No' if salary_type == 'HSB' else salary_type)
    )
    print("After Converting Salary Type:")
    print(merged_df.head())
    
    # Load the Excel template workbook and select the 'loader' sheet
    template_path = os.path.join(UNIONINSURANCE_TEMPLATES_DIR, "MemberUpload.xlsx")
    try:
        wb = openpyxl.load_workbook(template_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found at {template_path}")
    except Exception as e:
        raise ValueError(f"Error loading workbook: {e}")
    
    if 'loader' not in wb.sheetnames:
        raise ValueError("Sheet 'loader' not found in the workbook.")
    
    ws = wb['loader']
    
    # Iterate over each row in the DataFrame and populate the Excel sheet
    excel_row = 0
    for index, row in merged_df.iterrows():
        excel_row = index + 2  # Assuming the first row is a header
        
        # Handle DOB (Date of Birth)
        dob = row.get('DOB')
        if isinstance(dob, str):
            try:
                dob = datetime.strptime(dob.strip(), "%Y-%m-%d") 
            except ValueError:
                dob = None  
        elif pd.isna(dob):
            dob = None  # Handle NaN values
        
        if dob:
            dob_cell = ws.cell(row=excel_row, column=2)
            dob_cell.value = dob  # Assign datetime object directly
            dob_cell.number_format = "D-MMM-YY"  # Set desired date format
        else:
            ws.cell(row=excel_row, column=2).value = "Invalid DOB"
        
        # Assign other cell values
        ws.cell(row=excel_row, column=1).value = index + 1  # Serial Number
        ws.cell(row=excel_row, column=3).value = row.get("Gender", "")
        ws.cell(row=excel_row, column=4).value = row.get("Relation", "")
        ws.cell(row=excel_row, column=5).value = row.get("Marital status", "")
        ws.cell(row=excel_row, column=6).value = row.get("Category", "")
        ws.cell(row=excel_row, column=7).value = row.get("Salary Type", "")
        ws.cell(row=excel_row, column=8).value = row.get("Visa Issued Emirates", "")
        
        # Handle Category mapping if necessary
        category_letter = row.get("Category", "")
        category_mapping = {'A': "Category A", 'B': "Category B", 'C': "Category C"}
        category_value = category_mapping.get(category_letter, "Unknown")
        ws.cell(row=excel_row, column=6).value = category_value

        # Remove all remaining lines from the Excel sheet
      

        # Delete rows from start_row to max_row
    max_row=90
    sheet = wb.active
    print("excel" + str(excel_row))
    for row in range(excel_row+1, max_row + 1):
        sheet.delete_rows(row)
            

    
    # Save the modified workbook to the designated directory
    output_path = os.path.join(UNIONINSURANCE_GENERATED_CENSUS_DIR, "MemberUpload.xlsx")
    try:
        wb.save(output_path)
        print(f"Workbook successfully saved to {output_path}")

        #         # Launch Excel application
        # excel = win32com.client.Dispatch("Excel.Application")
        # print("Launch Excel")

        # # Open the workbook
        # workbook = excel.Workbooks.Open(output_path)
        # print("open workbook")

        # # Make the Excel application visible
        # excel.Visible = True

        # # Access the B2 cell in the active sheet
        # worksheet = workbook.ActiveSheet
        # print("Active workbook")

        # # Select the worksheet
        # b2_cell = worksheet.Range("K2")

        # # Select the B2 cell
        # b2_cell.Select()

        # # Set value to the B2 cell
        # b2_cell.Value = "New Value"
        # time.sleep(5)

        # # Remove value of the B2 cell
        # b2_cell.Value = ""
        # print("ok")
    
            
        # # Save and close the workbook
        # workbook.Save()
        # workbook.Close()
        # excel.Quit()
    except Exception as e:
        raise ValueError(f"Error saving workbook: {e}")
    