# 📊 TABLE OPERATIONS EXPLAINED - Complete Working Flow

> **Complete guide showing ACTUAL SQL queries and operations for each table**

---

## 🎯 QUICK OVERVIEW

| Table | Primary Purpose | Main Operations | Auto-Cleanup |
|-------|----------------|-----------------|--------------|
| **Staging** | Temporary workspace for new extractions | INSERT, DELETE, SELECT | ✅ Every run |
| **Backup** | Safety snapshot before changes | INSERT, DELETE, SELECT | ✅ After 7 days |
| **Audit** | Permanent change history log | INSERT, SELECT | ❌ Never |

---

# 1️⃣ STAGING TABLE (`Medical_CTN_Cascading_Dropdown_Staging`)

## 📝 Purpose
Temporary storage for **NEW extraction data** before comparing with production. Acts as a workspace to load fresh portal data.

## 🔄 Key Characteristics
- **Cleared at START** of each extraction run
- **Data retained** until next run (for manual comparison if needed)
- **No permanent data** - completely replaced each time

---

## 📌 OPERATION 1: DELETE (Clear Old Data)

### When: **START** of every extraction run
### Why: Make room for fresh data

```sql
-- Clear ALL previous staging data from last run
DELETE FROM Medical_CTN_Cascading_Dropdown_Staging
```

**Location in Code:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L544)

```python
# Clear ALL previous staging data (from previous runs)
deleted = self._execute(f"DELETE FROM {STAGING_TABLE}", ())
if deleted > 0:
    print(f"   ✓ Cleaned up {deleted} records from previous run")
```

**Result:** Empty staging table ready for new data

---

## 📌 OPERATION 2: INSERT (Upload New Extraction Data)

### When: After clearing staging table
### Why: Load fresh portal data for comparison

```sql
-- Insert new extraction records with Run_ID tag
INSERT INTO Medical_CTN_Cascading_Dropdown_Staging 
(Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value, Run_ID)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
```

**Location in Code:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L547-L569)

```python
# Insert new records in batches (BATCH_SIZE = 500)
insert_query = f"""
    INSERT INTO {STAGING_TABLE} 
    (Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value, Run_ID)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

for record in records:
    batch.append((
        record.get("Broker_ID", 3),
        record.get("Company", ""),
        record.get("TPA", ""),
        record.get("Network", ""),
        record.get("Region", ""),
        record.get("Dropdown_Name", ""),      # Already MAPPED!
        record.get("Selection_Value", ""),
        self.run_id                            # 20260226_153045
    ))
    
    if len(batch) >= BATCH_SIZE:
        self._execute_many(insert_query, batch)
        rows_inserted += len(batch)
        batch = []
```

**Example Data Inserted:**
```
Broker_ID: 3
Company: "SUKOON INSURANCE"
TPA: "NextCare"
Network: "Enhanced"
Region: "Dubai"
Dropdown_Name: "Quotation_For"           (Already mapped from portal name!)
Selection_Value: "Individual"
Run_ID: "20260226_153045"
```

---

## 📌 OPERATION 3: SELECT (Read for Comparison)

### When: During comparison phase
### Why: Compare staging data vs production data

```sql
-- Get all staging records for a specific company and dropdown names
SELECT Broker_ID, Company, TPA, Network, Region, 
       Dropdown_Name, Selection_Value
FROM Medical_CTN_Cascading_Dropdown_Staging
WHERE Company = %s 
  AND Run_ID = %s 
  AND Dropdown_Name IN (%s, %s, %s, ...)
```

**Location in Code:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L664-L671)

```python
# Get all staging records for this company
staging_query = f"""
    SELECT Broker_ID, Company, TPA, Network, Region, 
           Dropdown_Name, Selection_Value
    FROM {STAGING_TABLE}
    WHERE Company = %s AND Run_ID = %s AND Dropdown_Name IN ({placeholders})
"""
params = tuple([company, self.run_id] + list(dropdown_names))
staging_rows = self._fetch_all(staging_query, params)
```

**What Happens Next:** 
- Compare with ORIGINAL table
- Detect NEW, MODIFIED, DELETED values

---

## 📌 OPERATION 4: Optional Cleanup (After Commit)

### When: After successful database update (optional)
### Why: Clean up immediately if needed

```sql
-- Clear staging data for this specific Run_ID
DELETE FROM Medical_CTN_Cascading_Dropdown_Staging 
WHERE Run_ID = %s
```

**Location in Code:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L1239)

```python
def cleanup_staging(self):
    """Clear the staging table after successful sync."""
    print(f"\n🧹 Cleaning up staging table...")
    affected = self._execute(f"DELETE FROM {STAGING_TABLE} WHERE Run_ID = %s", 
                            (self.run_id,))
    print(f"   ✓ Staging table cleared ({affected} rows removed)")
```

**Note:** Usually NOT called - data kept until next run for manual inspection

---

# 2️⃣ BACKUP TABLE (`Medical_CTN_Cascading_Dropdown_Backup`)

## 📝 Purpose
**Complete snapshot** of production table BEFORE any changes. Safety net for disaster recovery.

## 🔄 Key Characteristics
- **Full table backup** - copies ENTIRE original table
- **7-day retention** - old backups auto-deleted
- **Tagged with Run_ID** - links to specific extraction run

---

## 📌 OPERATION 1: DELETE (Cleanup Old Backups)

### When: BEFORE creating new backup (at start of each run)
### Why: Remove backups older than 7 days to save space

```sql
-- Count old backups
SELECT COUNT(*) as cnt 
FROM Medical_CTN_Cascading_Dropdown_Backup 
WHERE Backup_Date < %s

-- Delete old backups (older than 7 days)
DELETE FROM Medical_CTN_Cascading_Dropdown_Backup 
WHERE Backup_Date < %s
```

**Location in Code:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L1245-L1265)

```python
def cleanup_old_backups(self) -> int:
    """Remove backups older than retention period (7 days)."""
    
    cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)  # 7 days ago
    
    # Count before delete
    count_query = f"SELECT COUNT(*) as cnt FROM {BACKUP_TABLE} WHERE Backup_Date < %s"
    result = self._fetch_all(count_query, (cutoff_date,))
    old_count = result[0].get('cnt', 0) if result else 0
    
    if old_count > 0:
        delete_query = f"DELETE FROM {BACKUP_TABLE} WHERE Backup_Date < %s"
        self._execute(delete_query, (cutoff_date,))
        print(f"   ✓ Removed {old_count} old backup records")
    
    return old_count
```

**Example:**
- Today: Feb 26, 2026
- Cutoff: Feb 19, 2026 (7 days ago)
- Deletes: All backups before Feb 19

---

## 📌 OPERATION 2: INSERT (Create Full Backup)

### When: AFTER cleanup, BEFORE any changes to production
### Why: Create complete snapshot of current state

```sql
-- Backup ENTIRE original table (all records)
INSERT INTO Medical_CTN_Cascading_Dropdown_Backup 
(Run_ID, Original_CTN_ID, Broker_ID, Company, TPA, Network, Region, 
 Dropdown_Name, Selection_Value)
SELECT %s, CTN_ID, Broker_ID, Company, TPA, Network, Region, 
       Dropdown_Name, Selection_Value
FROM Medical_CTN_Cascading_Dropdown_Lifecare
```

**Location in Code:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L594-L612)

```python
def create_backup(self, companies: List[str], dropdown_names_by_company: Dict[str, Set[str]]) -> int:
    """
    Create FULL backup of the entire original table to BACKUP_TABLE.
    
    Backs up ALL records from the original table with Run_ID for retention tracking.
    This provides a complete snapshot of the table state before any changes.
    """
    print(f"\n💾 Creating full table backup to BACKUP_TABLE...")
    
    # Backup ALL records from original table (complete snapshot)
    backup_query = f"""
        INSERT INTO {BACKUP_TABLE} 
        (Run_ID, Original_CTN_ID, Broker_ID, Company, TPA, Network, Region, 
         Dropdown_Name, Selection_Value)
        SELECT %s, CTN_ID, Broker_ID, Company, TPA, Network, Region, 
               Dropdown_Name, Selection_Value
        FROM {ORIGINAL_TABLE}
    """
    
    total_backed_up = self._execute(backup_query, (self.run_id,))
    
    print(f"   ✓ Backed up {total_backed_up} records from entire table (Run ID: {self.run_id})")
    return total_backed_up if total_backed_up else 0
```

**What Gets Backed Up:**
- ✅ **ALL** records from production table
- ✅ Tagged with current Run_ID
- ✅ Includes Original_CTN_ID for reference

**Example Backup Record:**
```
Backup_ID: 12345 (auto-increment)
Run_ID: "20260226_153045"
Original_CTN_ID: 5678
Broker_ID: 3
Company: "SUKOON INSURANCE"
TPA: "NextCare"
Network: "Enhanced"
Region: "Dubai"
Dropdown_Name: "Quotation_For"
Selection_Value: "Individual"
Backup_Date: 2026-02-26 15:30:45
```

---

## 📌 OPERATION 3: SELECT (Read Backups)

### When: Manual recovery or audit review
### Why: Restore data if something goes wrong

```sql
-- View all backups for a specific run
SELECT * FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Run_ID = '20260226_153045'
ORDER BY Backup_Date DESC

-- View all backups for a specific company
SELECT * FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Company = 'SUKOON INSURANCE'
  AND Backup_Date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY Backup_Date DESC

-- Count total backups
SELECT Run_ID, COUNT(*) as record_count, Backup_Date
FROM Medical_CTN_Cascading_Dropdown_Backup
GROUP BY Run_ID, Backup_Date
ORDER BY Backup_Date DESC
```

**Use Cases:**
1. **Disaster Recovery** - Restore deleted data
2. **Audit Trail** - Review historical changes
3. **Debugging** - Compare before/after states

---

## 📌 OPERATION 4: Restore from Backup (Manual)

### When: Emergency - need to undo changes
### Why: Recover from accidental deletions or bad data

```sql
-- Restore specific company data from backup
INSERT INTO Medical_CTN_Cascading_Dropdown_Lifecare
(Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
SELECT Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value
FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Run_ID = '20260226_153045'
  AND Company = 'SUKOON INSURANCE'
```

**⚠️ Warning:** Manual operation - requires careful review!

---

# 3️⃣ AUDIT TABLE (`Medical_CTN_Cascading_Dropdown_Audit`)

## 📝 Purpose
**Permanent log** of ALL changes made to production data. Complete audit trail with old/new values.

## 🔄 Key Characteristics
- **Never deleted** - permanent history
- **Tracks INSERT/UPDATE/DELETE** operations
- **Shows old and new values** for transparency
- **Categorizes difference types** (VALUE_CHANGE, WHITESPACE_CHANGE, CASE_CHANGE)

---

## 📌 OPERATION 1: INSERT (Log All Changes)

### When: After applying changes to production table
### Why: Create permanent audit trail

```sql
-- Log changes to audit table
INSERT INTO Medical_CTN_Cascading_Dropdown_Audit
(Run_ID, Change_Type, Company, TPA, Network, Region, 
 Dropdown_Name, Old_Value, New_Value, Difference_Type)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
```

**Location in Code:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L1186-L1223)

```python
def log_to_audit(self, report: ChangeReport) -> int:
    """Log all changes to the audit table."""
    
    print(f"\n📝 Logging changes to audit table...")
    
    insert_query = f"""
        INSERT INTO {AUDIT_TABLE}
        (Run_ID, Change_Type, Company, TPA, Network, Region, 
         Dropdown_Name, Old_Value, New_Value, Difference_Type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    all_changes = []
    
    # Log NEW records (INSERT)
    for rec in report.new_records:
        all_changes.append((
            self.run_id, 'INSERT', rec.company, rec.tpa, rec.network,
            rec.region, rec.dropdown_name, None, rec.new_value, rec.difference_type
        ))
    
    # Log MODIFIED records (UPDATE)
    for rec in report.modified_records:
        all_changes.append((
            self.run_id, 'UPDATE', rec.company, rec.tpa, rec.network,
            rec.region, rec.dropdown_name, rec.old_value, rec.new_value, rec.difference_type
        ))
    
    # Log DELETED records (DELETE)
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
```

---

### Example Audit Records

#### INSERT (New Value Added)
```
Audit_ID: 101
Run_ID: "20260226_153045"
Change_Type: "INSERT"
Company: "SUKOON INSURANCE"
TPA: "NextCare"
Network: "Enhanced"
Region: "Dubai"
Dropdown_Name: "Quotation_For"
Old_Value: NULL
New_Value: "Family Floater"
Difference_Type: "NEW_VALUE"
Changed_At: 2026-02-26 15:30:50
```

#### UPDATE (Value Modified)
```
Audit_ID: 102
Run_ID: "20260226_153045"
Change_Type: "UPDATE"
Company: "SUKOON INSURANCE"
TPA: "NextCare"
Network: "Enhanced"
Region: "Dubai"
Dropdown_Name: "Coverage_Amount"
Old_Value: "AED 100,000"
New_Value: "AED 150,000"
Difference_Type: "VALUE_CHANGE"
Changed_At: 2026-02-26 15:30:50
```

#### DELETE (Value Removed)
```
Audit_ID: 103
Run_ID: "20260226_153045"
Change_Type: "DELETE"
Company: "SUKOON INSURANCE"
TPA: "NextCare"
Network: "Enhanced"
Region: "Dubai"
Dropdown_Name: "Policy_Type"
Old_Value: "Old Policy"
New_Value: NULL
Difference_Type: "VALUE_CHANGE"
Changed_At: 2026-02-26 15:30:50
```

#### UPDATE (Whitespace Change Only)
```
Audit_ID: 104
Run_ID: "20260226_153045"
Change_Type: "UPDATE"
Company: "SUKOON INSURANCE"
TPA: "NextCare"
Network: "Enhanced"
Region: "Dubai"
Dropdown_Name: "Deductible"
Old_Value: "5 %"
New_Value: "5%"
Difference_Type: "WHITESPACE_CHANGE"
Changed_At: 2026-02-26 15:30:50
```

---

## 📌 OPERATION 2: SELECT (Read Audit History)

### When: Manual review, debugging, reporting
### Why: Track what changed, when, and why

### Query 1: View All Changes for a Run
```sql
SELECT * FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Run_ID = '20260226_153045'
ORDER BY Changed_At DESC
```

### Query 2: View Changes for Specific Company
```sql
SELECT * FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Company = 'SUKOON INSURANCE'
  AND Changed_At >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY Changed_At DESC
```

### Query 3: View Changes by Type
```sql
-- Only deletions
SELECT * FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Change_Type = 'DELETE'
  AND Changed_At >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY Changed_At DESC

-- Only whitespace changes
SELECT * FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Difference_Type IN ('WHITESPACE_CHANGE', 'INTERNAL_WHITESPACE')
ORDER BY Changed_At DESC
```

### Query 4: Summary Report
```sql
-- Count changes by type for each company
SELECT 
    Company,
    Change_Type,
    COUNT(*) as change_count,
    DATE(Changed_At) as change_date
FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Changed_At >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY Company, Change_Type, DATE(Changed_At)
ORDER BY change_date DESC, Company, Change_Type
```

### Query 5: Detect Specific Dropdown Changes
```sql
-- Track changes to a specific dropdown
SELECT 
    Run_ID,
    Change_Type,
    Company,
    TPA,
    Network,
    Old_Value,
    New_Value,
    Changed_At
FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Dropdown_Name = 'Quotation_For'
  AND Company = 'SUKOON INSURANCE'
ORDER BY Changed_At DESC
LIMIT 50
```

**Location in Code:** Used in various check scripts (`check_value_changes.py`, `verify_reinsert.py`)

---

# 🔄 COMPLETE WORKFLOW SUMMARY

## Step-by-Step Flow with SQL Queries

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: CLEANUP OLD BACKUPS                                     │
├─────────────────────────────────────────────────────────────────┤
│ DELETE FROM Medical_CTN_Cascading_Dropdown_Backup              │
│ WHERE Backup_Date < (NOW() - INTERVAL 7 DAY)                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: CREATE FULL BACKUP (Before any changes)                │
├─────────────────────────────────────────────────────────────────┤
│ INSERT INTO Medical_CTN_Cascading_Dropdown_Backup              │
│ SELECT '20260226_153045', CTN_ID, Broker_ID, ...               │
│ FROM Medical_CTN_Cascading_Dropdown_Lifecare                   │
│                                                                  │
│ Result: 15,234 records backed up                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: CLEAR STAGING TABLE                                     │
├─────────────────────────────────────────────────────────────────┤
│ DELETE FROM Medical_CTN_Cascading_Dropdown_Staging             │
│                                                                  │
│ Result: 8,456 old records removed                              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: INSERT NEW DATA TO STAGING                              │
├─────────────────────────────────────────────────────────────────┤
│ INSERT INTO Medical_CTN_Cascading_Dropdown_Staging             │
│ (Broker_ID, Company, TPA, Network, Region,                     │
│  Dropdown_Name, Selection_Value, Run_ID)                       │
│ VALUES (3, 'SUKOON', 'NextCare', 'Enhanced', 'Dubai',          │
│         'Quotation_For', 'Individual', '20260226_153045')      │
│                                                                  │
│ Result: 8,523 new records inserted (batches of 500)            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: COMPARE STAGING ↔ ORIGINAL                             │
├─────────────────────────────────────────────────────────────────┤
│ SELECT ... FROM Medical_CTN_Cascading_Dropdown_Staging         │
│ WHERE Company = 'SUKOON' AND Run_ID = '20260226_153045'       │
│                                                                  │
│ SELECT ... FROM Medical_CTN_Cascading_Dropdown_Lifecare        │
│ WHERE Company = 'SUKOON'                                       │
│                                                                  │
│ Result: Detect 125 changes                                     │
│   • 45 NEW values                                              │
│   • 12 MODIFIED values (whitespace/case)                       │
│   • 68 DELETED values                                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6A: DELETE (Remove values)                                │
├─────────────────────────────────────────────────────────────────┤
│ DELETE FROM Medical_CTN_Cascading_Dropdown_Lifecare            │
│ WHERE Company = 'SUKOON' AND TPA = 'NextCare'                 │
│   AND Network = 'Enhanced' AND Region = 'Dubai'               │
│   AND Dropdown_Name = 'Policy_Type'                           │
│   AND Selection_Value = 'Old Policy'                          │
│                                                                  │
│ Result: 68 records deleted                                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6B: UPDATE (Modify values)                                │
├─────────────────────────────────────────────────────────────────┤
│ -- Delete old value                                            │
│ DELETE FROM Medical_CTN_Cascading_Dropdown_Lifecare            │
│ WHERE ... AND Selection_Value = '5 %'                          │
│                                                                  │
│ -- Insert new value                                            │
│ INSERT INTO Medical_CTN_Cascading_Dropdown_Lifecare            │
│ VALUES (3, 'SUKOON', 'NextCare', 'Enhanced', 'Dubai',          │
│         'Deductible', '5%')                                    │
│                                                                  │
│ Result: 12 records updated                                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6C: INSERT (Add new values)                               │
├─────────────────────────────────────────────────────────────────┤
│ INSERT INTO Medical_CTN_Cascading_Dropdown_Lifecare            │
│ VALUES (3, 'SUKOON', 'NextCare', 'Enhanced', 'Dubai',          │
│         'Quotation_For', 'Family Floater')                     │
│                                                                  │
│ Result: 45 new records inserted (batches of 500)               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: LOG TO AUDIT TABLE                                      │
├─────────────────────────────────────────────────────────────────┤
│ INSERT INTO Medical_CTN_Cascading_Dropdown_Audit               │
│ (Run_ID, Change_Type, Company, TPA, Network, Region,           │
│  Dropdown_Name, Old_Value, New_Value, Difference_Type)         │
│ VALUES                                                          │
│   ('20260226_153045', 'INSERT', 'SUKOON', ..., NULL,           │
│    'Family Floater', 'NEW_VALUE'),                             │
│   ('20260226_153045', 'UPDATE', 'SUKOON', ..., '5 %',          │
│    '5%', 'WHITESPACE_CHANGE'),                                 │
│   ('20260226_153045', 'DELETE', 'SUKOON', ..., 'Old Policy',   │
│    NULL, 'VALUE_CHANGE')                                       │
│                                                                  │
│ Result: 125 audit records logged                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: COMMIT TRANSACTION                                      │
├─────────────────────────────────────────────────────────────────┤
│ COMMIT;                                                         │
│                                                                  │
│ ✅ All changes applied successfully                            │
└─────────────────────────────────────────────────────────────────┘
```

---

# 📊 DATA RETENTION SUMMARY

| Table | Retention Policy | Cleanup Method | Purpose |
|-------|-----------------|----------------|---------|
| **Staging** | Until next run | Manual `DELETE` at run start | Temporary workspace |
| **Backup** | 7 days | Auto `DELETE` before each backup | Disaster recovery |
| **Audit** | Permanent | Never deleted | Compliance & audit trail |
| **Original** | Permanent | Only updated with changes | Production data |

---

# 🔍 SAFETY FEATURES

## 1. **Transaction Safety**
```python
# Start transaction
self.db.connection.autocommit = False

try:
    # All operations...
    self.db.connection.commit()  # ✅ Success
except Exception as e:
    self.db.connection.rollback()  # ❌ Undo everything
```

## 2. **API Error Protection**
```python
# Only delete values from groups that EXIST in staging
if base_key not in staging_by_base_key:
    skipped_groups += 1
    continue  # Don't delete - missing from staging (possible API error)
```

**Example:** If API fails to extract "Daman Health" data → Don't delete existing Daman records!

## 3. **Full Backup Before Changes**
```sql
-- Complete snapshot BEFORE any modifications
INSERT INTO Medical_CTN_Cascading_Dropdown_Backup 
SELECT '20260226_153045', * FROM Medical_CTN_Cascading_Dropdown_Lifecare
```

## 4. **Audit Trail**
Every change logged with:
- What changed (Old_Value → New_Value)
- When changed (Changed_At timestamp)
- Why changed (Difference_Type: NEW_VALUE, WHITESPACE_CHANGE, etc.)
- Who triggered it (Run_ID links to extraction session)

---

# 🛠️ USEFUL QUERIES FOR MONITORING

## Check Recent Changes
```sql
SELECT 
    Run_ID,
    Change_Type,
    COUNT(*) as changes
FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Changed_At >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY Run_ID, Change_Type
ORDER BY Run_ID DESC
```

## View Current Staging Data
```sql
SELECT 
    Company,
    Dropdown_Name,
    COUNT(*) as value_count
FROM Medical_CTN_Cascading_Dropdown_Staging
GROUP BY Company, Dropdown_Name
ORDER BY Company, Dropdown_Name
```

## Check Backup Status
```sql
SELECT 
    Run_ID,
    COUNT(*) as records_backed_up,
    Backup_Date
FROM Medical_CTN_Cascading_Dropdown_Backup
GROUP BY Run_ID, Backup_Date
ORDER BY Backup_Date DESC
LIMIT 10
```

## Find Whitespace-Only Changes
```sql
SELECT 
    Company,
    Dropdown_Name,
    Old_Value,
    New_Value,
    Changed_At
FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Difference_Type IN ('WHITESPACE_CHANGE', 'INTERNAL_WHITESPACE')
  AND Changed_At >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY Changed_At DESC
```

---

# 📖 CODE REFERENCE

| Operation | File Location | Line Range |
|-----------|--------------|------------|
| Staging DELETE | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 544 |
| Staging INSERT | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 547-569 |
| Staging SELECT | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 664-671 |
| Backup DELETE | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 1245-1265 |
| Backup INSERT | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 594-612 |
| Original DELETE | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 1113-1121 |
| Original UPDATE | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 1123-1147 |
| Original INSERT | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 1149-1174 |
| Audit INSERT | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 1186-1223 |
| Compare Logic | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 617-900 |

---

# ✅ SUMMARY

Each table has a specific role with distinct operations:

1. **STAGING** = Temporary workspace
   - INSERT new extraction data
   - DELETE old data at start
   - SELECT for comparison
   - **Never permanent storage**

2. **BACKUP** = Safety snapshot
   - INSERT full table before changes
   - DELETE backups older than 7 days
   - SELECT for disaster recovery
   - **7-day rolling retention**

3. **AUDIT** = Permanent history
   - INSERT all changes (INSERT/UPDATE/DELETE)
   - SELECT for reporting and compliance
   - **Never deleted - permanent log**

**All operations happen in a single database transaction** - if anything fails, everything rolls back! 🛡️
