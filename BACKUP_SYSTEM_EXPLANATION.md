"""
Backup System Explanation - Extraction Bot
===========================================

YES, you're correct! There are TWO backup methods, and cleanup happens BEFORE creating new backups.

═══════════════════════════════════════════════════════════════════════════════
METHOD 1: DATABASE TABLE BACKUP (BACKUP_TABLE)
═══════════════════════════════════════════════════════════════════════════════

Table: Medical_CTN_Cascading_Dropdown_Backup
Retention: 7 days
When: Before every database update

FLOW:
1. Delete old backups (older than 7 days)
2. Create new full table backup

Code Location: staging_upload.py

def cleanup_old_backups(self):
    \"\"\"Remove backups older than retention period (7 days).\"\"\"
    cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)  # 7 days
    
    # Count old backups
    SELECT COUNT(*) FROM Medical_CTN_Cascading_Dropdown_Backup 
    WHERE Backup_Date < cutoff_date
    
    # Delete old backups
    DELETE FROM Medical_CTN_Cascading_Dropdown_Backup 
    WHERE Backup_Date < cutoff_date

def create_backup(self):
    \"\"\"Create FULL backup of entire original table.\"\"\"
    INSERT INTO Medical_CTN_Cascading_Dropdown_Backup 
    (Run_ID, Original_CTN_ID, Broker_ID, Company, TPA, Network, Region, 
     Dropdown_Name, Selection_Value)
    SELECT 'run_id', CTN_ID, Broker_ID, Company, TPA, Network, Region, 
           Dropdown_Name, Selection_Value
    FROM Medical_CTN_Cascading_Dropdown_Lifecare

EXECUTION ORDER:
1. cleanup_old_backups()  ← Delete backups older than 7 days FIRST
2. create_backup()        ← Insert new full table snapshot SECOND
3. upload_to_staging()    ← Upload new data to staging THIRD


═══════════════════════════════════════════════════════════════════════════════
METHOD 2: FILE BACKUP (SQL/CSV Files)
═══════════════════════════════════════════════════════════════════════════════

Location: database/backups/
Retention: 30 days
Formats: SQL dump (.sql) or CSV export (.csv) or both
When: Before every database update

FLOW:
1. Create new backup file(s)
2. Delete old backup files (older than 30 days)

Code Location: staging_upload.py

def create_full_table_backup(self):
    \"\"\"Create complete file backup.\"\"\"
    # 1. Create new backup file(s)
    if FULL_BACKUP_FORMAT == 'sql':
        _create_sql_dump()  # Creates .sql file
    elif FULL_BACKUP_FORMAT == 'csv':
        _create_csv_export()  # Creates .csv file
    elif FULL_BACKUP_FORMAT == 'both':
        _create_sql_dump() + _create_csv_export()
    
    # 2. Cleanup old files
    _cleanup_old_backup_files()

def _cleanup_old_backup_files(self, backup_dir):
    \"\"\"Delete backup files older than 30 days.\"\"\"
    cutoff_date = datetime.now() - timedelta(days=FULL_BACKUP_RETENTION_DAYS)  # 30 days
    
    for file in backup_dir:
        file_date = extract_date_from_filename(file)
        if file_date < cutoff_date:
            os.remove(file)

EXECUTION ORDER (within create_full_table_backup):
1. _create_sql_dump()              ← Create new .sql file
2. _create_csv_export()            ← Create new .csv file (if enabled)
3. _cleanup_old_backup_files()    ← Delete files older than 30 days


═══════════════════════════════════════════════════════════════════════════════
CONFIGURATION SETTINGS
═══════════════════════════════════════════════════════════════════════════════

staging_config.py:

# Method 1: Database Table Backup
BACKUP_TABLE = "Medical_CTN_Cascading_Dropdown_Backup"
BACKUP_RETENTION_DAYS = 7  ← Delete backups older than 7 days

# Method 2: File Backup
ENABLE_FULL_TABLE_BACKUP = True
FULL_BACKUP_FORMAT = 'sql'  # Options: 'sql', 'csv', 'both'
FULL_BACKUP_DIR = 'database/backups'
FULL_BACKUP_RETENTION_DAYS = 30  ← Delete files older than 30 days


═══════════════════════════════════════════════════════════════════════════════
COMPLETE BACKUP PROCESS (Every Extraction Run)
═══════════════════════════════════════════════════════════════════════════════

main.py execution:

1. Extract data from portals
2. BACKUP PROCESS (BEFORE staging upload):
   
   A. FILE BACKUP (outside transaction):
      ├─ _create_sql_dump()        ← CREATE new .sql file
      ├─ _create_csv_export()      ← CREATE new .csv file (if enabled)
      └─ _cleanup_old_backup_files() ← DELETE old files (> 30 days)
   
   B. DATABASE TRANSACTION STARTS:
      ├─ cleanup_old_backups()     ← DELETE old records (> 7 days) FIRST
      ├─ create_backup()           ← INSERT new full snapshot SECOND
      └─ upload_to_staging()       ← Upload new data THIRD

3. Compare staging vs original
4. Apply changes to production table
5. Log to audit table
6. Commit transaction


═══════════════════════════════════════════════════════════════════════════════
YOUR UNDERSTANDING IS CORRECT!
═══════════════════════════════════════════════════════════════════════════════

YES - Order is:
1. First DELETE old backups (cleanup)
2. Then CREATE new backup (insert/create)

This ensures:
✅ No accumulation of old data
✅ Controlled storage usage
✅ Automatic rotation
✅ Always have recent backups

DATABASE TABLE BACKUP: Cleanup → Insert (7 day retention)
FILE BACKUP: Create → Cleanup (30 day retention)
  (Slight difference in order but same concept - keep only recent backups)


═══════════════════════════════════════════════════════════════════════════════
WHY TWO BACKUP METHODS?
═══════════════════════════════════════════════════════════════════════════════

METHOD 1 (Database Table):
✅ Fast query access
✅ Can restore specific records
✅ Integrated with SQL queries
✅ 7-day retention (short-term recovery)

METHOD 2 (File Backup):
✅ Complete disaster recovery
✅ Portable (can move to another server)
✅ Can restore entire database
✅ 30-day retention (long-term recovery)
✅ Human-readable (CSV) or executable (SQL)

Together: Comprehensive backup strategy with multiple recovery options!
"""

# Example verification query
"""
-- Check current backups in database table
SELECT 
    Run_ID,
    Backup_Date,
    COUNT(*) as Records,
    DATEDIFF(NOW(), Backup_Date) as Days_Old
FROM Medical_CTN_Cascading_Dropdown_Backup
GROUP BY Run_ID, Backup_Date
ORDER BY Backup_Date DESC;

-- Should show:
-- Only backups from last 7 days
-- Older backups automatically deleted
"""
