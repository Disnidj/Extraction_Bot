import base64
import os
from src.utils.load_yaml import ATTACHMENTS_SAVE_DIR

def save_base64_to_file(base64_string, output_file_path):
    try:
        file_data = base64.b64decode(base64_string)
        with open(output_file_path, 'wb') as file:
            file.write(file_data)
        print(f"File saved successfully as {output_file_path}")
    except Exception as e:
        print(f"An error occurred while saving the file {output_file_path}: {e}")

def fetch_request_from_db(db, req_id):
    """Fetches a request using an existing database connection."""
    try:
        query = "SELECT * FROM medical_cloud_requests_portal_check WHERE Req_Id = %s"
        request = db.fetch_one(query, (req_id,))
        if not request:
            print(f"No request found with Req_Id {req_id}")
            return None
        return request
    except Exception as e:
        print(f"Database query failed for Req_Id {req_id}: {e}")
        return None

def process_download_cencus(db, req_id):
    """Downloads Census_Data using an existing DB connection."""
    request = fetch_request_from_db(db, req_id)
    if request:
        census_data = request.get('Census_Data')
        if census_data:
            output_folder = ATTACHMENTS_SAVE_DIR
            os.makedirs(output_folder, exist_ok=True)
            output_file_path = os.path.join(output_folder, f"MemberUpload.xlsx")
            save_base64_to_file(census_data, output_file_path)
        else:
            print("No Census_Data found for the given request.")

def process_download_tob(db, req_id):
    """Downloads TOB using an existing DB connection."""
    request = fetch_request_from_db(db, req_id)
    if request:
        tob_data = request.get('TOB')
        if tob_data:
            output_folder = ATTACHMENTS_SAVE_DIR
            os.makedirs(output_folder, exist_ok=True)
            output_file_path = os.path.join(output_folder, f"tob.pdf")
            save_base64_to_file(tob_data, output_file_path)
        else:
            print("No TOB found for the given request.")

def process_download_trade_license(db, req_id):
    """Downloads Trade_License_Doc using an existing DB connection."""
    request = fetch_request_from_db(db, req_id)
    if request:
        trade_license_data = request.get('Trade_License_Doc')
        if trade_license_data:
            output_folder = ATTACHMENTS_SAVE_DIR
            os.makedirs(output_folder, exist_ok=True)
            output_file_path = os.path.join(output_folder, f"Trade_License.pdf")
            save_base64_to_file(trade_license_data, output_file_path)
        else:
            print("No Trade License found for the given request.")
