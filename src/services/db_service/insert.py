import sqlite3
from src.utils.load_yaml import DATABASE_PATH
from src.services.excel_service.read_excel import get_all_comapnies,get_app_key
from src.utils.enums import Final_Status, Orient_Status

def start_process_record():
    try:
        # Convert the list to a comma-separated string
        companies_str = ','.join(get_all_comapnies())

        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        values =  [get_app_key(), Orient_Status.NOT_APPLICABLE.value, companies_str, Orient_Status.NOT_APPLICABLE.value, Final_Status.STARTED.value]
        # Prepare the SQL statement for insertion
        placeholders = ', '.join(['?'] * len(values))
        sql = f"INSERT INTO process_records ({', '.join(["app_key", "iq_quotation_no", "companies","iq_status","final_status"])}) VALUES ({placeholders})"
        
        # Execute the SQL statement
        cursor.execute(sql, values)
        
        # Commit the transaction
        conn.commit()
        print("Process Record Started successfully.")
        
    except sqlite3.Error as e:
        raise Exception(f"Error inserting process record: {e}")
        
    finally:
        # Close the connection
        if conn:
            conn.close()

