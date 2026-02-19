"""
Upload Extracted Portal Data to Database
Handles batch upload with transaction support - delete old, insert new, rollback on error.

Includes dropdown name mapping from Medical_CTN_Portal_Field_Mapping table:
- Looks up portal-specific dropdown names (e.g., "Quotation For" from MaxHealth column)
- Maps to standard dropdown names (e.g., "Quotation_For" from Dropdown_Name column)

Note: TPA/Network expansion is done in the formatters when writing the txt file.
"""

import json
import os
import time
from typing import List, Dict, Tuple
from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD


# Table names
TABLE_NAME = "Medical_CTN_Cascading_Dropdown_Lifecare"
MAPPING_TABLE = "Medical_CTN_Portal_Field_Mapping"

# Batch size for inserts
BATCH_SIZE = 100

# Upload only records that have dropdown mappings in the database
# When True: Unmapped dropdowns are skipped (not uploaded) - recommended for clean data
# When False: All dropdowns are uploaded (mapped ones renamed, unmapped keep original names)
ONLY_UPLOAD_MAPPED = True

# Company name standardization mapping
# Maps formatter names to standard database names
COMPANY_NAME_MAPPING = {
    "Sukoon": "SUKOON INSURANCE",
    "Qatar": "QATAR INSURANCE CO",
    "Takaful": "TAKAFUL EMARAT",
    "ADNIC": "ADNIC",
    "MaxHealth": "MaxHealth",
    "Orient Aura": "Orient Aura",  # Orient Aura API extraction
    "NLGI Aura": "Liva Globalcare",  # NLGI Aura API extraction
    # Add other portals as needed
}


def standardize_company_name(company: str) -> str:
    """
    Standardize company name to match database naming convention.
    
    Args:
        company: Company name from extracted file
        
    Returns:
        Standardized company name
    """
    return COMPANY_NAME_MAPPING.get(company, company)


def get_db_connection() -> MySQLDatabase:
    """Create and return a database connection."""
    return MySQLDatabase(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)


def load_dropdown_mappings(db, company: str) -> Dict[str, str]:
    """
    Load dropdown name mappings from Medical_CTN_Portal_Field_Mapping.
    
    Maps portal-specific dropdown names to standard database names.
    Example: "Dental Benefit" (Liva Globalcare) -> "Dental" (standard)
    
    Args:
        db: Database connection
        company: Company/portal name (column name in mapping table)
        
    Returns:
        Dict mapping {portal_dropdown_name: standard_dropdown_name}
    """
    mappings = {}
    
    try:
        # Query to get mappings for this company
        # Column name is the company name (e.g., MaxHealth, Sukoon, Qatar, Liva Globalcare)
        query = f"""
            SELECT `{company}`, Dropdown_Name 
            FROM {MAPPING_TABLE}
            WHERE `{company}` IS NOT NULL AND `{company}` != ''
        """
        rows = db.fetch_all(query)
        
        if rows:
            for row in rows:
                # Try both exact column name and stripped version
                portal_name = row.get(company, "") or row.get(company.strip(), "")
                standard_name = row.get("Dropdown_Name", "")
                
                # Strip whitespace from both values
                if portal_name:
                    portal_name = portal_name.strip()
                if standard_name:
                    standard_name = standard_name.strip()
                    
                if portal_name and standard_name:
                    mappings[portal_name] = standard_name
                    
        print(f"   Loaded {len(mappings)} dropdown mappings for {company}")
        
    except Exception as e:
        print(f"   ⚠️ Could not load mappings for {company}: {e}")
        print(f"   → Will use original dropdown names")
        import traceback
        traceback.print_exc()
    
    return mappings


def apply_dropdown_mapping(records: List[Dict], mappings: Dict[str, str], only_mapped: bool = True) -> Tuple[List[Dict], int, int, Dict[str, str], set]:
    """
    Apply dropdown name mappings to records.
    
    Args:
        records: List of record dictionaries
        mappings: Dict mapping {portal_dropdown_name: standard_dropdown_name}
        only_mapped: If True, return only records that have a mapping (skip unmapped)
        
    Returns:
        Tuple of (filtered_records, mapped_count, unmapped_count, applied_mappings, unmapped_names)
        - filtered_records: Records to upload (only mapped if only_mapped=True)
        - mapped_count: Number of records that were mapped
        - unmapped_count: Number of records that were not mapped
        - applied_mappings: Dict of {portal_name: db_name} that were actually applied
        - unmapped_names: Set of dropdown names that had no mapping
    """
    mapped_records = []
    unmapped_records = []
    unmapped_names = set()
    applied_mappings = {}  # Track which mappings were actually used
    
    for record in records:
        original_name = record.get("Dropdown_Name", "")
        # Try with stripped value
        original_name_stripped = original_name.strip() if original_name else ""
        
        if original_name in mappings:
            new_name = mappings[original_name]
            record["Dropdown_Name"] = new_name
            mapped_records.append(record)
            # Track the mapping (only add once per unique original name)
            if original_name not in applied_mappings:
                applied_mappings[original_name] = new_name
        elif original_name_stripped in mappings:
            new_name = mappings[original_name_stripped]
            record["Dropdown_Name"] = new_name
            mapped_records.append(record)
            if original_name_stripped not in applied_mappings:
                applied_mappings[original_name_stripped] = new_name
        else:
            unmapped_records.append(record)
            unmapped_names.add(original_name)
    
    # Return only mapped records if only_mapped is True
    if only_mapped:
        return mapped_records, len(mapped_records), len(unmapped_records), applied_mappings, unmapped_names
    else:
        # Return all records (mapped ones have been renamed, unmapped keep original names)
        return mapped_records + unmapped_records, len(mapped_records), len(unmapped_records), applied_mappings, unmapped_names


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
    3. Load dropdown name mappings for each company
    4. Apply mappings to convert portal names to standard names
    5. Delete old data for affected companies (in transaction)
    6. Insert new data in batches (in transaction)
    7. Commit on success, rollback on any error
    
    Args:
        output_dir: Base output directory containing portal subdirectories
        
    Returns:
        Tuple of (success: bool, rows_inserted: int, message: str, deletion_details: dict)
    """
    upload_start_time = time.time()
    
    print("\n" + "=" * 70)
    print("📤 DATABASE UPLOAD STARTED")
    print("=" * 70)
    print(f"   Database: {DB_NAME}")
    print(f"   Table: {TABLE_NAME}")
    print(f"   Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Collect files
    print("\n📁 Collecting extracted files...")
    extracted_files = collect_extracted_files(output_dir)
    if not extracted_files:
        return False, 0, "No extracted files found", {}
    
    print(f"   Found {len(extracted_files)} file(s)")
    for portal, filepath in extracted_files:
        print(f"   • {portal}: {os.path.basename(filepath)}")
    
    # Parse all records and group by company
    print("\n📖 Parsing extracted data...")
    records_by_company = {}  # {company: [records]}
    all_dropdown_names_by_company = {}  # Track unique dropdown names per company
    
    for portal_name, file_path in extracted_files:
        records = parse_extracted_file(file_path)
        for record in records:
            company = record.get("Company", "")
            if company:
                # Standardize company name to match database naming convention
                standardized_company = standardize_company_name(company)
                record["Company"] = standardized_company  # Update record with standardized name
                
                if standardized_company not in records_by_company:
                    records_by_company[standardized_company] = []
                    all_dropdown_names_by_company[standardized_company] = set()
                records_by_company[standardized_company].append(record)
                dropdown_name = record.get("Dropdown_Name", "")
                if dropdown_name:
                    all_dropdown_names_by_company[standardized_company].add(dropdown_name)
    
    total_records = sum(len(recs) for recs in records_by_company.values())
    print(f"   Total records: {total_records}")
    print(f"   Companies: {', '.join(records_by_company.keys())}")
    
    if not records_by_company:
        return False, 0, "No valid records found", {}
    
    # Connect to database
    print("\n🔌 Connecting to database...")
    db = get_db_connection()
    if not db.connect():
        return False, 0, "Failed to connect to database"
    
    try:
        # Load and apply dropdown mappings for each company
        print("\n" + "-" * 70)
        print("🔄 DROPDOWN MAPPING SUMMARY")
        print("-" * 70)
        all_records = []
        total_mapped = 0
        total_unmapped = 0
        all_applied_mappings = {}  # {company: {portal_name: db_name}}
        all_unmapped_names = {}    # {company: set of unmapped names}
        
        # Dropdown names to skip (hierarchy fields and unwanted fields)
        # Keep TPA and Network out of the insert batch (they are handled separately)
        SKIP_DROPDOWN_NAMES = {"", "TPA", "Network"}
        
        for company, records in records_by_company.items():
            print(f"\n   📋 {company}:")
            print(f"      • Total records from file: {len(records)}")
            print(f"      • Unique dropdown fields: {len(all_dropdown_names_by_company[company])}")
            
            # Filter out unwanted dropdown names FIRST (before mapping)
            filtered_records = [
                r for r in records 
                if r.get("Dropdown_Name", "") not in SKIP_DROPDOWN_NAMES
            ]
            skipped = len(records) - len(filtered_records)
            if skipped > 0:
                print(f"      • Skipped {skipped} rows (empty/unwanted fields)")
            
            # Apply mapping only to filtered records
            mappings = load_dropdown_mappings(db, company)
            if mappings:
                # Use ONLY_UPLOAD_MAPPED to control whether unmapped records are included
                records_to_upload, mapped, unmapped, applied_mappings, unmapped_names = apply_dropdown_mapping(
                    filtered_records, mappings, only_mapped=ONLY_UPLOAD_MAPPED
                )
                total_mapped += mapped
                total_unmapped += unmapped
                all_applied_mappings[company] = applied_mappings
                all_unmapped_names[company] = unmapped_names
                
                if ONLY_UPLOAD_MAPPED:
                    print(f"      • Mapped: {mapped} records → TO BE UPLOADED")
                    print(f"      • Unmapped: {unmapped} records → SKIPPED (not in mapping table)")
                else:
                    print(f"      • Mapped: {mapped}, Unmapped: {unmapped}")
            else:
                print(f"      • No mappings found - SKIPPING all records for {company}")
                all_applied_mappings[company] = {}
                all_unmapped_names[company] = set(r.get("Dropdown_Name", "") for r in filtered_records)
                records_to_upload = [] if ONLY_UPLOAD_MAPPED else filtered_records
            
            # Note: TPA/Network expansion is now done in the formatter when writing the txt file
            # No need to expand here anymore
            
            all_records.extend(records_to_upload)
        
        # Get unique dropdown names being inserted
        unique_dropdowns = set(r.get("Dropdown_Name", "") for r in all_records if r.get("Dropdown_Name", ""))
        
        # Display mapping details per company
        print(f"\n   {'='*70}")
        print(f"   📊 DROPDOWN MAPPING DETAILS")
        print(f"   {'='*70}")
        
        for company, applied_mappings in all_applied_mappings.items():
            if applied_mappings:
                print(f"\n   🏢 {company} - Applied Mappings ({len(applied_mappings)}):")
                print(f"      {'Portal Field Name':<45} → {'Database Field Name':<30}")
                print(f"      {'-'*45}   {'-'*30}")
                for portal_name, db_name in sorted(applied_mappings.items()):
                    # Truncate long names for display
                    portal_display = (portal_name[:42] + '...') if len(portal_name) > 45 else portal_name
                    db_display = (db_name[:27] + '...') if len(db_name) > 30 else db_name
                    print(f"      {portal_display:<45} → {db_display:<30}")
            else:
                print(f"\n   🏢 {company} - No mappings applied")
            
            # Show unmapped names (limited to first 10)
            unmapped = all_unmapped_names.get(company, set())
            if unmapped:
                skip_status = "SKIPPED" if ONLY_UPLOAD_MAPPED else "uploaded with original names"
                print(f"\n      ⚠️ Unmapped fields ({len(unmapped)}) - {skip_status}:")
                for i, name in enumerate(sorted(unmapped)[:10]):
                    name_display = (name[:60] + '...') if len(name) > 60 else name
                    print(f"         • {name_display}")
                if len(unmapped) > 10:
                    print(f"         ... and {len(unmapped) - 10} more")
        
        print(f"\n   {'='*70}")
        print(f"   📊 MAPPING TOTALS:")
        print(f"      • Mode: {'ONLY MAPPED DROPDOWNS' if ONLY_UPLOAD_MAPPED else 'ALL DROPDOWNS'}")
        print(f"      • Total mapped records: {total_mapped}")
        print(f"      • Total unmapped records: {total_unmapped}" + (" (SKIPPED)" if ONLY_UPLOAD_MAPPED else ""))
        print(f"      • Records to upload: {len(all_records)}")
        print(f"      • Unique dropdown fields to insert: {len(unique_dropdowns)}")
        if ONLY_UPLOAD_MAPPED:
            print(f"      ℹ️  Note: Only mapped dropdowns will be uploaded and deleted")
        print(f"   {'='*70}")
        
        db.connection.autocommit = False  # Start transaction
        
        # Delete old data by Company + Dropdown_Name (after mapping)
        print(f"\n🗑️ Deleting old data by Company + Dropdown Names...")
        total_deleted = 0
        deletion_details = {}  # Track deletion info per company
        
        for company in records_by_company.keys():
            # Get unique dropdown names for this company (AFTER mapping)
            company_records = [r for r in all_records if r.get("Company") == company]
            dropdown_names_to_delete = set(
                r.get("Dropdown_Name", "") 
                for r in company_records 
                if r.get("Dropdown_Name", "")
            )
            
            if not dropdown_names_to_delete:
                print(f"   • {company}: No dropdown names to delete")
                deletion_details[company] = {
                    'rows_deleted': 0,
                    'dropdown_names': []
                }
                continue
            
            # Build DELETE query with IN clause
            placeholders = ', '.join(['%s'] * len(dropdown_names_to_delete))
            delete_query = f"""
                DELETE FROM {TABLE_NAME} 
                WHERE Company = %s 
                AND Dropdown_Name IN ({placeholders})
            """
            
            # Execute deletion
            params = [company] + list(dropdown_names_to_delete)
            db.cursor.execute(delete_query, params)
            deleted = db.cursor.rowcount
            total_deleted += deleted
            
            # Store deletion details
            deletion_details[company] = {
                'rows_deleted': deleted,
                'dropdown_names': sorted(dropdown_names_to_delete)
            }
            
            print(f"   • {company}: {deleted} rows deleted")
            print(f"      Dropdown names: {', '.join(sorted(dropdown_names_to_delete))}")
        
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
        
        # Calculate duration
        upload_duration = time.time() - upload_start_time
        minutes = int(upload_duration // 60)
        seconds = upload_duration % 60
        
        print(f"\n" + "=" * 70)
        print(f"✅ DATABASE UPLOAD COMPLETED SUCCESSFULLY")
        print(f"=" * 70)
        print(f"   📊 FINAL SUMMARY:")
        print(f"      • Mode: {'ONLY MAPPED DROPDOWNS' if ONLY_UPLOAD_MAPPED else 'ALL DROPDOWNS'}")
        print(f"      • Companies processed: {len(records_by_company)}")
        print(f"      • Total rows deleted: {total_deleted}")
        print(f"      • Total rows inserted: {rows_inserted}")
        print(f"      • Unique dropdown fields: {len(unique_dropdowns)}")
        if ONLY_UPLOAD_MAPPED:
            print(f"      ℹ️  Note: Only mapped dropdowns were uploaded/deleted")
        
        # Show inserted dropdown names per company
        print(f"\n   📋 INSERTED DROPDOWN NAMES:")
        for company in records_by_company.keys():
            company_dropdowns = set(
                r.get("Dropdown_Name", "") 
                for r in all_records 
                if r.get("Company") == company and r.get("Dropdown_Name", "")
            )
            if company_dropdowns:
                print(f"      🏢 {company}: {', '.join(sorted(company_dropdowns))}")
            else:
                print(f"      🏢 {company}: None")
        
        print(f"\n   ⏱️  Duration: {minutes}m {seconds:.2f}s")
        print(f"   🕐 End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"=" * 70)
        
        # Build mapping details for report
        # Include inserted dropdown names per company for the report
        inserted_dropdowns_by_company = {}
        for company in records_by_company.keys():
            company_dropdowns = set(
                r.get("Dropdown_Name", "") 
                for r in all_records 
                if r.get("Company") == company and r.get("Dropdown_Name", "")
            )
            inserted_dropdowns_by_company[company] = sorted(company_dropdowns)
        
        mapping_details = {
            'applied_mappings': all_applied_mappings,  # {company: {portal_name: db_name}}
            'unmapped_names': {k: list(v) for k, v in all_unmapped_names.items()},  # Convert sets to lists
            'only_mapped_mode': ONLY_UPLOAD_MAPPED,  # Whether only mapped dropdowns were uploaded
            'inserted_dropdown_names': inserted_dropdowns_by_company  # {company: [dropdown_names]}
        }
        
        return True, rows_inserted, f"Successfully uploaded {rows_inserted} records in {minutes}m {seconds:.2f}s", deletion_details, mapping_details
        
    except Exception as e:
        upload_duration = time.time() - upload_start_time
        print(f"\n❌ ERROR: {e}")
        print("🔄 Rolling back transaction...")
        print(f"   ⏱️  Duration before failure: {upload_duration:.2f}s")
        if db.connection:
            db.connection.rollback()
        return False, 0, f"Upload failed: {str(e)}", {}, {}
        
    finally:
        db.disconnect()


def upload_single_file(file_path: str) -> Tuple[bool, int, str]:
    """
    Upload a single extracted file to database with dropdown mapping.
    
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
    
    # Get company name from first record and standardize it
    company = records[0].get("Company", "")
    if not company:
        return False, 0, "Company name not found in records"
    
    # Standardize company name to match database naming convention
    standardized_company = standardize_company_name(company)
    print(f"   Company: {standardized_company}")
    print(f"   Records: {len(records)}")
    
    # Update all records with standardized company name
    for record in records:
        record["Company"] = standardized_company
    
    # Connect to database
    db = get_db_connection()
    if not db.connect():
        return False, 0, "Failed to connect to database"
    
    try:
        # Load and apply dropdown mappings
        print("\n🔄 Loading dropdown name mappings...")
        mappings = load_dropdown_mappings(db, company)
        if mappings:
            mapped, unmapped = apply_dropdown_mapping(records, mappings)
            print(f"   Mapped: {mapped}, Unmapped: {unmapped}")
        else:
            print(f"   No mappings found, using original names")
        
        # Note: TPA/Network expansion is now done in the formatter when writing the txt file
        # No need to expand here anymore
        
        db.connection.autocommit = False
        
        # Delete old data by Company + Dropdown_Name (after mapping)
        dropdown_names_to_delete = set(
            r.get("Dropdown_Name", "") 
            for r in records 
            if r.get("Dropdown_Name", "")
        )
        
        if dropdown_names_to_delete:
            placeholders = ', '.join(['%s'] * len(dropdown_names_to_delete))
            delete_query = f"""
                DELETE FROM {TABLE_NAME} 
                WHERE Company = %s 
                AND Dropdown_Name IN ({placeholders})
            """
            params = [standardized_company] + list(dropdown_names_to_delete)
            db.cursor.execute(delete_query, params)
            deleted = db.cursor.rowcount
            print(f"   Deleted {deleted} old rows for {standardized_company}")
            print(f"   Dropdown names: {', '.join(sorted(dropdown_names_to_delete))}")
        else:
            print(f"   No dropdown names to delete for {standardized_company}")
        
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
