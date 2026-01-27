import openpyxl 
import pandas
import os
from src.utils.load_yaml import ATTACHMENTS_SAVE_DIR,GIG_TEMPLATES_DIR,REFERRAL_FILE_STORE_DIR, GIG_GENERATED_CENSUS_DIR
from src.utils.support_functions import get_replaced_referral_id
from datetime import datetime
import pandas as pd
from openpyxl.styles import NamedStyle
from src.services.excel_service.read_excel import read_excel
from src.utils.logger import logger


def gig_map_census_data(id):
    census_filename = ""
    if id == 'default':
        for file_name in os.listdir(ATTACHMENTS_SAVE_DIR):
            if not file_name.startswith("Medical__") and file_name.endswith(".xlsx"):
                census_filename = file_name

        excel_data_df = pandas.read_excel(os.path.join(ATTACHMENTS_SAVE_DIR, census_filename), sheet_name='Sheet1')
        nationality_df = pandas.read_excel(os.path.join(ATTACHMENTS_SAVE_DIR, census_filename), sheet_name='Nationality_Updated')

    else:
        for file_name in os.listdir(os.path.join(REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(id))):
            if not file_name.startswith("Medical__") and file_name.endswith(".xlsx"):
                census_filename = file_name

        excel_data_df = pandas.read_excel(os.path.join(REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(id), census_filename), sheet_name='Sheet1')
        nationality_df = pandas.read_excel(os.path.join(REFERRAL_FILE_STORE_DIR, get_replaced_referral_id(id), census_filename), sheet_name='Nationality_Updated')

    nationality_df.columns = nationality_df.columns.str.strip()
    merged_df = pandas.merge(excel_data_df, nationality_df, left_on='Nationality', right_on='AL SAGR', how='left')

    wb = openpyxl.load_workbook(os.path.join(GIG_TEMPLATES_DIR, "MemberUpload.xlsx"))
    ws = wb['Census']



    ##Effective Date
    df1, df2 = read_excel('GIG Insurance', 'default')

    # Check if the dataframes are empty
    if df1.empty:
        print("No data found sheet1")
        logger.error("No data found sheet1")
        raise Exception("No data found sheet1")


    #Data mapping for census
    for index, row in merged_df.iterrows():
        
        #Name
        ws.cell(row=index+2, column=2).value = row['Beneficiary First Name']  

        #Member Type
        relation = row['Relation']
        if relation == 'Principal':
            relation = 'Employee'
        gender = row['Gender']
        marital_status = row['Marital status']
        member_type=F'{relation} {gender} – {marital_status}'
        ws.cell(row=index+2, column=6).value = member_type

        #Relation
        if relation == 'Employee':
            relation = 'E' 
        elif relation == 'Spouse' and gender == 'Male':
            relation = 'H'
        elif relation == 'Spouse' and gender == 'Female':
            relation = 'W'
        elif relation == 'Child' and gender == 'Male':
            relation = 'S'
        elif relation == 'Child' and gender == 'Female':
            relation = 'D'
        ws.cell(row=index+2, column=3).value = relation

        #Gender
        if gender == 'Male':
            gender = 'M'
        elif gender == 'Female':
            gender = 'F'
        ws.cell(row=index+2, column=4).value = gender

        #Marital Status        
        if marital_status == 'Single':
            marital_status = 'S'
        elif marital_status == 'Married':
            marital_status = 'M'
        ws.cell(row=index+2, column=5).value = marital_status


        


        #Date of Birth
        dob = row['DOB']

        # Define a date format style (only needs to be done once)
        date_style = NamedStyle(name="date_style", number_format="DD-MM-YY")

        # Check if the style already exists to avoid duplicate errors
        if "date_style" not in ws.parent.named_styles:
            ws.parent.add_named_style(date_style)

        # Set the value and apply the date format
        if dob:
            dob_cell = ws.cell(row=index+2, column=7)
            dob_cell.value = dob  # Assign the datetime object directly
            dob_cell.number_format = "DD-MM-YY"  # Apply the correct date format
        else:
            ws.cell(row=index+2, column=7).value = "Invalid DOB"


        ##Nationality

        # Mappings 
        nationality_mapping = dict(
            zip(nationality_df['AL SAGR'], nationality_df['GIG INSURANCE']))
        
        # Fetch the mapped nationality; if not found, use the original value
        mapped_nationality = nationality_mapping.get(row['Nationality'], row['Nationality'])

        # Assign the mapped nationality to the Excel cell
        ws.cell(row=index+2, column=8).value = mapped_nationality
        # nationality = row['Nationality']
        # ws.cell(row=index+2, column=8).value = nationality
    

        ##Category
        cat=row['Category']
        if cat == 'A':
            cat = 'CAT 1'
        if cat == 'B':
            cat = 'CAT 2'
        if cat == 'C':
            cat = 'CAT 3'
        ws.cell(row=index+2, column=9).value = cat


    # Extract the effective date from the DataFrame
    effective_date = df1[df1['KEY'] == "Effective from"]['VALUE'].values[0].strip()
    logger.debug("Effective date given: " + effective_date)

    # Convert string to datetime object
    try:
        date_obj = datetime.strptime(effective_date, "%m/%d/%Y")  # Convert to datetime
    except ValueError:
        logger.error(f"Invalid date format: {effective_date}")
        date_obj = None  # Handle invalid date case

    # Define a date format style
    date_style = NamedStyle(name="date_style", number_format="DD/MM/YYYY")

    # Avoid duplicate named styles
    if "date_style" not in ws.parent.named_styles:
        ws.parent.add_named_style(date_style)

    # Select the cell where the date should be entered
    effective_date_cell = ws.cell(row=2, column=26)

    # Assign value and apply formatting
    if date_obj:
        effective_date_cell.value = date_obj  # Use datetime object so Excel recognizes it
        effective_date_cell.number_format = "DD/MM/YYYY"  # Ensure it's formatted as a date
        
        #**Force Excel to detect it as a date by reassigning**
        temp_value = effective_date_cell.value  # Store the value
        effective_date_cell.value = None  # Clear the cell
        effective_date_cell.value = temp_value  # Reassign the value

    else:
        effective_date_cell.value = "Invalid DOB"  # Handle errors properly

    logger.debug("Formatted effective date written to Excel.")
    
    # ws.cell(row=2, column=26).value = effective_date
    logger.debug(f"Effective Date: {effective_date}")

    wb.save(os.path.join(GIG_GENERATED_CENSUS_DIR, "gig_map.xlsx"))



    

