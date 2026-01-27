import sqlite3
from src.utils.load_yaml import DATABASE_PATH
from src.utils.enums import Final_Status

def read_pending_referrals():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Prepare the SQL statement for selecting the pending referrals
        sql = "SELECT * FROM process_records WHERE final_status = ?"
        
        # Execute the SQL statement
        cursor.execute(sql, (Final_Status.PENDING.value,))
        
        # Fetch the results
        pending_referrals = cursor.fetchall()
        
        # Commit the transaction
        conn.commit()
        
        return pending_referrals
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Close the connection
        if conn:
            conn.close()


