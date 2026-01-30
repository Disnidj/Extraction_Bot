"""
Upload Extracted Portal Data to Database
Handles batch upload with transaction support - delete old, insert new, rollback on error.
"""

import json
import os
from typing import List, Dict, Tuple
from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD


# Table name for portal dropdowns
TABLE_NAME = "Medical_CTN_Cascading_Dropdown_Lifecare"

# Batch size for inserts
BATCH_SIZE = 100


def get_db_connection() -> MySQLDatabase:
    """Create and return a database connection."""
    return MySQLDatabase(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)


def parse_extracted_file(file_path: str) -> List[Dict]:
    """Parse an extracted .txt file into a list of records."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"   ⚠️ Skipping invalid JSON at line {line_num}: {e}")
    return records


def collect_extracted_files(output_dir: str) -> List[Tuple[str, str]]:
    """Collect all extracted .txt files from the output directory."""
    files = []
    if not os.path.exists(output_dir):
        return files
    
    for portal_name in os.listdir(output_dir):
        portal_dir = os.path.join(output_dir, portal_name)
        if not os.path.isdir(portal_dir):
            continue
        for filename in os.listdir(portal_dir):
            if "_extracted_" in filename and filename.endswith(".txt"):
                files.append((portal_name, os.path.join(portal_dir, filename)))
    return files


def upload_to_database(output_dir: str) -> Tuple[bool, int, str]:
    """
    Upload all extracted data to database with transaction support.
    
    Process:
    1. Collect all extracted files
    2. Parse all records  
    3. Delete old data for affected companies (in transaction)
    4. Insert new data in batches (in transaction)
    5. Commit on success, rollback on any error
    
    Args:
        output_dir: Base output directory containing portal subdirectories
        
    Returns:
        Tuple of (success: bool, rows_inserted: int, message: str)
    """
    print("\n" + "=" * 60)
    print("📤 UPLOADING TO DATABASE")
    print("=" * 60)
    print(f"   Database: {DB_NAME}")
    print(f"   Table: {TABLE_NAME}")
    
    # Collect files
    print("\n📁 Collecting extracted files...")
    extracted_files = collect_extracted_files(output_dir)
    if not extracted_files:
        return False, 0, "No extracted files found"
    
    print(f"   Found {len(extracted_files)} file(s)")
    for portal, filepath in extracted_files:
        print(f"   • {portal}: {os.path.basename(filepath)}")
    
    # Parse all records
    print("\n📖 Parsing extracted data...")
    all_records = []
    companies_found = set()
    
    for portal_name, file_path in extracted_files:
        records = parse_extracted_file(file_path)
        all_records.extend(records)
        for record in records:
            if record.get("Company"):
                companies_found.add(record["Company"])
    
    print(f"   Total records: {len(all_records)}")
    print(f"   Companies: {', '.join(companies_found)}")
    
    if not all_records:
        return False, 0, "No valid records found"
    
    # Connect to database
    print("\n🔌 Connecting to database...")
    db = get_db_connection()
    if not db.connect():
        return False, 0, "Failed to connect to database"
    
    try:
        db.connection.autocommit = False  # Start transaction
        
        # Delete old data for affected companies only
        print(f"\n🗑️ Deleting old data for: {', '.join(companies_found)}")
        for company in companies_found:
            db.cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE Company = %s", (company,))
            print(f"   • {company}: {db.cursor.rowcount} rows deleted")
        
        # Insert new data in batches
        print(f"\n📥 Inserting {len(all_records)} new records...")
        insert_query = f"""
            INSERT INTO {TABLE_NAME} 
            (Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        rows_inserted = 0
        batch = []
        
        for record in all_records:
            batch.append((
                record.get("Broker_ID", 0),
                record.get("Company", ""),
                record.get("TPA", ""),
                record.get("Network", ""),
                record.get("Region", ""),
                record.get("Dropdown_Name", ""),
                record.get("Selection_Value", "")
            ))
            
            if len(batch) >= BATCH_SIZE:
                db.cursor.executemany(insert_query, batch)
                rows_inserted += len(batch)
                print(f"   Inserted {rows_inserted} / {len(all_records)} rows...")
                batch = []
        
        if batch:
            db.cursor.executemany(insert_query, batch)
            rows_inserted += len(batch)
        
        # Commit transaction
        db.connection.commit()
        print(f"\n✅ SUCCESS: {rows_inserted} rows inserted")
        print("=" * 60)
        
        return True, rows_inserted, f"Successfully uploaded {rows_inserted} records"
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("🔄 Rolling back transaction...")
        if db.connection:
            db.connection.rollback()
        return False, 0, f"Upload failed: {str(e)}"
        
    finally:
        db.disconnect()


def upload_single_file(file_path: str) -> Tuple[bool, int, str]:
    """
    Upload a single extracted file to database.
    
    Args:
        file_path: Path to the extracted .txt file
        
    Returns:
        Tuple of (success: bool, rows_inserted: int, message: str)
    """
    print(f"\n📤 Uploading: {os.path.basename(file_path)}")
    print(f"   Database: {DB_NAME}")
    print(f"   Table: {TABLE_NAME}")
    
    # Parse records
    records = parse_extracted_file(file_path)
    if not records:
        return False, 0, "No valid records found"
    
    # Get company name from first record
    company = records[0].get("Company", "")
    if not company:
        return False, 0, "Company name not found in records"
    
    print(f"   Company: {company}")
    print(f"   Records: {len(records)}")
    
    # Connect to database
    db = get_db_connection()
    if not db.connect():
        return False, 0, "Failed to connect to database"
    
    try:
        db.connection.autocommit = False
        
        # Delete old data for this company only
        db.cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE Company = %s", (company,))
        deleted = db.cursor.rowcount
        print(f"   Deleted {deleted} old rows for {company}")
        
        # Insert new data
        insert_query = f"""
            INSERT INTO {TABLE_NAME} 
            (Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        values = [
            (
                r.get("Broker_ID", 0),
                r.get("Company", ""),
                r.get("TPA", ""),
                r.get("Network", ""),
                r.get("Region", ""),
                r.get("Dropdown_Name", ""),
                r.get("Selection_Value", "")
            )
            for r in records
        ]
        
        db.cursor.executemany(insert_query, values)
        rows_inserted = len(values)
        
        db.connection.commit()
        print(f"   ✅ Inserted {rows_inserted} rows")
        
        return True, rows_inserted, f"Uploaded {rows_inserted} records for {company}"
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        if db.connection:
            db.connection.rollback()
        return False, 0, str(e)
        
    finally:
        db.disconnect()


# For command line testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            success, count, msg = upload_single_file(file_path)
            print(f"\nResult: {msg}")
        else:
            print(f"File not found: {file_path}")
    else:
        print("Usage: python -m src.services.db_service.upload_extracted <file_path>")
