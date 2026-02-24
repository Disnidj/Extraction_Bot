"""
Upload Extracted Portal Data to Database
Handles batch upload with transaction support using staged comparison.

COMPLETE FLOW:
═══════════════════════════════════════════════════════════════════════════
1. EXTRACT & PARSE: Read extracted .txt files from portal extractions
2. MAP DROPDOWN NAMES: Convert portal-specific names → standard names (BEFORE staging)
   - Uses Medical_CTN_Portal_Field_Mapping table
   - Example: "Quotation For" → "Quotation_For", "Policy_Holder_Type" → "Quotation_For"
3. FILTER & VALIDATE: Remove unwanted dropdowns (SKIP_DROPDOWN_NAMES)
4. INSERT TO STAGING: Upload prepared data to Medical_CTN_Cascading_Dropdown_Staging
5. BACKUP ORIGINAL: Snapshot affected rows from Medical_CTN_Cascading_Dropdown_Lifecare
6. COMPARE: Staging ↔ Original (exact match detection)
7. APPLY CHANGES: Only INSERT/UPDATE/DELETE what changed
8. AUDIT TRAIL: Log all changes to Medical_CTN_Cascading_Dropdown_Audit
═══════════════════════════════════════════════════════════════════════════

KEY FEATURES:
- ✅ Mapping happens BEFORE staging upload (data already standardized)
- ✅ Only changed records are modified (unchanged data untouched)
- ✅ Detects whitespace and case differences
- ✅ Selective backup (only affected rows, 7-day retention)
- ✅ Full audit trail (permanent change history)
- ✅ Transaction safety (rollback on error)

NOTE: TPA/Network expansion is done in formatters when writing the txt file.
"""

import json
import os
import time
import traceback
from typing import List, Dict, Tuple, Set, Optional

from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

# Import from modular components
from .staging_upload import staged_upload_to_database
from .staging_models import ChangeReport
from .staging_config import (
    ORIGINAL_TABLE as TABLE_NAME,
    MAPPING_TABLE,
    BATCH_SIZE,
    ONLY_UPLOAD_MAPPED,
    SKIP_DROPDOWN_NAMES,
    standardize_company_name
)
from .staging_mapping_service import (
    load_dropdown_mappings,
    apply_dropdown_mapping,
    filter_skip_dropdowns,
    get_unique_dropdown_names
)


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


def upload_to_database(output_dir: str) -> Tuple[bool, int, str, dict, dict, Optional[ChangeReport]]:
    """
    Upload all extracted data to database using staged comparison.
    
    IMPORTANT: Dropdown name mapping happens in THIS function BEFORE staging upload.
    Data is inserted to staging table with ALREADY-MAPPED dropdown names.
    
    Detailed Process:
    ─────────────────────────────────────────────────────────────────────────
    PHASE 1: DATA PREPARATION (This Function)
        1. Collect all extracted .txt files
        2. Parse JSON records from files
        3. Standardize company names
        4. Load dropdown mappings from Medical_CTN_Portal_Field_Mapping
        5. Apply mappings: portal-specific names → standard names
        6. Filter unwanted dropdowns (SKIP_DROPDOWN_NAMES)
        7. Pass PREPARED DATA to staged_upload_to_database()
        
    PHASE 2: STAGED UPLOAD (staging_upload.py)
        8. Insert prepared data to STAGING table
        9. Backup affected rows from ORIGINAL table
        10. Compare STAGING ↔ ORIGINAL (direct comparison, no mapping needed)
        11. Detect changes (NEW/MODIFIED/DELETED)
        12. Apply only the changes to ORIGINAL table
        13. Log changes to AUDIT table
    ─────────────────────────────────────────────────────────────────────────
    
    Args:
        output_dir: Base output directory containing portal subdirectories
        
    Returns:
        Tuple of (success: bool, rows_changed: int, message: str, 
                  deletion_details: dict, mapping_details: dict, change_report: ChangeReport)
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
        return False, 0, "No extracted files found", {}, {}, None
    
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
        return False, 0, "No valid records found", {}, {}, None
    
    # Connect to database for loading mappings
    print("\n🔌 Connecting to database for mappings...")
    db = get_db_connection()
    if not db.connect():
        return False, 0, "Failed to connect to database", {}, {}, None
    
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
        
        # Build dropdown names by company for staged upload
        dropdown_names_by_company = {}
        for company in records_by_company.keys():
            company_dropdowns = set(
                r.get("Dropdown_Name", "") 
                for r in all_records 
                if r.get("Company") == company and r.get("Dropdown_Name", "")
            )
            dropdown_names_by_company[company] = company_dropdowns
        
        # Close the mapping connection - staged upload will create its own
        db.disconnect()
        
        # Use staged upload with comparison
        companies = list(records_by_company.keys())
        success, total_changes, upload_msg, change_report = staged_upload_to_database(
            all_records,
            companies,
            dropdown_names_by_company
        )
        
        # Calculate total duration
        upload_duration = time.time() - upload_start_time
        minutes = int(upload_duration // 60)
        seconds = upload_duration % 60
        
        # Build deletion details from change report (for backward compatibility)
        deletion_details = {}
        if change_report:
            changes_by_company = change_report.get_changes_by_company()
            for company in companies:
                if company in changes_by_company:
                    data = changes_by_company[company]
                    deletion_details[company] = {
                        'rows_deleted': len(data['deleted']),
                        'rows_modified': len(data['modified']),
                        'rows_inserted': len(data['new']),
                        'dropdown_names': sorted(dropdown_names_by_company.get(company, set()))
                    }
                else:
                    deletion_details[company] = {
                        'rows_deleted': 0,
                        'rows_modified': 0,
                        'rows_inserted': 0,
                        'dropdown_names': sorted(dropdown_names_by_company.get(company, set()))
                    }
        
        # Build mapping details for report
        inserted_dropdowns_by_company = {
            company: sorted(dropdown_names_by_company.get(company, set()))
            for company in companies
        }
        
        mapping_details = {
            'applied_mappings': all_applied_mappings,  # {company: {portal_name: db_name}}
            'unmapped_names': {k: list(v) for k, v in all_unmapped_names.items()},  # Convert sets to lists
            'only_mapped_mode': ONLY_UPLOAD_MAPPED,  # Whether only mapped dropdowns were uploaded
            'inserted_dropdown_names': inserted_dropdowns_by_company  # {company: [dropdown_names]}
        }
        
        if success:
            return True, total_changes, f"Successfully processed with {total_changes} changes in {minutes}m {seconds:.2f}s", deletion_details, mapping_details, change_report
        else:
            return False, 0, upload_msg, deletion_details, mapping_details, change_report
        
    except Exception as e:
        upload_duration = time.time() - upload_start_time
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print(f"   ⏱️  Duration before failure: {upload_duration:.2f}s")
        if db.connection:
            db.connection.rollback()
        return False, 0, f"Upload failed: {str(e)}", {}, {}, None
        
    finally:
        if db.is_connected():
            db.disconnect()


# =============================================================================
# LEGACY FUNCTION - DEPRECATED (Kept for manual testing only)
# =============================================================================
# WARNING: This function uses OLD upload logic (DELETE + INSERT)
# WITHOUT staging, backup, comparison, or audit trail.
# 
# For production use, always use upload_to_database() instead.
# This function is kept only for manual command-line testing.
# =============================================================================

def upload_single_file(file_path: str) -> Tuple[bool, int, str]:
    """
    [DEPRECATED] Upload a single extracted file to database with dropdown mapping.
    
    ⚠️ WARNING: This is LEGACY CODE using DELETE + INSERT approach!
    ⚠️ Does NOT use staging, backup, comparison, or audit trail.
    ⚠️ Use upload_to_database() for production instead.
    
    This function is kept only for manual testing via command line:
        python -m src.services.db_service.api_data.upload_extracted <file_path>
    
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
