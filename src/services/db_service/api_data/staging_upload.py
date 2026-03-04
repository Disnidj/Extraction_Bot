"""
Staging Upload Service - Compare and Sync Portal Data with Change Detection

═══════════════════════════════════════════════════════════════════════════
IMPORTANT: This module receives ALREADY-MAPPED data from upload_extracted.py
Dropdown names are already converted to standard names BEFORE reaching here.
═══════════════════════════════════════════════════════════════════════════

COMPLETE DATA FLOW (From Extraction to Database):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: EXTRACTION & PREPARATION (upload_extracted.py)                 │
└─────────────────────────────────────────────────────────────────────────┘
  [Portal APIs] → Extract dropdown data
       ↓
  [Parse .txt files] → Load JSON records
       ↓
  [Standardize company names] → "SUKOON INSURANCE"
       ↓
  [Load mapping table] → Medical_CTN_Portal_Field_Mapping
       ↓
  [Map dropdown names] ← CRITICAL STEP!
       Portal name → Standard name
       "Quotation For" → "Quotation_For"
       "Policy_Holder_Type" → "Quotation_For"
       ↓
  [Filter unwanted dropdowns] → SKIP_DROPDOWN_NAMES
       ↓
  [Pass to staging_upload.py] → MAPPED DATA READY
  
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: STAGING & COMPARISON (THIS MODULE - staging_upload.py)         │
└─────────────────────────────────────────────────────────────────────────┘

  STEP 1: Cleanup Old Backups
  ┌──────────────────────────────────────┐
  │ DELETE FROM Backup_Table             │ ← Remove backups > 28 days
  │ WHERE Backup_Date < (NOW - 28 days)  │
  └──────────────────────────────────────┘
  
  STEP 2: Backup Original Data (FULL TABLE)
  ┌──────────────────────────────────────┐
  │ SELECT * FROM Original_Table         │ ← Current state snapshot
  │         ↓                            │
  │ INSERT INTO Backup_Table             │ ← 28-day retention
  │                                       │
  │ + Full file backup (.sql/.csv)       │ ← 30-day retention
  └──────────────────────────────────────┘
  
  STEP 3: Upload to Staging
  ┌──────────────────────────────────────┐
  │ DELETE FROM Staging_Table            │ ← Clear old data
  │         ↓                            │
  │ INSERT INTO Staging_Table            │ ← New data (already mapped!)
  │ • Broker_ID                          │
  │ • Company (standardized)              │
  │ • TPA                                │
  │ • Network                            │
  │ • Region                             │
  │ • Dropdown_Name (MAPPED!)            │ ← Not portal-specific anymore
  │ • Selection_Value                     │
  │ • Run_ID (20260223_141939)           │
  └──────────────────────────────────────┘
  
  STEP 4: Compare (DIRECT - No Mapping Needed!)
  ┌──────────────────────────────────────┐
  │ Staging_Table ↔ Original_Table       │
  │                                       │
  │ Match on:                            │
  │   (Company, TPA, Network, Region,    │
  │    Dropdown_Name, Selection_Value)   │
  │                                       │
  │ Detect:                              │
  │   🆕 NEW: In staging only            │
  │   ♻️ MODIFIED: Different value       │
  │   🗑️ DELETED: In original only       │
  │   ✅ UNCHANGED: Exact match          │
  └──────────────────────────────────────┘
  
  STEP 5: Apply Changes
  ┌──────────────────────────────────────┐
  │ Original_Table                       │
  │   ↓                                  │
  │ • INSERT new values                  │
  │ • UPDATE modified dropdown names     │
  │ • DELETE removed values              │
  └──────────────────────────────────────┘
  
  STEP 6: Audit Trail
  ┌──────────────────────────────────────┐
  │ INSERT INTO Audit_Table              │ ← Permanent history
  │ • Run_ID                             │
  │ • Change_Type (INSERT/UPDATE/DELETE) │
  │ • Company                            │
  │ • Dropdown_Name                      │
  │ • Old_Value                          │
  │ • New_Value                          │
  │ • Changed_At (timestamp)             │
  └──────────────────────────────────────┘
  
  STEP 7: Commit
  ┌──────────────────────────────────────┐
  │ • Keep staging data (until next run) │
  │ • COMMIT transaction ✅              │
  └──────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TABLE ROLES:
─────────────────────────────────────────────────────────────────────────
┌─────────────────────┬──────────────────┬──────────────────────────────┐
│ Table               │ Purpose          │ When Cleared                 │
├─────────────────────┼──────────────────┼──────────────────────────────┤
│ Staging             │ Temp workspace   │ At START of next run         │
│ Original (Lifecare) │ Live production  │ Never (only updated)         │
│ Backup              │ Safety snapshot  │ After 28 days                │
│ Audit               │ Change history   │ Never (permanent)            │
│ Mapping             │ Name translator  │ Never (reference data)       │
└─────────────────────┴──────────────────┴──────────────────────────────┘

KEY FEATURES:
- ✅ Receives pre-mapped data (no additional mapping needed)
- ✅ Exact match comparison (whitespace-sensitive)
- ✅ Full table backup (entire original table)
- ✅ Full audit trail (permanent change history)
- ✅ Transaction safety (rollback on error)
"""

import time
import traceback
import os
import csv
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Set

from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

# Import from modular components
from .staging_config import (
    ORIGINAL_TABLE, STAGING_TABLE, BACKUP_TABLE, AUDIT_TABLE,
    BACKUP_RETENTION_DAYS, BATCH_SIZE,
    ENABLE_FULL_TABLE_BACKUP, FULL_BACKUP_FORMAT, FULL_BACKUP_DIR, FULL_BACKUP_RETENTION_DAYS
)
from .staging_models import ChangeRecord, ChangeReport
from .staging_comparison_utils import highlight_difference, format_value_for_display


# =============================================================================
# MAIN STAGING UPLOADER CLASS
# =============================================================================

class StagingUploader:
    """
    Handles staged database uploads with comparison and audit trail.
    
    Usage:
        uploader = StagingUploader()
        success, report, message = uploader.process_upload(records, companies)
    """
    
    def __init__(self):
        self.db: Optional[MySQLDatabase] = None
        self.run_id: str = ""
    
    def _connect(self) -> bool:
        """Establish database connection."""
        self.db = MySQLDatabase(
            host=DB_HOST, 
            database=DB_NAME, 
            user=DB_USER, 
            password=DB_PASSWORD
        )
        return self.db.connect()
    
    def _disconnect(self):
        """Close database connection."""
        if self.db:
            self.db.disconnect()
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID for this upload session."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _execute(self, query: str, params: tuple = None) -> int:
        """Execute a query and return affected row count."""
        try:
            self.db.cursor.execute(query, params or ())
            return self.db.cursor.rowcount
        except Exception as e:
            print(f"   ❌ Query error: {e}")
            raise
    
    def _execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute many queries and return total affected row count."""
        try:
            self.db.cursor.executemany(query, params_list)
            return len(params_list)
        except Exception as e:
            print(f"   ❌ Batch query error: {e}")
            raise
    
    def _fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """Fetch all rows from a SELECT query."""
        try:
            self.db.cursor.execute(query, params or ())
            return self.db.cursor.fetchall()
        except Exception as e:
            print(f"   ❌ Fetch error: {e}")
            raise
    
    # =========================================================================
    # FULL TABLE BACKUP (SQL Dump & CSV Export)
    # =========================================================================
    
    def create_full_table_backup(self) -> Tuple[bool, Optional[str]]:
        """
        Create a complete backup of the original table as file(s).
        
        This is in ADDITION to the full backup to BACKUP_TABLE (database table).
        Use this for disaster recovery - can restore entire table from file.
        
        Backup formats:
        - SQL: Complete mysqldump file (.sql) - can restore with mysql command
        - CSV: Readable CSV file (.csv) - can open in Excel/import easily
        
        Returns:
            Tuple of (success: bool, backup_file_path: str or None)
        """
        if not ENABLE_FULL_TABLE_BACKUP:
            return True, None
        
        print(f"\n💾 Creating full table backup file...")
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(os.getcwd(), FULL_BACKUP_DIR)
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        success = True
        backup_files = []
        
        try:
            # SQL Dump backup
            if FULL_BACKUP_FORMAT in ['sql', 'both']:
                sql_file = self._create_sql_dump(backup_dir, timestamp)
                if sql_file:
                    backup_files.append(sql_file)
                else:
                    success = False
            
            # CSV Export backup
            if FULL_BACKUP_FORMAT in ['csv', 'both']:
                csv_file = self._create_csv_export(backup_dir, timestamp)
                if csv_file:
                    backup_files.append(csv_file)
                else:
                    success = False
            
            # Cleanup old backup files
            self._cleanup_old_backup_files(backup_dir)
            
            if backup_files:
                print(f"   ✓ Full backup created: {', '.join([os.path.basename(f) for f in backup_files])}")
                return True, backup_files[0] if backup_files else None
            else:
                print(f"   ⚠️ Backup skipped or failed")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Full backup failed: {e}")
            return False, None
    
    def _create_sql_dump(self, backup_dir: str, timestamp: str) -> Optional[str]:
        """
        Create SQL dump using mysqldump command.
        
        Returns:
            Path to created SQL file, or None if failed
        """
        backup_file = os.path.join(backup_dir, f'{ORIGINAL_TABLE}_backup_{timestamp}.sql')
        
        try:
            # Build mysqldump command
            dump_command = [
                'mysqldump',
                f'--host={DB_HOST}',
                f'--user={DB_USER}',
                f'--password={DB_PASSWORD}',
                '--single-transaction',  # Consistent snapshot without locking
                '--skip-lock-tables',    # Don't lock tables
                '--compact',             # Less verbose output
                DB_NAME,
                ORIGINAL_TABLE,
                f'--result-file={backup_file}'
            ]
            
            # Execute mysqldump
            result = subprocess.run(
                dump_command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0 and os.path.exists(backup_file):
                size_mb = os.path.getsize(backup_file) / (1024 * 1024)
                print(f"   ✓ SQL dump created: {os.path.basename(backup_file)} ({size_mb:.2f} MB)")
                
                # Add restore instructions at the top of the file
                self._add_restore_instructions(backup_file)
                
                return backup_file
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                print(f"   ⚠️ SQL dump failed: {error_msg}")
                
                # Try alternative method using Python if mysqldump not available
                return self._create_sql_dump_python(backup_dir, timestamp)
                
        except FileNotFoundError:
            print(f"   ℹ️  mysqldump not available in PATH, using built-in Python method")
            print(f"   💡 Tip: Install MySQL client tools for faster backups")
            return self._create_sql_dump_python(backup_dir, timestamp)
        except Exception as e:
            print(f"   ⚠️ SQL dump error: {e}")
            return None
    
    def _create_sql_dump_python(self, backup_dir: str, timestamp: str) -> Optional[str]:
        """
        Create SQL dump using Python (fallback when mysqldump not available).
        
        Returns:
            Path to created SQL file, or None if failed
        """
        backup_file = os.path.join(backup_dir, f'{ORIGINAL_TABLE}_backup_{timestamp}.sql')
        
        try:
            # Get all data
            query = f"SELECT * FROM {ORIGINAL_TABLE}"
            rows = self._fetch_all(query, ())
            
            if not rows:
                print(f"   ⚠️ No data to backup")
                return None
            
            # Get column names
            columns_query = f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """
            column_rows = self._fetch_all(columns_query, (DB_NAME, ORIGINAL_TABLE))
            columns = [row['COLUMN_NAME'] for row in column_rows]
            
            # Write SQL file
            with open(backup_file, 'w', encoding='utf-8') as f:
                # Header
                f.write(f"-- Full Table Backup: {ORIGINAL_TABLE}\n")
                f.write(f"-- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- Database: {DB_NAME}\n")
                f.write(f"-- Total Rows: {len(rows)}\n")
                f.write(f"--\n")
                f.write(f"-- To restore:\n")
                f.write(f"-- mysql -u {DB_USER} -p {DB_NAME} < {os.path.basename(backup_file)}\n")
                f.write(f"--\n\n")
                
                # Create INSERT statements (batched for efficiency)
                column_list = ', '.join([f'`{col}`' for col in columns])
                batch_size = 100
                
                for i in range(0, len(rows), batch_size):
                    batch = rows[i:i+batch_size]
                    
                    f.write(f"INSERT INTO `{ORIGINAL_TABLE}` ({column_list}) VALUES\n")
                    
                    for idx, row in enumerate(batch):
                        values = []
                        for col in columns:
                            val = row.get(col)
                            if val is None:
                                values.append('NULL')
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            else:
                                # Escape single quotes and wrap in quotes
                                escaped = str(val).replace("'", "\\'").replace("\\", "\\\\")
                                values.append(f"'{escaped}'")
                        
                        value_str = f"({', '.join(values)})"
                        
                        if idx < len(batch) - 1:
                            f.write(f"  {value_str},\n")
                        else:
                            f.write(f"  {value_str};\n\n")
            
            size_mb = os.path.getsize(backup_file) / (1024 * 1024)
            print(f"   ✓ SQL backup created: {os.path.basename(backup_file)} ({size_mb:.2f} MB, {len(rows)} rows)")
            
            return backup_file
            
        except Exception as e:
            print(f"   ❌ Python SQL dump failed: {e}")
            return None
    
    def _create_csv_export(self, backup_dir: str, timestamp: str) -> Optional[str]:
        """
        Create CSV export of the table.
        
        Returns:
            Path to created CSV file, or None if failed
        """
        backup_file = os.path.join(backup_dir, f'{ORIGINAL_TABLE}_backup_{timestamp}.csv')
        
        try:
            # Get all data
            query = f"SELECT * FROM {ORIGINAL_TABLE}"
            rows = self._fetch_all(query, ())
            
            if not rows:
                print(f"   ⚠️ No data to export")
                return None
            
            # Get column names
            columns_query = f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """
            column_rows = self._fetch_all(columns_query, (DB_NAME, ORIGINAL_TABLE))
            columns = [row['COLUMN_NAME'] for row in column_rows]
            
            # Write CSV file
            with open(backup_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow(columns)
                
                # Data rows
                for row in rows:
                    writer.writerow([row.get(col, '') for col in columns])
            
            row_count = len(rows)
            size_mb = os.path.getsize(backup_file) / (1024 * 1024)
            
            print(f"   ✓ CSV export created: {os.path.basename(backup_file)} ({size_mb:.2f} MB, {row_count:,} rows)")
            
            return backup_file
            
        except Exception as e:
            print(f"   ❌ CSV export failed: {e}")
            return None
    
    def _add_restore_instructions(self, sql_file: str):
        """Add restore instructions to the top of SQL dump file."""
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            instructions = f"""-- ═══════════════════════════════════════════════════════════════════════════
-- Full Table Backup: {ORIGINAL_TABLE}
-- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Database: {DB_NAME}
-- ═══════════════════════════════════════════════════════════════════════════
--
-- TO RESTORE THIS BACKUP:
-- 
-- Option 1: Restore entire table (replace current data):
--   mysql -u {DB_USER} -p {DB_NAME} < {os.path.basename(sql_file)}
--
-- Option 2: Restore using MySQL Workbench:
--   1. Open MySQL Workbench
--   2. File → Run SQL Script
--   3. Select this file
--
-- Option 3: Restore via command line with progress:
--   pv {os.path.basename(sql_file)} | mysql -u {DB_USER} -p {DB_NAME}
--
-- ═══════════════════════════════════════════════════════════════════════════

"""
            
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write(instructions + content)
                
        except Exception as e:
            # Non-critical error, just log it
            pass
    
    def _cleanup_old_backup_files(self, backup_dir: str):
        """Remove backup files older than retention period."""
        try:
            cutoff_date = datetime.now() - timedelta(days=FULL_BACKUP_RETENTION_DAYS)
            deleted_count = 0
            
            for filename in os.listdir(backup_dir):
                if not filename.startswith(f'{ORIGINAL_TABLE}_backup_'):
                    continue
                
                filepath = os.path.join(backup_dir, filename)
                
                # Get file modification time
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_mtime < cutoff_date:
                    os.remove(filepath)
                    deleted_count += 1
            
            if deleted_count > 0:
                print(f"   ✓ Cleaned up {deleted_count} old backup file(s)")
                
        except Exception as e:
            # Non-critical error
            print(f"   ⚠️ Cleanup warning: {e}")
    
    # =========================================================================
    # STEP 1: Upload to Staging
    # =========================================================================
    
    def upload_to_staging(self, records: List[Dict]) -> Tuple[int, int]:
        """
        STEP 1 & 2: Clear previous staging data and insert new extraction data.
        
        IMPORTANT: Records received here already have MAPPED dropdown names!
        Mapping was done in upload_extracted.py before calling this function.
        
        Process:
        1. DELETE all previous staging data (from last run)
        2. INSERT new records with Run_ID tag
        
        Data Structure (each record must have):
        - Broker_ID: int
        - Company: str (standardized name)
        - TPA: str
        - Network: str
        - Region: str
        - Dropdown_Name: str (ALREADY MAPPED - standard name, not portal-specific)
        - Selection_Value: str
        
        Args:
            records: List of record dictionaries (already mapped and validated)
        
        Returns:
            Tuple of (rows_inserted, staging_cleared)
        """
        print(f"\n📥 Uploading {len(records)} records to staging table...")
        
        # Clear ALL previous staging data (from previous runs)
        deleted = self._execute(f"DELETE FROM {STAGING_TABLE}", ())
        if deleted > 0:
            print(f"   ✓ Cleaned up {deleted} records from previous run")
        
        # Insert new records in batches
        insert_query = f"""
            INSERT INTO {STAGING_TABLE} 
            (Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value, Run_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        rows_inserted = 0
        batch = []
        
        for record in records:
            batch.append((
                record.get("Broker_ID", 3),
                record.get("Company", ""),
                record.get("TPA", ""),
                record.get("Network", ""),
                record.get("Region", ""),
                record.get("Dropdown_Name", ""),
                record.get("Selection_Value", ""),
                self.run_id
            ))
            
            if len(batch) >= BATCH_SIZE:
                self._execute_many(insert_query, batch)
                rows_inserted += len(batch)
                batch = []
        
        if batch:
            self._execute_many(insert_query, batch)
            rows_inserted += len(batch)
        
        print(f"   ✓ Inserted {rows_inserted} records to staging")
        return rows_inserted, deleted
    
    # =========================================================================
    # STEP 2: Create Backup
    # =========================================================================
    
    def create_backup(self, companies: List[str], dropdown_names_by_company: Dict[str, Set[str]]) -> int:
        """
        Create FULL backup of the entire original table to BACKUP_TABLE.
        
        Backs up ALL records from the original table with Run_ID for retention tracking.
        This provides a complete snapshot of the table state before any changes.
        
        This backup happens in ADDITION to the full table file backup (.sql/.csv).
        Both backup methods run simultaneously during database upload process.
        
        Backup retention: 28 days (older backups auto-deleted)
        Backup table: Medical_CTN_Cascading_Dropdown_Backup
        
        Args:
            companies: List of company names (not used - backing up entire table)
            dropdown_names_by_company: Dict mapping company to set of dropdown names (not used)
        
        Returns:
            Number of records backed up
        """
        print(f"\n💾 Creating full table backup to BACKUP_TABLE...")
        
        # Backup ALL records from original table (complete snapshot)
        backup_query = f"""
            INSERT INTO {BACKUP_TABLE} 
            (Run_ID, Original_CTN_ID, Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
            SELECT %s, CTN_ID, Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value
            FROM {ORIGINAL_TABLE}
        """
        
        total_backed_up = self._execute(backup_query, (self.run_id,))
        
        print(f"   ✓ Backed up {total_backed_up} records from entire table (Run ID: {self.run_id})")
        print(f"   ℹ️  Full table snapshot stored in {BACKUP_TABLE}")
        return total_backed_up if total_backed_up else 0
    
    # =========================================================================
    # STEP 3: Compare Tables
    # =========================================================================
    
    def compare_tables(self, companies: List[str], dropdown_names_by_company: Dict[str, Set[str]], 
                      backup_count: int = 0, old_backups_removed: int = 0, 
                      staging_inserted: int = 0, staging_cleared: int = 0,
                      broker_id: int = None) -> ChangeReport:
        """
        Compare staging table with original table to detect changes.
        
        IMPORTANT: No mapping is done here! Both tables already have standardized dropdown names.
        Dropdown mapping was done in upload_extracted.py BEFORE data was inserted to staging.
        
        This function performs DIRECT comparison:
        - STAGING.Dropdown_Name = ORIGINAL.Dropdown_Name (both already mapped)
        - Exact match on Selection_Value (whitespace-sensitive)
        - BROKER-AWARE: Compares data for specified Broker_ID or ALL brokers in staging
        
        Comparison key: (Broker_ID, Company, TPA, Network, Region, Dropdown_Name)
        Comparison value: Selection_Value (exact match)
        
        Change Detection:
        - NEW: Value exists in staging but not in original → INSERT needed
        - MODIFIED: Same base_key, different value → UPDATE needed
        - DELETED: Value exists in original but not in staging → DELETE needed
        - UNCHANGED: Exact match in both → No action needed
        
        Args:
            companies: List of company names to compare
            dropdown_names_by_company: Dict mapping company to set of dropdown names
            backup_count: Number of records backed up to BACKUP_TABLE
            old_backups_removed: Number of old backup records removed (>28 days)
            staging_inserted: Number of new staging records uploaded
            staging_cleared: Number of old staging records cleared before upload
            broker_id: Broker ID to filter comparison (None = compare ALL brokers in staging)
        
        Returns:
            ChangeReport with all detected changes grouped by portal and dropdown
        """
        if broker_id is None:
            print(f"\n🔍 Comparing staging vs original table (BATCH MODE - ALL BROKERS)...")
        else:
            print(f"\n🔍 Comparing staging vs original table for Broker {broker_id}...")
        print(f"   ℹ️  Using EXACT MATCH - whitespace and case differences will be detected")
        
        report = ChangeReport(
            run_id=self.run_id,
            companies_processed=companies,
            backup_count=backup_count,
            old_backups_removed=old_backups_removed,
            staging_cleared=staging_cleared,
            backup_table=BACKUP_TABLE,
            staging_table=STAGING_TABLE,
            original_table=ORIGINAL_TABLE,
            audit_table=AUDIT_TABLE
        )
        
        # Track total protected groups/values across all companies
        total_protected_groups = 0
        total_protected_values = 0
        
        for company in companies:
            dropdown_names = dropdown_names_by_company.get(company, set())
            
            if not dropdown_names:
                continue
            
            placeholders = ", ".join(["%s"] * len(dropdown_names))
            
            # Get staging records - filter by broker if specified, otherwise get all
            if broker_id is not None:
                staging_query = f"""
                    SELECT Broker_ID, Company, TPA, Network, Region, 
                           Dropdown_Name, Selection_Value
                    FROM {STAGING_TABLE}
                    WHERE Broker_ID = %s AND Company = %s AND Run_ID = %s AND Dropdown_Name IN ({placeholders})
                """
                params = tuple([broker_id, company, self.run_id] + list(dropdown_names))
            else:
                # BATCH MODE: Get ALL brokers in staging for this run
                staging_query = f"""
                    SELECT Broker_ID, Company, TPA, Network, Region, 
                           Dropdown_Name, Selection_Value
                    FROM {STAGING_TABLE}
                    WHERE Company = %s AND Run_ID = %s AND Dropdown_Name IN ({placeholders})
                """
                params = tuple([company, self.run_id] + list(dropdown_names))
            
            staging_rows = self._fetch_all(staging_query, params)
            
            # Get original records - need to fetch for ALL brokers present in staging
            # Extract unique broker IDs from staging data
            staging_broker_ids = set(row.get('Broker_ID') or row.get('broker_id', 3) for row in staging_rows)
            
            if broker_id is not None:
                # Single broker mode
                original_query = f"""
                    SELECT Broker_ID, Company, TPA, Network, Region, 
                           Dropdown_Name, Selection_Value
                    FROM {ORIGINAL_TABLE}
                    WHERE Broker_ID = %s AND Company = %s AND Dropdown_Name IN ({placeholders})
                """
                params = tuple([broker_id, company] + list(dropdown_names))
            else:
                # BATCH MODE: Get original data for ALL brokers present in staging
                if not staging_broker_ids:
                    original_rows = []
                else:
                    broker_placeholders = ", ".join(["%s"] * len(staging_broker_ids))
                    original_query = f"""
                        SELECT Broker_ID, Company, TPA, Network, Region, 
                               Dropdown_Name, Selection_Value
                        FROM {ORIGINAL_TABLE}
                        WHERE Broker_ID IN ({broker_placeholders}) AND Company = %s AND Dropdown_Name IN ({placeholders})
                    """
                    params = tuple(list(staging_broker_ids) + [company] + list(dropdown_names))
            
            if broker_id is not None or staging_broker_ids:
                original_rows = self._fetch_all(original_query, params)
            
            # Build lookup dictionaries
            # Full key includes Selection_Value for exact matching
            staging_full_keys = set()
            staging_by_base_key = {}  # Key without Selection_Value
            
            for row in staging_rows:
                broker_id_val = row.get('Broker_ID') or row.get('broker_id', 3)
                comp = row.get('Company') or row.get('company', '')
                tpa = row.get('TPA') or row.get('tpa', '')
                network = row.get('Network') or row.get('network', '')
                region = row.get('Region') or row.get('region', '')
                dropdown = row.get('Dropdown_Name') or row.get('dropdown_name', '')
                value = row.get('Selection_Value') or row.get('selection_value', '')
                
                # Include Broker_ID in keys for broker-aware comparison
                full_key = (broker_id_val, comp, tpa, network, region, dropdown, value)
                base_key = (broker_id_val, comp, tpa, network, region, dropdown)
                
                staging_full_keys.add(full_key)
                staging_by_base_key.setdefault(base_key, []).append({
                    'broker_id': broker_id_val,
                    'value': value
                })
            
            original_full_keys = set()
            original_by_base_key = {}
            
            for row in original_rows:
                broker_id_val = row.get('Broker_ID') or row.get('broker_id', 3)
                comp = row.get('Company') or row.get('company', '')
                tpa = row.get('TPA') or row.get('tpa', '')
                network = row.get('Network') or row.get('network', '')
                region = row.get('Region') or row.get('region', '')
                dropdown = row.get('Dropdown_Name') or row.get('dropdown_name', '')
                value = row.get('Selection_Value') or row.get('selection_value', '')
                
                # Include Broker_ID in keys for broker-specific comparison
                full_key = (broker_id_val, comp, tpa, network, region, dropdown, value)
                base_key = (broker_id_val, comp, tpa, network, region, dropdown)
                
                original_full_keys.add(full_key)
                original_by_base_key.setdefault(base_key, []).append({
                    'broker_id': broker_id_val,
                    'value': value
                })
            
            # Track which original values have been matched to modified records
            matched_original_values = {}  # base_key -> set of matched values
            
            # Find NEW and MODIFIED records
            # MODIFICATION = only whitespace/case differences (same semantic value)
            # NEW = completely different value that doesn't exist in original
            for base_key, staging_values in staging_by_base_key.items():
                original_values = original_by_base_key.get(base_key, [])
                original_value_set = {v['value'] for v in original_values}
                
                for staging_item in staging_values:
                    staging_value = staging_item['value']
                    
                    if staging_value in original_value_set:
                        # Exact match - unchanged
                        continue
                    
                    # This value doesn't exist in original (exact string match)
                    # Check if this is a whitespace/case modification of an existing value
                    found_similar = False
                    
                    for orig_item in original_values:
                        orig_value = orig_item['value']
                        
                        # Skip if already matched to another staging value
                        if orig_value in matched_original_values.get(base_key, set()):
                            continue
                        
                        # Check if values are similar (whitespace/case difference only)
                        _, _, diff_type = highlight_difference(orig_value, staging_value)
                        
                        if diff_type in ["WHITESPACE_CHANGE", "INTERNAL_WHITESPACE", "CASE_CHANGE"]:
                            # This is a whitespace/case modification - UPDATE needed
                            # Example: "5 %" in original → "5%" in staging
                            report.modified_records.append(ChangeRecord(
                                change_type='UPDATE',
                                broker_id=staging_item['broker_id'],
                                company=base_key[1],
                                tpa=base_key[2],
                                network=base_key[3],
                                region=base_key[4],
                                dropdown_name=base_key[5],
                                old_value=orig_value,
                                new_value=staging_value,
                                difference_type=diff_type
                            ))
                            # Mark this original value as matched (don't delete it separately)
                            matched_original_values.setdefault(base_key, set()).add(orig_value)
                            found_similar = True
                            break
                    
                    if not found_similar:
                        # This is a truly NEW value - INSERT needed
                        # The value doesn't exist in original (not even with whitespace differences)
                        # Example: "X" in staging, but original only has [A, B, C]
                        report.new_records.append(ChangeRecord(
                            change_type='INSERT',
                            broker_id=staging_item['broker_id'],
                            company=base_key[1],
                            tpa=base_key[2],
                            network=base_key[3],
                            region=base_key[4],
                            dropdown_name=base_key[5],
                            new_value=staging_value,
                            difference_type="NEW_VALUE"
                        ))
            
            # Find DELETED records (in original but not in staging)
            # SAFETY: Only delete values from groups that EXIST in staging
            # This prevents mass deletions when API errors cause incomplete extraction
            skipped_groups = 0
            skipped_values = 0
            
            for base_key, original_values in original_by_base_key.items():
                # CRITICAL SAFETY CHECK: Only delete if this GROUP exists in staging
                # If the group doesn't exist in staging, it could mean:
                # - API error (rate limit, session issue, portal change)
                # - Network/TPA data not extracted
                # DON'T delete groups missing from staging - this protects valid data
                if base_key not in staging_by_base_key:
                    skipped_groups += 1
                    skipped_values += len(original_values)
                    continue  # Skip - don't delete groups missing from staging
                
                staging_values = staging_by_base_key[base_key]
                staging_value_set = {v['value'] for v in staging_values}
                
                for orig_item in original_values:
                    orig_value = orig_item['value']
                    
                    # Skip if exact match exists in staging
                    if orig_value in staging_value_set:
                        continue
                    
                    # Skip if already matched as modified
                    if orig_value in matched_original_values.get(base_key, set()):
                        continue
                    
                    # This is a deleted record - group exists in staging but value doesn't
                    report.deleted_records.append(ChangeRecord(
                        change_type='DELETE',
                        broker_id=orig_item['broker_id'],
                        company=base_key[1],
                        tpa=base_key[2],
                        network=base_key[3],
                        region=base_key[4],
                        dropdown_name=base_key[5],
                        old_value=orig_value,
                        difference_type="VALUE_CHANGE"
                    ))
            
            # Track skipped deletions for this company
            if skipped_groups > 0:
                print(f"      ⚠️  {company}: Protected {skipped_values} values in {skipped_groups} groups missing from staging")
                total_protected_groups += skipped_groups
                total_protected_values += skipped_values
        
        # Update report with protected counts
        report.protected_groups = total_protected_groups
        report.protected_values = total_protected_values
        
        # Use the staging_inserted count passed in (more accurate than re-querying)
        report.staging_count = staging_inserted if staging_inserted >0 else 0
        
        # Calculate unchanged count
        report.unchanged_count = report.staging_count - len(report.new_records) - len(report.modified_records)
        
        print(f"   ✓ Comparison complete:")
        print(f"      • New records: {len(report.new_records)}")
        print(f"      • Modified records: {len(report.modified_records)}")
        print(f"      • Deleted records: {len(report.deleted_records)}")
        print(f"      • Unchanged records: {report.unchanged_count}")
        
        # Show protected groups (API error safety)
        if total_protected_groups > 0:
            print(f"      🛡️  Protected: {total_protected_values} values in {total_protected_groups} groups (not in staging - possible API issue)")
        
        # Count whitespace/case changes
        whitespace_changes = sum(1 for r in report.modified_records 
                                if r.difference_type in ["WHITESPACE_CHANGE", "INTERNAL_WHITESPACE"])
        case_changes = sum(1 for r in report.modified_records if r.difference_type == "CASE_CHANGE")
        
        if whitespace_changes > 0:
            print(f"      ⚠️  Whitespace-only changes: {whitespace_changes}")
        if case_changes > 0:
            print(f"      ⚠️  Case-only changes: {case_changes}")
        
        return report
    
    # =========================================================================
    # STEP 4: Generate Change Report
    # =========================================================================
    
    def generate_change_report_text(self, report: ChangeReport) -> str:
        """
        Generate human-readable change report organized by PORTAL/COMPANY.
        Shows exactly which dropdown values changed, including whitespace differences.
        
        Args:
            report: ChangeReport object with all changes
        
        Returns:
            Formatted string report
        """
        lines = []
        lines.append("=" * 90)
        lines.append("📊 EXTRACTION CHANGE REPORT")
        lines.append("=" * 90)
        lines.append(f"   Run ID: {report.run_id}")
        lines.append(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"   Portals Processed: {', '.join(report.companies_processed)}")
        lines.append("=" * 90)
        
        # Count different types of changes
        whitespace_changes = [r for r in report.modified_records 
                             if r.difference_type in ["WHITESPACE_CHANGE", "INTERNAL_WHITESPACE"]]
        case_changes = [r for r in report.modified_records 
                       if r.difference_type == "CASE_CHANGE"]
        value_changes = [r for r in report.modified_records 
                        if r.difference_type == "VALUE_CHANGE"]
        
        # Overall Summary
        lines.append("\n" + "─" * 90)
        lines.append("📈 OVERALL SUMMARY")
        lines.append("─" * 90)
        lines.append(f"   Total records extracted: {report.staging_count}")
        lines.append(f"   Total changes detected: {report.total_changes}")
        lines.append(f"      • New dropdown values: {len(report.new_records)}")
        lines.append(f"      • Modified dropdown values: {len(report.modified_records)}")
        
        if report.modified_records:
            lines.append(f"         ├─ Value changes: {len(value_changes)}")
            lines.append(f"         ├─ Whitespace changes: {len(whitespace_changes)}")
            lines.append(f"         └─ Case changes: {len(case_changes)}")
        
        lines.append(f"      • Deleted dropdown values: {len(report.deleted_records)}")
        lines.append(f"   Unchanged records: {report.unchanged_count}")
        
        if not report.has_changes:
            lines.append("\n" + "─" * 90)
            lines.append("✅ NO CHANGES DETECTED")
            lines.append("   All portals are up to date. No database modifications required.")
            lines.append("─" * 90)
            return "\n".join(lines)
        
        # Portal-wise Summary Table
        changes_by_company = report.get_changes_by_company()
        
        lines.append("\n" + "─" * 90)
        lines.append("📋 PORTAL-WISE SUMMARY")
        lines.append("─" * 90)
        lines.append("")
        lines.append(f"   {'Portal':<30} {'New':>10} {'Modified':>12} {'Deleted':>10} {'Total':>10}")
        lines.append(f"   {'-'*30} {'-'*10} {'-'*12} {'-'*10} {'-'*10}")
        
        for company in report.companies_processed:
            if company in changes_by_company:
                data = changes_by_company[company]
                new_count = len(data['new'])
                mod_count = len(data['modified'])
                del_count = len(data['deleted'])
                total = new_count + mod_count + del_count
                lines.append(f"   {company:<30} {new_count:>10} {mod_count:>12} {del_count:>10} {total:>10}")
            else:
                lines.append(f"   {company:<30} {'0':>10} {'0':>12} {'0':>10} {'0':>10}")
        
        # Detailed Changes by Portal
        lines.append("\n" + "=" * 90)
        lines.append("📝 DETAILED CHANGES BY PORTAL")
        lines.append("=" * 90)
        
        for company in report.companies_processed:
            if company not in changes_by_company:
                lines.append(f"\n┌{'─' * 88}┐")
                lines.append(f"│ 🏢 PORTAL: {company:<75} │")
                lines.append(f"├{'─' * 88}┤")
                lines.append(f"│ ✅ No changes detected - This portal is up to date{' ' * 36} │")
                lines.append(f"└{'─' * 88}┘")
                continue
            
            data = changes_by_company[company]
            total_changes = len(data['new']) + len(data['modified']) + len(data['deleted'])
            
            lines.append(f"\n┌{'─' * 88}┐")
            lines.append(f"│ 🏢 PORTAL: {company:<75} │")
            lines.append(f"│    Total Changes: {total_changes:<68} │")
            lines.append(f"└{'─' * 88}┘")
            
            # MODIFIED dropdown values (most important - show first)
            if data['modified']:
                lines.append(f"\n   🔄 MODIFIED DROPDOWN VALUES ({len(data['modified'])} changes)")
                lines.append(f"   " + "─" * 85)
                
                # Group by dropdown name
                by_dropdown = {}
                for rec in data['modified']:
                    by_dropdown.setdefault(rec.dropdown_name, []).append(rec)
                
                for dropdown_name, recs in by_dropdown.items():
                    lines.append(f"\n   📂 Dropdown: {dropdown_name}")
                    lines.append(f"   " + "." * 80)
                    
                    for rec in recs[:15]:  # Limit display
                        lines.append(f"   │")
                        lines.append(f"   │  TPA: {rec.tpa}")
                        lines.append(f"   │  Network: {rec.network}")
                        lines.append(f"   │  Region: {rec.region}")
                        lines.append(f"   │")
                        
                        old_display = format_value_for_display(rec.old_value)
                        new_display = format_value_for_display(rec.new_value)
                        
                        lines.append(f"   │  ❌ OLD VALUE: {old_display}")
                        lines.append(f"   │  ✅ NEW VALUE: {new_display}")
                        
                        if rec.difference_type and rec.difference_type != "VALUE_CHANGE":
                            lines.append(f"   │  📌 {rec.get_difference_description()}")
                        
                        lines.append(f"   │  " + "─" * 60)
                    
                    if len(recs) > 15:
                        lines.append(f"   │  ... and {len(recs) - 15} more changes")
            
            # NEW dropdown values
            if data['new']:
                lines.append(f"\n   🆕 NEW DROPDOWN VALUES ({len(data['new'])} additions)")
                lines.append(f"   " + "─" * 85)
                
                by_dropdown = {}
                for rec in data['new']:
                    by_dropdown.setdefault(rec.dropdown_name, []).append(rec)
                
                for dropdown_name, recs in by_dropdown.items():
                    lines.append(f"\n   📂 Dropdown: {dropdown_name}")
                    lines.append(f"   " + "." * 80)
                    
                    for rec in recs[:15]:
                        lines.append(f"   │  + {rec.new_value}")
                        lines.append(f"   │    (TPA: {rec.tpa}, Network: {rec.network}, Region: {rec.region})")
                    
                    if len(recs) > 15:
                        lines.append(f"   │  ... and {len(recs) - 15} more new values")
            
            # DELETED dropdown values
            if data['deleted']:
                lines.append(f"\n   🗑️ DELETED DROPDOWN VALUES ({len(data['deleted'])} removals)")
                lines.append(f"   " + "─" * 85)
                
                by_dropdown = {}
                for rec in data['deleted']:
                    by_dropdown.setdefault(rec.dropdown_name, []).append(rec)
                
                for dropdown_name, recs in by_dropdown.items():
                    lines.append(f"\n   📂 Dropdown: {dropdown_name}")
                    lines.append(f"   " + "." * 80)
                    
                    for rec in recs[:15]:
                        lines.append(f"   │  - {rec.old_value}")
                        lines.append(f"   │    (TPA: {rec.tpa}, Network: {rec.network}, Region: {rec.region})")
                    
                    if len(recs) > 15:
                        lines.append(f"   │  ... and {len(recs) - 15} more deleted values")
        
        # Footer
        lines.append("\n" + "=" * 90)
        lines.append("📌 NOTES:")
        lines.append(f"   • Backup created before changes (retained for {BACKUP_RETENTION_DAYS} days)")
        lines.append("   • All changes logged to audit table")
        lines.append("   • Whitespace differences shown with · (middle dot) markers")
        lines.append(f"   • Run ID for reference: {report.run_id}")
        lines.append("=" * 90)
        
        return "\n".join(lines)
    
    # =========================================================================
    # STEP 5: Apply Changes
    # =========================================================================
    
    def apply_changes(self, report: ChangeReport) -> Tuple[int, int, int]:
        """
        Apply detected changes to the original table.
        Only INSERT/UPDATE/DELETE the changed records.
        
        Args:
            report: ChangeReport with changes to apply
        
        Returns:
            Tuple of (inserted_count, updated_count, deleted_count)
        """
        print(f"\n⚡ Applying changes to original table...")
        
        inserted = 0
        updated = 0
        deleted = 0
        
        # Process DELETES first
        if report.deleted_records:
            print(f"   Deleting {len(report.deleted_records)} records...")
            for rec in report.deleted_records:
                delete_query = f"""
                    DELETE FROM {ORIGINAL_TABLE}
                    WHERE Broker_ID = %s AND Company = %s AND TPA = %s AND Network = %s 
                          AND Region = %s AND Dropdown_Name = %s AND Selection_Value = %s
                """
                affected = self._execute(delete_query, (
                    rec.broker_id, rec.company, rec.tpa, rec.network, 
                    rec.region, rec.dropdown_name, rec.old_value
                ))
                deleted += affected if affected else 0
        
        # Process UPDATES (delete old + insert new)
        if report.modified_records:
            print(f"   Updating {len(report.modified_records)} records...")
            for rec in report.modified_records:
                # Delete old value
                delete_query = f"""
                    DELETE FROM {ORIGINAL_TABLE}
                    WHERE Broker_ID = %s AND Company = %s AND TPA = %s AND Network = %s 
                          AND Region = %s AND Dropdown_Name = %s AND Selection_Value = %s
                """
                self._execute(delete_query, (
                    rec.broker_id, rec.company, rec.tpa, rec.network,
                    rec.region, rec.dropdown_name, rec.old_value
                ))
                
                # Insert new value
                insert_query = f"""
                    INSERT INTO {ORIGINAL_TABLE}
                    (Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                affected = self._execute(insert_query, (
                    rec.broker_id or 3, rec.company, rec.tpa, rec.network,
                    rec.region, rec.dropdown_name, rec.new_value
                ))
                updated += 1 if affected else 0
        
        # Process INSERTS
        if report.new_records:
            print(f"   Inserting {len(report.new_records)} records...")
            insert_query = f"""
                INSERT INTO {ORIGINAL_TABLE}
                (Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            batch = []
            for rec in report.new_records:
                batch.append((
                    rec.broker_id or 3, rec.company, rec.tpa, rec.network,
                    rec.region, rec.dropdown_name, rec.new_value
                ))
                
                if len(batch) >= BATCH_SIZE:
                    self._execute_many(insert_query, batch)
                    inserted += len(batch)
                    batch = []
            
            if batch:
                self._execute_many(insert_query, batch)
                inserted += len(batch)
        
        print(f"   ✓ Applied: {inserted} inserted, {updated} updated, {deleted} deleted")
        return inserted, updated, deleted
    
    # =========================================================================
    # STEP 6: Log to Audit Table
    # =========================================================================
    
    def log_to_audit(self, report: ChangeReport) -> int:
        """
        Log all changes to the audit table.
        
        Args:
            report: ChangeReport with all changes
        
        Returns:
            Number of audit records logged
        """
        print(f"\n📝 Logging changes to audit table...")
        
        insert_query = f"""
            INSERT INTO {AUDIT_TABLE}
            (Run_ID, Change_Type, Company, TPA, Network, Region, Dropdown_Name, Old_Value, New_Value, Difference_Type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        all_changes = []
        
        # Log NEW records
        for rec in report.new_records:
            all_changes.append((
                self.run_id, 'INSERT', rec.company, rec.tpa, rec.network,
                rec.region, rec.dropdown_name, None, rec.new_value, rec.difference_type
            ))
        
        # Log MODIFIED records
        for rec in report.modified_records:
            all_changes.append((
                self.run_id, 'UPDATE', rec.company, rec.tpa, rec.network,
                rec.region, rec.dropdown_name, rec.old_value, rec.new_value, rec.difference_type
            ))
        
        # Log DELETED records
        for rec in report.deleted_records:
            all_changes.append((
                self.run_id, 'DELETE', rec.company, rec.tpa, rec.network,
                rec.region, rec.dropdown_name, rec.old_value, None, rec.difference_type
            ))
        
        if all_changes:
            self._execute_many(insert_query, all_changes)
        
        audit_count = len(all_changes)
        print(f"   ✓ Logged {audit_count} changes to audit table")
        return audit_count
    
    # =========================================================================
    # STEP 7 & 8: Cleanup
    # =========================================================================
    
    def cleanup_staging(self):
        """Clear the staging table after successful sync."""
        print(f"\n🧹 Cleaning up staging table...")
        affected = self._execute(f"DELETE FROM {STAGING_TABLE} WHERE Run_ID = %s", (self.run_id,))
        print(f"   ✓ Staging table cleared ({affected} rows removed)")
    
    def cleanup_old_backups(self) -> int:
        """Remove backups older than retention period (28 days).
        
        Returns:
            Number of old backup records removed
        """
        print(f"\n🗑️ Cleaning up old backups (older than {BACKUP_RETENTION_DAYS} days)...")
        
        cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
        
        # Count before delete
        count_query = f"SELECT COUNT(*) as cnt FROM {BACKUP_TABLE} WHERE Backup_Date < %s"
        result = self._fetch_all(count_query, (cutoff_date,))
        old_count = result[0].get('cnt', 0) if result else 0
        
        if old_count > 0:
            delete_query = f"DELETE FROM {BACKUP_TABLE} WHERE Backup_Date < %s"
            self._execute(delete_query, (cutoff_date,))
            print(f"   ✓ Removed {old_count} old backup records")
        else:
            print(f"   ✓ No old backups to remove")
        
        return old_count
    
    # =========================================================================
    # MULTI-BROKER SUPPORT METHODS
    # =========================================================================
    
    def upload_company_data(
        self,
        file_path: str,
        run_id: str,
        company_name: str,
        broker_id: int
    ) -> Dict:
        """
        Upload extracted company data from file for a specific broker.
        Entry point for multi-broker upload system.
        
        Args:
            file_path: Path to extracted .txt file
            run_id: Unique run identifier (timestamp)
            company_name: Portal/company name
            broker_id: Broker ID to associate with this data
            
        Returns:
            Dict with upload results
        """
        import json
        from .staging_config import standardize_company_name
        from .staging_mapping_service import load_dropdown_mappings, apply_dropdown_mapping
        
        print(f"\n   📋 Parsing file: {os.path.basename(file_path)}")
        
        # Parse JSON records from file
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    # Add broker ID to every record
                    record['Broker_ID'] = broker_id
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"      ⚠️ Skipping invalid JSON at line {line_num}: {e}")
        
        if not records:
            print(f"      ⚠️ No valid records found in file")
            return {"success": False, "error": "No valid records"}
        
        print(f"      ✓ Parsed {len(records)} records")
        
        # Standardize company name
        standardized_company = standardize_company_name(company_name)
        for record in records:
            record["Company"] = standardized_company
        
        # Set run ID for this upload
        self.run_id = run_id
        
        # Connect to database for mapping lookup
        if not self._connect():
            raise ConnectionError("Failed to connect to database")
        
        try:
            # Load and apply dropdown mappings
            print(f"      🔄 Applying dropdown name mappings...")
            from .staging_mapping_service import load_dropdown_mappings, apply_dropdown_mapping
            from .staging_config import get_mapping_column_name
            
            # Get the correct column name for mapping table lookup
            mapping_column = get_mapping_column_name(company_name)
            
            mappings = load_dropdown_mappings(self.db, mapping_column)
            if mappings:
                # apply_dropdown_mapping returns 5 values!
                records, mapped, unmapped, applied_mappings, unmapped_names = apply_dropdown_mapping(
                    records, mappings, only_mapped=False
                )
                print(f"         Mapped: {mapped}, Unmapped: {unmapped}")
            else:
                print(f"         No mappings found for {company_name}")
            
            # Get unique dropdown names
            dropdown_names = set(r.get("Dropdown_Name", "") for r in records if r.get("Dropdown_Name"))
            
            # Prepare for process_upload
            companies = [standardized_company]
            dropdown_names_by_company = {standardized_company: dropdown_names}
            
            # Disconnect before calling process_upload (it will create its own connection)
            self._disconnect()
            
            # Call main upload process
            print(f"      📤 Uploading to staging table for Broker {broker_id}...")
            success, report, message = self.process_upload(
                records=records,
                companies=companies,
                dropdown_names_by_company=dropdown_names_by_company
            )
            
            return {
                "success": success,
                "message": message,
                "report": report,
                "records_processed": len(records),
                "changes": report.total_changes if report else 0
            }
            
        except Exception as e:
            # If error occurs before process_upload, disconnect here
            self._disconnect()
            raise
    
    def apply_staging_changes_for_broker(
        self,
        broker_id: int,
        company_name: str,
        run_id: str
    ) -> Dict:
        """
        Apply staging changes to main table for a specific broker.
        This is called by multi_broker_upload.py after replicating staging records.
        
        Args:
            broker_id: Broker ID to process
            company_name: Company/portal name
            run_id: Extraction run ID
            
        Returns:
            Dict with statistics (inserted, updated, deleted counts)
        """
        if not self._connect():
            raise ConnectionError("Failed to connect to database")
        
        try:
            print(f"      📊 Comparing staging vs main for Broker {broker_id}...")
            
            # Fetch staging records for this broker
            staging_query = f"""
                SELECT Company, TPA, Network, Region, Dropdown_Name, Selection_Value
                FROM {STAGING_TABLE}
                WHERE Broker_ID = %s AND Company = %s AND Run_ID = %s
            """
            staging_records = self._fetch_all(staging_query, (broker_id, company_name, run_id))
            
            # Fetch main table records for this broker
            main_query = f"""
                SELECT CTN_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value
                FROM {ORIGINAL_TABLE}
                WHERE Broker_ID = %s AND Company = %s
            """
            main_records = self._fetch_all(main_query, (broker_id, company_name))
            
            # Build lookup sets
            staging_keys = set()
            for row in staging_records:
                key = (
                    row['Company'], row['TPA'], row['Network'],
                    row['Region'], row['Dropdown_Name'], row['Selection_Value']
                )
                staging_keys.add(key)
            
            main_keys_with_ids = {}
            for row in main_records:
                key = (
                    row['Company'], row['TPA'], row['Network'],
                    row['Region'], row['Dropdown_Name'], row['Selection_Value']
                )
                main_keys_with_ids[key] = row['CTN_ID']
            
            # Identify changes
            new_keys = staging_keys - set(main_keys_with_ids.keys())
            deleted_keys = set(main_keys_with_ids.keys()) - staging_keys
            
            inserted = 0
            updated = 0
            deleted = 0
            
            # Insert new records
            if new_keys:
                insert_query = f"""
                    INSERT INTO {ORIGINAL_TABLE}
                    (Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                insert_params = [
                    (broker_id, key[0], key[1], key[2], key[3], key[4], key[5])
                    for key in new_keys
                ]
                self.db.cursor.executemany(insert_query, insert_params)
                inserted = len(insert_params)
                print(f"      ✅ Inserted {inserted} new records")
            
            # Delete old records
            if deleted_keys:
                delete_ids = [main_keys_with_ids[key] for key in deleted_keys]
                placeholders = ','.join(['%s'] * len(delete_ids))
                delete_query = f"DELETE FROM {ORIGINAL_TABLE} WHERE CTN_ID IN ({placeholders})"
                self.db.cursor.execute(delete_query, delete_ids)
                deleted = len(delete_ids)
                print(f"      ✅ Deleted {deleted} old records")
            
            # Commit changes
            self.db.connection.commit()
            
            print(f"      ✅ Applied changes: {inserted} new, {updated} updated, {deleted} deleted")
            
            return {
                "inserted": inserted,
                "updated": updated,
                "deleted": deleted,
                "total": inserted + updated + deleted
            }
            
        except Exception as e:
            print(f"      ❌ Failed to apply changes: {str(e)}")
            if self.db and self.db.connection:
                self.db.connection.rollback()
            raise
        finally:
            self._disconnect()
    
    # =========================================================================
    # MAIN PROCESS METHOD
    # =========================================================================
    
    def process_upload(
        self, 
        records: List[Dict], 
        companies: List[str],
        dropdown_names_by_company: Dict[str, Set[str]]
    ) -> Tuple[bool, ChangeReport, str]:
        """
        Main method to process staged upload with comparison.
        
        ═══════════════════════════════════════════════════════════════════════════
        PREREQUISITE: Records must already have MAPPED dropdown names!
        This function expects data from upload_extracted.py after mapping is done.
        ═══════════════════════════════════════════════════════════════════════════
        
        Complete flow (all within single database transaction):
        
        STEP 1: Cleanup Old Backups
           - DELETE backup records older than 28 days
           - Free up space before creating new backup
           
        STEP 2: Backup Original Data
           - SELECT ALL rows from production table
           - INSERT to backup table with Run_ID (current snapshot)
           
        STEP 3: Upload to Staging
           - DELETE all previous staging data
           - INSERT new records to staging table
           
        STEP 4: Compare Staging ↔ Original
           - DIRECT comparison (no mapping - already done!)
           - Detect NEW, MODIFIED, DELETED values
           - Group changes by portal and dropdown
           
        STEP 5: Apply Changes to Production
           - INSERT new dropdown values
           - UPDATE modified dropdown names
           - DELETE removed values
           
        STEP 6: Audit Trail
           - INSERT all changes to audit table
           - Record old/new values with timestamps
           
        STEP 7: Commit
           - Commit all changes (or rollback on error)
        
        Args:
            records: List of ALREADY-MAPPED record dictionaries
            companies: List of company names being processed
            dropdown_names_by_company: Dict mapping company to set of dropdown names
        
        Returns:
            Tuple of (success: bool, report: ChangeReport, message: str)
        """
        start_time = time.time()
        self.run_id = self._generate_run_id()
        
        print("\n" + "=" * 90)
        print("📤 STAGED DATABASE UPLOAD STARTED")
        print("=" * 90)
        print(f"   Run ID: {self.run_id}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Records to process: {len(records)}")
        print(f"   Companies: {', '.join(companies)}")
        print(f"   Database: {DB_NAME}")
        print(f"   Original Table: {ORIGINAL_TABLE}")
        
        # Initialize empty report
        report = ChangeReport(
            run_id=self.run_id, 
            companies_processed=companies,
            backup_table=BACKUP_TABLE,
            staging_table=STAGING_TABLE,
            original_table=ORIGINAL_TABLE,
            audit_table=AUDIT_TABLE
        )
        
        # Connect
        if not self._connect():
            return False, report, "Failed to connect to database"
        
        try:
            # Step 0: Create full table backup file (before transaction)
            # This is in addition to the full table backup to BACKUP_TABLE
            if ENABLE_FULL_TABLE_BACKUP:
                backup_success, backup_file = self.create_full_table_backup()
                if backup_success and backup_file:
                    report.full_backup_file = backup_file
                elif not backup_success:
                    print(f"   ⚠️ Full backup failed, continuing with staging upload...")
            
            # Start transaction
            self.db.connection.autocommit = False
            
            # Step 1: Cleanup old backups FIRST (delete backups > 28 days)
            old_backups_removed = self.cleanup_old_backups()
            
            # Step 2: Create full backup in BACKUP_TABLE (fresh snapshot before changes)
            backup_count = self.create_backup(companies, dropdown_names_by_company)
            
            # Step 3: Upload to staging (new extraction data)
            staging_inserted, staging_cleared = self.upload_to_staging(records)
            
            # Detect broker mode: single broker or batch (multiple brokers)
            unique_broker_ids = set(r.get('Broker_ID') for r in records if r.get('Broker_ID') is not None)
            
            if len(unique_broker_ids) == 1:
                # Single broker mode
                broker_id = next(iter(unique_broker_ids))
                print(f"   ℹ️  Single-broker mode: Broker {broker_id}")
            elif len(unique_broker_ids) > 1:
                # Batch mode - multiple brokers
                broker_id = None
                print(f"   ℹ️  Batch mode: {len(unique_broker_ids)} brokers ({', '.join(map(str, sorted(unique_broker_ids)))})")
            else:
                # Fallback: no broker ID found
                broker_id = 3
                print(f"   ⚠️  No Broker_ID found in records, defaulting to Broker {broker_id}")
            
            # Step 4: Compare tables (pass counts so they're set during creation)
            report = self.compare_tables(
                companies, 
                dropdown_names_by_company,
                backup_count=backup_count,
                old_backups_removed=old_backups_removed,
                staging_inserted=staging_inserted,
                staging_cleared=staging_cleared,
                broker_id=broker_id  # None = batch mode, int = single broker mode
            )
            
            # Print change report
            report_text = self.generate_change_report_text(report)
            print("\n" + report_text)
            
            # Step 5 & 6: Apply changes and log to audit
            if report.has_changes:
                inserted, updated, deleted = self.apply_changes(report)
                report.audit_records_logged = self.log_to_audit(report)
            else:
                print("\n✅ No changes to apply - database is already up to date")
                report.audit_records_logged = 0
            
            # Commit transaction
            self.db.connection.commit()
            
            # Calculate duration
            duration = time.time() - start_time
            minutes = int(duration // 60)
            seconds = duration % 60
            
            print("\n" + "=" * 90)
            print("✅ STAGED UPLOAD COMPLETED SUCCESSFULLY")
            print("=" * 90)
            print(f"   Run ID: {self.run_id}")
            print(f"   Duration: {minutes}m {seconds:.1f}s")
            print(f"   Total changes applied: {report.total_changes}")
            print(f"      • Inserted: {len(report.new_records)}")
            print(f"      • Updated: {len(report.modified_records)}")
            print(f"      • Deleted: {len(report.deleted_records)}")
            print(f"   Backup records created: {report.backup_count}")
            print("=" * 90)
            
            message = f"Successfully processed {report.staging_count} records with {report.total_changes} changes"
            return True, report, message
            
        except Exception as e:
            # Rollback on error
            print(f"\n❌ Error during staged upload: {e}")
            traceback.print_exc()
            
            if self.db and self.db.connection:
                self.db.connection.rollback()
                print("   ⟲ Transaction rolled back")
            
            return False, report, f"Error: {str(e)}"
            
        finally:
            self._disconnect()


# =============================================================================
# WRAPPER FUNCTION (for integration with upload_extracted.py)
# =============================================================================

def staged_upload_to_database(
    records: List[Dict], 
    companies: List[str],
    dropdown_names_by_company: Dict[str, Set[str]]
) -> Tuple[bool, int, str, ChangeReport]:
    """
    Wrapper function to perform staged upload.
    
    This is called from upload_extracted.py after parsing and mapping.
    
    Args:
        records: List of record dictionaries (after dropdown mapping)
        companies: List of company names being processed
        dropdown_names_by_company: Dict mapping company to set of dropdown names
    
    Returns:
        Tuple of (success, total_changes, message, change_report)
    """
    uploader = StagingUploader()
    success, report, message = uploader.process_upload(records, companies, dropdown_names_by_company)
    return success, report.total_changes, message, report


# =============================================================================
# COMMAND LINE TESTING
# =============================================================================

if __name__ == "__main__":
    print("Testing Staging Uploader...")
    print("This module should be imported and used via staged_upload_to_database()")
    print("\nTo test, run: python -m src.services.db_service.staging_upload")
