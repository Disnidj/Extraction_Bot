import pandas as pd
import json
import time
import os
from src.utils.load_yaml import BROKER_ID, ATTACHMENTS_SAVE_DIR

from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from src.services.db_config.db_connect import MySQLDatabase

# Your existing file download functions are imported here
from src.services.db_service.db_file_download import process_download_cencus
from src.services.db_service.db_file_download import process_download_tob
from src.services.db_service.db_file_download import process_download_trade_license

# --- MODIFIED FUNCTIONS TO ACCEPT A DB CONNECTION ---

def fetch_first_pending_request(db):
    """
    Fetches the single, oldest pending request using an existing database connection.
    """
    try:
        query = """
        SELECT * FROM WebDB_Live.medical_cloud_requests
        WHERE broker_id = %s AND Req_Id IN (9,10)
        ORDER BY Req_Id ASC
        LIMIT 1
        """
        request = db.fetch_one(query, (BROKER_ID,))
        
        if request and isinstance(request, dict):
            return request
        return None
    except Exception as e:
        print(f"Database query failed while fetching pending request. Error: {e!r}")
        return None

def update_request_status(db, req_id, new_status):
    """
    Updates the status of a request using an existing database connection.
    """
    try:
        data = {"status": new_status}
        condition = f"Req_Id = {req_id}"
        result = db.update_record("WebDB_Live.medical_cloud_requests_portal_check", data, condition)
        
        if result:
            print(f"Successfully updated Req_Id {req_id} to status '{new_status}'.")
            return True
        else:
            print(f"Failed to update Req_Id {req_id} to status '{new_status}'.")
            return False
    except Exception as e:
        print(f"Database update failed for Req_Id {req_id}: {e!r}")
        return False

# --- Helper functions for data parsing and saving (No changes needed here) ---

def parse_general_data(general_data_json):
    try:
        if isinstance(general_data_json, dict):
            flat_data = {key: json.dumps(value) if isinstance(value, (list, dict)) else value for key, value in general_data_json.items()}
            return pd.DataFrame(list(flat_data.items()), columns=['KEY', 'VALUE'])
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def parse_individual_data_list(individual_data_list_json):
    try:
        if isinstance(individual_data_list_json, list) and individual_data_list_json:
            return pd.json_normalize(individual_data_list_json)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def fetch_medical_data(request):
    req_data_json = json.loads(request.get('Req_Data', '{}')) if isinstance(request.get('Req_Data'), str) else request.get('Req_Data', {})
    general_data = parse_general_data(req_data_json.get('generalData', {}))
    individual_data = parse_individual_data_list(req_data_json.get('individualDataList', []))
    return general_data, individual_data

def clean_numeric_strings(value):
    try:
        float_val = float(str(value))
        return str(int(float_val)) if float_val.is_integer() else str(value)
    except (ValueError, TypeError):
        return str(value)

def save_to_excel(req_id, df_general, df_individual):
    file_path = os.path.join(ATTACHMENTS_SAVE_DIR, f"Medical__NBQ{req_id}.xlsx")
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Sheet2
        desired_columns = ["Category", "Company", "TPA", "Network"]
        existing_cols = [col for col in desired_columns if col in df_individual.columns]
        other_cols = [col for col in df_individual.columns if col not in existing_cols]
        df_individual_ordered = df_individual[existing_cols + other_cols].map(clean_numeric_strings)
        df_individual_ordered.to_excel(writer, sheet_name='Sheet2', index=False)
        
        # Sheet1
        if not df_general.empty:
            df_general['VALUE'] = df_general['VALUE'].apply(clean_numeric_strings)
            df_general.to_excel(writer, sheet_name='Sheet1', index=False)
        else:
            pd.DataFrame(columns=['KEY', 'VALUE']).to_excel(writer, sheet_name='Sheet1', index=False)
    print(f"Data saved to {file_path}")

# --- REFACTORED Main processing function ---

def process_next_pending_request():
    """
    Manages a single DB connection to fetch and process the next pending request.
    This is the main orchestrator function.
    
    Returns:
        int or None: The Req_Id of the processed request, or None if none found.
    """
    print("\nChecking for the next pending medical request...")
    db = None
    try:
        # 1. Establish one single connection for this entire process
        db = MySQLDatabase(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
        if not db.connect():
            print("Failed to establish main database connection.")
            return None

        # 2. Find the next request using the active connection
        request = fetch_first_pending_request(db)

        if not request:
            return None  # No request found

        req_id = request.get('Req_Id')
        print(f"\n--- Found request. Starting processing for Req_Id {req_id} ---")

        # 3. Update status using the active connection
        if not update_request_status(db, req_id, "In Progress"):
            print(f"Failed to update status for Req_Id {req_id}. Skipping this request.")
            return None

        # 4. Download all related files using the active connection
        process_download_cencus(db, req_id)
        process_download_tob(db, req_id)
        process_download_trade_license(db, req_id)

        # 5. Fetch, parse, and save the main data to its unique Excel file
        df_general, df_individual = fetch_medical_data(request)
        save_to_excel(req_id, df_general, df_individual)

        print(f"--- Initial processing complete for Req_Id {req_id}. Handing over to automation. ---")
        
        return req_id  # Return the ID for the main loop to use

    except Exception as e:
        print(f"An unexpected error occurred during request processing: {e!r}")
        return None
    finally:
        # 6. Ensure the single connection is closed no matter what
        if db and db.is_connected():
            db.disconnect()

