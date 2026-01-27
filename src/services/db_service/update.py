import sqlite3
from src.utils.load_yaml import DATABASE_PATH
from datetime import datetime

def update_last_check_datetime(referral_id):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Format the current datetime to 'YYYY-MM-DD HH:MM:SS'
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            "UPDATE process_records SET last_checked = ? WHERE iq_quotation_no = ?",
            (current_time, referral_id)
        )
        conn.commit()
    except Exception as e:
        print(f"Error updating last check time: {e}")
    finally:
        if conn:
            conn.close()

def update_iq_quotation_status(app_key, iq_quotation_no, iq_status, final_status):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Use placeholders (?) for parameters to prevent SQL injection
        cursor.execute(
            "UPDATE process_records SET iq_quotation_no=?, iq_status=?, final_status=? WHERE app_key=?",
            (iq_quotation_no, iq_status, final_status, app_key)
        )
        
        conn.commit()
        print(f"Successfully updated referral status for app_key {app_key}")
    
    except Exception as e:
        print(f"Error updating referral status: {e}")
    
    finally:
        if conn:
            conn.close()

def update_iq_status(iq_quotation_no, iq_status):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE process_records SET iq_status=? WHERE iq_quotation_no=?",
            (iq_status, iq_quotation_no)
        )
        
        conn.commit()
        print(f"Successfully updated IQ status for IQ Quotation No {iq_quotation_no}")
    
    except Exception as e:
        print(f"Error updating IQ status: {e}")
    
    finally:
        if conn:
            conn.close()

def update_final_status(key, final_status, type):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        if type == 'app_key':
            cursor.execute(
                "UPDATE process_records SET final_status=? WHERE app_key=?",
                (final_status, key)
            )
        elif type == 'iq_quotation_no':
            cursor.execute(
                "UPDATE process_records SET final_status=? WHERE iq_quotation_no=?",
                (final_status, key)
            )
        
        conn.commit()
        print(f"Successfully updated final status for key {key}")
    
    except Exception as e:
        print(f"Error updating final status: {e}")
    
    finally:
        if conn:
            conn.close()