# 🗄️ Database Flow & Table Architecture Documentation

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Database Tables](#database-tables)
3. [Complete Data Flow](#complete-data-flow)
4. [Dropdown Name Mapping](#dropdown-name-mapping)
5. [Backup Strategy](#backup-strategy)
6. [Audit Trail System](#audit-trail-system)
7. [Configuration Options](#configuration-options)
8. [Error Handling & Recovery](#error-handling--recovery)

---

## 🎯 System Overview

The Extraction Bot is designed to extract cascading dropdown data from multiple insurance portal APIs, standardize the data through mapping, and intelligently synchronize it with the production database while maintaining complete audit trails and backup safety nets.

### Key Features
✅ **Smart Comparison**: Only changes are applied to the database  
✅ **Dual Backup**: Full table backup (files) + Selective database backup  
✅ **Complete Audit Trail**: Every INSERT/UPDATE/DELETE is logged permanently  
✅ **Dropdown Mapping**: Portal-specific names → Standardized database names  
✅ **Whitespace Detection**: Detects subtle differences (spaces, case changes)  
✅ **Transaction Safety**: Rollback on error - all or nothing  

---

## 🗄️ Database Tables

The system uses **5 primary tables** working together:

### 1️⃣ Medical_CTN_Cascading_Dropdown_Lifecare (PRODUCTION TABLE)

**Purpose**: Main production table containing live cascading dropdown data

**Structure**:
```sql
CREATE TABLE Medical_CTN_Cascading_Dropdown_Lifecare (
    CTN_ID INT AUTO_INCREMENT PRIMARY KEY,
    Broker_ID INT,
    Company VARCHAR(100),       -- Insurance company name
    TPA VARCHAR(100),            -- Third Party Administrator
    Network VARCHAR(100),        -- Network provider
    Region VARCHAR(100),         -- Geographic region
    Dropdown_Name TEXT,          -- Standard dropdown field name
    Selection_Value TEXT,        -- Actual dropdown value
    Created_At DATETIME,
    Updated_At DATETIME,
    
    INDEX idx_company (Company),
    INDEX idx_lookup (Company, TPA, Network, Region, Dropdown_Name(100))
);
```

**Characteristics**:
- 🔴 **Never truncated** - only INSERT/UPDATE/DELETE specific records
- 📊 Contains ~10,000 rows currently
- 🔄 Updated only when changes detected via staging comparison
- 🎯 Critical production data - protected by transaction safety

**Example Data**:
| CTN_ID | Company | TPA | Network | Region | Dropdown_Name | Selection_Value |
|--------|---------|-----|---------|--------|---------------|-----------------|
| 1 | MaxHealth | Direct | MaxHealth Network | UAE | Quotation_For | Individual |
| 2 | MaxHealth | Direct | MaxHealth Network | UAE | Quotation_For | Family |
| 3 | SUKOON INSURANCE | Direct | Sukoon Network | Dubai | Dental | Basic Coverage |

---

### 2️⃣ Medical_CTN_Cascading_Dropdown_Staging (STAGING TABLE)

**Purpose**: Temporary workspace for new extraction data before comparison

**Structure**:
```sql
CREATE TABLE Medical_CTN_Cascading_Dropdown_Staging (
    Staging_ID INT AUTO_INCREMENT PRIMARY KEY,
    Broker_ID INT,
    Company VARCHAR(100),
    TPA VARCHAR(100),
    Network VARCHAR(100),
    Region VARCHAR(100),
    Dropdown_Name TEXT,          -- Already mapped to standard name!
    Selection_Value TEXT,
    Run_ID VARCHAR(50),          -- Links to extraction run (e.g., 20260223_141939)
    Created_At DATETIME,
    
    INDEX idx_staging_company (Company),
    INDEX idx_staging_runid (Run_ID),
    INDEX idx_staging_lookup (Company, TPA, Network, Region, Dropdown_Name(100))
);
```

**Characteristics**:
- 🔄 **Cleared at START of each new run** (DELETE FROM staging)
- 📥 Receives ALREADY-MAPPED data (dropdown names standardized before insertion)
- ⏱️ Temporary - data valid only during current extraction run
- 🔍 Used for comparison with ORIGINAL table
- 📊 Contains ~500-1000 rows per run (from current extraction)
- 📈 **Tracks cleared count** - number of old records removed before upload

**Lifecycle**:
```
Run 1: [Empty] → Insert new data → Compare → Keep data
Run 2: DELETE all → Insert new data → Compare → Keep data
Run 3: DELETE all → Insert new data → Compare → Keep data
```

**Why Keep Staging Data?**
- Allows post-run debugging
- Can re-run comparison without re-extraction
- Provides snapshot of what was extracted

---

### 3️⃣ Medical_CTN_Cascading_Dropdown_Backup (BACKUP TABLE)

**Purpose**: Safety snapshot of FULL original table before applying changes

**Structure**:
```sql
CREATE TABLE Medical_CTN_Cascading_Dropdown_Backup (
    Backup_ID INT AUTO_INCREMENT PRIMARY KEY,
    Run_ID VARCHAR(50),              -- Links to extraction run
    Original_CTN_ID INT,             -- Original record's CTN_ID
    Broker_ID INT,
    Company VARCHAR(100),
    TPA VARCHAR(100),
    Network VARCHAR(100),
    Region VARCHAR(100),
    Dropdown_Name TEXT,
    Selection_Value TEXT,
    Backup_Date DATETIME,
    
    INDEX idx_backup_runid (Run_ID),
    INDEX idx_backup_date (Backup_Date),
    INDEX idx_backup_company (Company)
);
```

**Characteristics**:
- 💾 **Full table backup** - ALL rows from original table
- 🔄 Created BEFORE any changes applied
- 📅 **7-day retention** - auto-deleted after 7 days
- 🔗 Each backup linked to Run_ID
- 📊 Can contain ~70,000 rows (7 runs × ~10,000 rows)
- 📈 **Tracks cleanup count** - number of old backups removed (>7 days)
- 📈 **Tracks backup count** - number of new backup records created

**Backup Strategy**:
```sql
-- STEP 1: Backup entire original table
INSERT INTO Backup_Table (Run_ID, Original_CTN_ID, Company, TPA, ...)
SELECT '20260223_141939', CTN_ID, Company, TPA, ...
FROM Original_Table;

-- STEP 2: Auto-cleanup old backups
DELETE FROM Backup_Table 
WHERE Backup_Date < DATE_SUB(NOW(), INTERVAL 7 DAY);
```

**Recovery Example**:
```sql
-- Restore data from specific run
SELECT * FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Run_ID = '20260223_141939'
ORDER BY Original_CTN_ID;
```

---

### 4️⃣ Medical_CTN_Cascading_Dropdown_Audit (AUDIT TABLE)

**Purpose**: Permanent change history log - tracks every modification

**Structure**:
```sql
CREATE TABLE Medical_CTN_Cascading_Dropdown_Audit (
    Audit_ID INT AUTO_INCREMENT PRIMARY KEY,
    Run_ID VARCHAR(50),
    Change_Type ENUM('INSERT', 'UPDATE', 'DELETE'),
    Company VARCHAR(100),
    TPA VARCHAR(100),
    Network VARCHAR(100),
    Region VARCHAR(100),
    Dropdown_Name TEXT,
    Old_Value TEXT,              -- NULL for INSERT
    New_Value TEXT,              -- NULL for DELETE
    Difference_Type VARCHAR(50), -- VALUE_CHANGE, WHITESPACE_CHANGE, CASE_CHANGE
    Changed_At DATETIME,
    
    INDEX idx_audit_runid (Run_ID),
    INDEX idx_audit_date (Changed_At),
    INDEX idx_audit_company (Company),
    INDEX idx_audit_type (Change_Type)
);
```

**Characteristics**:
- 🔒 **Permanent storage** - never auto-deleted
- 📝 Logs INSERT/UPDATE/DELETE operations
- 🔍 Tracks old and new values for comparison
- ⏰ Timestamp of every change
- 📊 Grows continuously (append-only)
- 📈 **Tracks audit count** - number of change records logged per run

**What Gets Logged**:

| Change Type | Old_Value | New_Value | Example |
|-------------|-----------|-----------|---------|
| **INSERT** | NULL | "Individual" | New dropdown value added |
| **UPDATE** | "Individual " | "Individual" | Whitespace removed |
| **DELETE** | "Family" | NULL | Dropdown value removed |

**Example Audit Records**:
```sql
-- New record added
Audit_ID: 1
Run_ID: 20260223_141939
Change_Type: INSERT
Company: MaxHealth
Dropdown_Name: Quotation_For
Old_Value: NULL
New_Value: Individual
Difference_Type: NULL
Changed_At: 2026-02-23 14:19:45

-- Value updated (whitespace change)
Audit_ID: 2
Run_ID: 20260223_141939
Change_Type: UPDATE
Company: MaxHealth
Dropdown_Name: Quotation_For
Old_Value: "Individual "  (with trailing space)
New_Value: "Individual"
Difference_Type: WHITESPACE_CHANGE
Changed_At: 2026-02-23 14:19:45

-- Record deleted
Audit_ID: 3
Run_ID: 20260223_141939
Change_Type: DELETE
Company: MaxHealth
Dropdown_Name: Coverage_Type
Old_Value: "Legacy Plan"
New_Value: NULL
Difference_Type: NULL
Changed_At: 2026-02-23 14:19:45
```

---

### 5️⃣ Medical_CTN_Portal_Field_Mapping (MAPPING TABLE)

**Purpose**: Maps portal-specific dropdown names to standardized database names

**Structure**:
```sql
CREATE TABLE Medical_CTN_Portal_Field_Mapping (
    Mapping_ID INT AUTO_INCREMENT PRIMARY KEY,
    Dropdown_Name VARCHAR(100),      -- Standard database field name
    MaxHealth VARCHAR(100),          -- MaxHealth portal's name
    Sukoon VARCHAR(100),             -- Sukoon portal's name
    Qatar VARCHAR(100),              -- Qatar Insurance portal's name
    ADNIC VARCHAR(100),              -- ADNIC portal's name
    `Liva Globalcare` VARCHAR(100),  -- Liva/NLGI portal's name
    -- ... other portal columns ...
    
    INDEX idx_dropdown_name (Dropdown_Name)
);
```

**Characteristics**:
- 📚 **Reference data** - rarely changes
- 🔄 Pre-populated by admin
- 🎯 Used BEFORE staging upload
- 🌐 One row per standard dropdown field

**Example Mapping Data**:

| Dropdown_Name (Standard) | MaxHealth | Sukoon | Liva Globalcare | ADNIC |
|-------------------------|-----------|---------|-----------------|-------|
| Quotation_For | Quotation For | Policy_Holder_Type | Quotation For | PolicyType |
| Dental | Dental Benefit | Dental_Coverage | Dental Benefit | DentalPlan |
| Maternity | Maternity Cover | Maternity_Benefit | Maternity | MaternityBenefit |
| Region | Location | Area | Geographic_Region | Region |

**How Mapping Works**:
```python
# Portal extracts "Quotation For" (MaxHealth-specific name)
portal_name = "Quotation For"

# Load mapping for MaxHealth
mappings = load_dropdown_mappings(db, "MaxHealth")
# Returns: {"Quotation For": "Quotation_For", ...}

# Apply mapping
standard_name = mappings.get("Quotation For", "Quotation For")
# Result: "Quotation_For" (standardized)

# This standardized name is used in staging and original tables
```

---

## 🔄 Complete Data Flow

### Phase 1: Extraction & Preparation (upload_extracted.py)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Extract Data from Portal APIs                          │
└─────────────────────────────────────────────────────────────────┘
         ↓
[MaxHealth API] → extracted_data/20260223_141939/maxhealth/dropdown_data.txt
[Sukoon API]   → extracted_data/20260223_141939/sukoon/dropdown_data.txt
[Qatar API]    → extracted_data/20260223_141939/qatar/dropdown_data.txt

Example extracted record (JSON):
{
  "Broker_ID": 1,
  "Company": "MaxHealth",
  "TPA": "Direct",
  "Network": "MaxHealth Network",
  "Region": "UAE",
  "Dropdown_Name": "Quotation For",  ← Portal-specific name!
  "Selection_Value": "Individual"
}

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Parse Files & Group by Company                         │
└─────────────────────────────────────────────────────────────────┘
         ↓
records_by_company = {
    "MaxHealth": [record1, record2, ...],
    "SUKOON INSURANCE": [record3, record4, ...],
    "QATAR INSURANCE CO": [record5, record6, ...]
}

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Standardize Company Names                              │
└─────────────────────────────────────────────────────────────────┘
         ↓
"Sukoon" → "SUKOON INSURANCE"
"Qatar" → "QATAR INSURANCE CO"
"MaxHealth" → "MaxHealth"  (already standard)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Load Dropdown Mappings (Critical!)                     │
└─────────────────────────────────────────────────────────────────┘
         ↓
For each company:
    mappings = load_dropdown_mappings(db, company)
    
    MaxHealth mappings:
    {
        "Quotation For": "Quotation_For",
        "Policy_Holder_Type": "Quotation_For",
        "Dental Benefit": "Dental",
        ...
    }

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Apply Mappings - Transform Names                       │
└─────────────────────────────────────────────────────────────────┘
         ↓
BEFORE MAPPING:
{
  "Company": "MaxHealth",
  "Dropdown_Name": "Quotation For",  ← Portal name
  "Selection_Value": "Individual"
}

AFTER MAPPING:
{
  "Company": "MaxHealth",
  "Dropdown_Name": "Quotation_For",  ← Standard name ✓
  "Selection_Value": "Individual"
}

┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Filter Unwanted Dropdowns                              │
└─────────────────────────────────────────────────────────────────┘
         ↓
Remove records where Dropdown_Name in ["TPA", "Network", ""]
These are hierarchy fields, not actual dropdown values

┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: Pass to Staging Upload Module                          │
└─────────────────────────────────────────────────────────────────┘
         ↓
staged_upload_to_database(
    all_records,           ← Already mapped!
    companies,
    dropdown_names_by_company
)
```

---

### Phase 2: Staging & Comparison (staging_upload.py)

**IMPORTANT BUG FIX**: The `process_upload()` method must save counts BEFORE calling `compare_tables()` because `compare_tables()` creates a brand new ChangeReport object, wiping previously set values.

```python
# CORRECT APPROACH (Fixed):
def process_upload(self, records, companies, dropdown_names):
    # 1. Save counts BEFORE compare_tables
    old_backups_removed = self.cleanup_old_backups()  # Returns count
    backup_count = self.create_backup(companies, dropdown_names)  # Returns count
    staging_inserted, staging_cleared = self.upload_to_staging(records)  # Returns tuple
    
    # 2. compare_tables creates NEW ChangeReport (wipes old values!)
    report = self.compare_tables(companies, dropdown_names)
    
    # 3. Restore counts AFTER compare_tables
    report.backup_count = backup_count
    report.old_backups_removed = old_backups_removed
    report.staging_cleared = staging_cleared
    report.staging_count = staging_inserted
    
    # 4. Apply changes
    self.apply_changes(report)
    
    # 5. Log to audit (returns count)
    audit_count = self.log_to_audit(report)
    report.audit_records_logged = audit_count
    
    return report
```

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Clear Previous Staging Data                            │
└─────────────────────────────────────────────────────────────────┘
         ↓
DELETE FROM Medical_CTN_Cascading_Dropdown_Staging;
-- Ensures clean slate for new extraction
-- Returns: Number of records cleared (0 on first run, ~500-1000 on subsequent)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Upload to Staging Table                                │
└─────────────────────────────────────────────────────────────────┘
         ↓
INSERT INTO Medical_CTN_Cascading_Dropdown_Staging 
(Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value, Run_ID)
VALUES 
(1, 'MaxHealth', 'Direct', 'MaxHealth Network', 'UAE', 'Quotation_For', 'Individual', '20260223_141939'),
(1, 'MaxHealth', 'Direct', 'MaxHealth Network', 'UAE', 'Quotation_For', 'Family', '20260223_141939'),
...

Result: ~500-1000 new records in staging
Returns: Tuple (rows_inserted, rows_cleared_before_insert)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3A: Create Full Table Backup (File)                       │
└─────────────────────────────────────────────────────────────────┘
         ↓
Option 1: mysqldump (if available)
mysqldump Medical_CTN_Cascading_Dropdown_Lifecare > 
    database/backups/Medical_CTN_Cascading_Dropdown_Lifecare_backup_20260223_141939.sql

Option 2: Python fallback (CSV)
    database/backups/Medical_CTN_Cascading_Dropdown_Lifecare_backup_20260223_141939.csv

Retention: 30 days (auto-cleanup old files)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3B: Create Database Backup (Full Table)                   │
└─────────────────────────────────────────────────────────────────┘
         ↓
-- First: Cleanup old backups (>7 days)
DELETE FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Backup_Date < DATE_SUB(NOW(), INTERVAL 7 DAY);
-- Returns: Number of old backup records removed

-- Then: Create new backup
INSERT INTO Medical_CTN_Cascading_Dropdown_Backup 
(Run_ID, Original_CTN_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value, Backup_Date)
SELECT 
    '20260223_141939',  -- Run_ID
    CTN_ID,             -- Original ID
    Company, TPA, Network, Region, Dropdown_Name, Selection_Value,
    NOW()
FROM Medical_CTN_Cascading_Dropdown_Lifecare;

Result: ALL ~10,000 rows backed up with Run_ID linkage
Returns: Number of new backup records created
Retention: 7 days (auto-cleanup)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Compare Staging ↔ Original (Smart Detection)           │
└─────────────────────────────────────────────────────────────────┘
         ↓
SQL Query 1: Find NEW records (in staging only)
-------------------------------------------------
SELECT s.* FROM Staging s
LEFT JOIN Original o ON (
    s.Company = o.Company AND
    s.TPA = o.TPA AND
    s.Network = o.Network AND
    s.Region = o.Region AND
    s.Dropdown_Name = o.Dropdown_Name AND
    s.Selection_Value = o.Selection_Value
)
WHERE o.CTN_ID IS NULL;

Result: Records that don't exist in original
Example: New "Corporate" value for Quotation_For


SQL Query 2: Find DELETED records (in original only)
-----------------------------------------------------
SELECT o.* FROM Original o
LEFT JOIN Staging s ON (
    o.Company = s.Company AND
    o.TPA = s.TPA AND
    o.Network = s.Network AND
    o.Region = s.Region AND
    o.Dropdown_Name = s.Dropdown_Name AND
    o.Selection_Value = s.Selection_Value
)
WHERE s.Staging_ID IS NULL
AND o.Company IN ('MaxHealth', 'SUKOON INSURANCE', ...)  -- Only processed companies
AND o.Dropdown_Name IN ('Quotation_For', 'Dental', ...);  -- Only extracted dropdowns

Result: Records removed from portal
Example: "Legacy Plan" no longer in portal API


SQL Query 3: Find MODIFIED records (same key, different value)
---------------------------------------------------------------
SELECT 
    o.CTN_ID,
    o.Selection_Value as old_value,
    s.Selection_Value as new_value
FROM Original o
INNER JOIN Staging s ON (
    o.Company = s.Company AND
    o.TPA = s.TPA AND
    o.Network = s.Network AND
    o.Region = s.Region AND
    o.Dropdown_Name = s.Dropdown_Name
)
WHERE o.Selection_Value != s.Selection_Value;  -- Different values

Result: Same dropdown, different value
Example: "Individual " (with space) → "Individual" (trimmed)

Difference Type Detection:
- WHITESPACE_CHANGE: Spaces added/removed
- CASE_CHANGE: Capitalization changed
- INTERNAL_WHITESPACE: Spacing within text changed
- VALUE_CHANGE: Actual content changed


SQL Query 4: Find UNCHANGED records (exact match)
--------------------------------------------------
SELECT COUNT(*) FROM Original o
INNER JOIN Staging s ON (
    o.Company = s.Company AND
    o.TPA = s.TPA AND
    o.Network = s.Network AND
    o.Region = s.Region AND
    o.Dropdown_Name = s.Dropdown_Name AND
    o.Selection_Value = s.Selection_Value  -- Exact match
);

Result: Count of records that match exactly

┌─────────────────────────────────────────────────────────────────┐
│ COMPARISON RESULTS                                              │
└─────────────────────────────────────────────────────────────────┘
ChangeReport object:
- new_records: [RecordChange(...), ...]          → 15 new values
- modified_records: [RecordChange(...), ...]     → 3 whitespace fixes
- deleted_records: [RecordChange(...), ...]      → 2 removed values
- unchanged_count: 480                           → No action needed
- old_backups_removed: int                       → Old backups deleted (>7 days)
- staging_cleared: int                           → Old staging records cleared
- audit_records_logged: int                      → Audit entries created
- backup_count: int                              → New backup records created
- staging_count: int                             → Staging records uploaded

Total changes: 15 + 3 + 2 = 20
Efficiency: Only 20 DB operations instead of 500!

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Apply Changes (Transaction Protected)                  │
└─────────────────────────────────────────────────────────────────┘
         ↓
BEGIN TRANSACTION;

-- Insert NEW records
INSERT INTO Medical_CTN_Cascading_Dropdown_Lifecare
(Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
VALUES
(1, 'MaxHealth', 'Direct', 'MaxHealth Network', 'UAE', 'Quotation_For', 'Corporate'),
...
-- 15 INSERT queries

-- Update MODIFIED records
UPDATE Medical_CTN_Cascading_Dropdown_Lifecare
SET Selection_Value = 'Individual',  -- Remove trailing space
    Updated_At = NOW()
WHERE CTN_ID = 1234;
...
-- 3 UPDATE queries

-- Delete REMOVED records
DELETE FROM Medical_CTN_Cascading_Dropdown_Lifecare
WHERE CTN_ID IN (5678, 5679);
-- 2 DELETE queries

COMMIT;  -- All or nothing!

┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Log to Audit Trail                                     │
└─────────────────────────────────────────────────────────────────┘
         ↓
INSERT INTO Medical_CTN_Cascading_Dropdown_Audit
(Run_ID, Change_Type, Company, TPA, Network, Region, Dropdown_Name, Old_Value, New_Value, Difference_Type, Changed_At)
VALUES
-- For NEW records
('20260223_141939', 'INSERT', 'MaxHealth', 'Direct', 'MaxHealth Network', 'UAE', 'Quotation_For', NULL, 'Corporate', NULL, NOW()),

-- For MODIFIED records
('20260223_141939', 'UPDATE', 'MaxHealth', 'Direct', 'MaxHealth Network', 'UAE', 'Quotation_For', 'Individual ', 'Individual', 'WHITESPACE_CHANGE', NOW()),

-- For DELETED records
('20260223_141939', 'DELETE', 'MaxHealth', 'Direct', 'MaxHealth Network', 'UAE', 'Coverage_Type', 'Legacy Plan', NULL, NULL, NOW()),
...

Result: 20 audit records permanently logged
Returns: Number of audit records created (20 in this example)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: Return Complete Report                                 │
└─────────────────────────────────────────────────────────────────┘
         ↓
ChangeReport with all tracking data:
- Comparison results (new/modified/deleted/unchanged)
- old_backups_removed: 0 (or count if >7 days exist)
- staging_cleared: 906 (from previous run)
- backup_count: 10,848 (full table backup)
- staging_count: 500 (newly uploaded)
- audit_records_logged: 20 (changes logged)

This ChangeReport flows to:
- PDF Report Generator → Database Operations Summary section
- Email Notifier → Database Operations HTML grid

-- Cleanup happens BEFORE backup creation (see STEP 3B)
-- Delete old backup files (30 days)
Files older than 30 days removed from database/backups/

-- Keep staging data for debugging (not deleted)
```

---

## 🔄 Dropdown Name Mapping Logic

### Why Mapping is Needed

Each insurance portal uses **different names** for the same dropdown field:

| Standard Name | MaxHealth | Sukoon | Liva Globalcare | ADNIC |
|---------------|-----------|---------|-----------------|-------|
| Quotation_For | "Quotation For" | "Policy_Holder_Type" | "Quotation For" | "PolicyType" |

**Without mapping**: Database would have 4 separate fields  
**With mapping**: Database has 1 standardized field with 4 different portal values

### Mapping Process

```python
# 1. Load mappings for company
mappings = load_dropdown_mappings(db, "MaxHealth")
# Returns: {"Quotation For": "Quotation_For", "Dental Benefit": "Dental", ...}

# 2. Apply to each record
for record in records:
    portal_name = record["Dropdown_Name"]  # "Quotation For"
    
    if portal_name in mappings:
        record["Dropdown_Name"] = mappings[portal_name]  # "Quotation_For"
        # Record is MAPPED
    else:
        # Record is UNMAPPED
        if ONLY_UPLOAD_MAPPED:
            # Skip this record
            continue
        else:
            # Keep original name
            pass
```

### Configuration Options

**Option 1: ONLY_UPLOAD_MAPPED = True (Recommended)**
- Only mapped dropdown names are uploaded
- Unmapped names are skipped
- Ensures database consistency
- Example: If "NewField" has no mapping → skipped

**Option 2: ONLY_UPLOAD_MAPPED = False**
- Both mapped and unmapped names uploaded
- Unmapped keep their original portal names
- Useful during mapping table development
- Example: If "NewField" has no mapping → uploaded as "NewField"

### Skip Dropdowns

Some dropdown names are **hierarchy fields**, not actual values:

```python
SKIP_DROPDOWN_NAMES = {"", "TPA", "Network"}
```

These are filtered out **before upload** because:
- They're used in query structure, not as dropdown options
- TPA/Network expansion already done in formatters
- Empty names are invalid data

---

## 💾 Backup Strategy

The system employs a **dual backup approach** for maximum safety:

### Backup Type 1: Full Table File Backup

**Location**: `database/backups/`  
**Format**: `.sql` or `.csv`  
**Retention**: 30 days  
**Created**: Before EVERY extraction run  

**Files Created**:
```
database/backups/
├── Medical_CTN_Cascading_Dropdown_Lifecare_backup_20260223_141939.sql
├── Medical_CTN_Cascading_Dropdown_Lifecare_backup_20260223_145607.sql
├── Medical_CTN_Cascading_Dropdown_Lifecare_backup_20260223_152714.sql
└── ... (auto-cleanup after 30 days)
```

**Advantages**:
- ✅ Complete table snapshot
- ✅ Can restore entire table with single SQL file
- ✅ Independent of database (file-based)
- ✅ Can be archived to external storage

**How It Works**:
```python
# Check if mysqldump is available
if mysqldump_available:
    # Use native MySQL dump (faster, more reliable)
    mysqldump -u admin -p WebDB Medical_CTN_Cascading_Dropdown_Lifecare > backup.sql
else:
    # Use Python fallback (SELECT + write to CSV)
    SELECT * FROM Medical_CTN_Cascading_Dropdown_Lifecare → backup.csv
```

### Backup Type 2: Full Table Database Backup

**Table**: `Medical_CTN_Cascading_Dropdown_Backup`  
**Retention**: 7 days  
**Created**: Before EVERY extraction run  

**How It Works**:
```sql
-- Backup ALL rows from original table
INSERT INTO Medical_CTN_Cascading_Dropdown_Backup 
(Run_ID, Original_CTN_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value, Backup_Date)
SELECT 
    '20260223_141939',  -- Current run ID
    CTN_ID,             -- Link to original record
    Company, TPA, Network, Region, Dropdown_Name, Selection_Value,
    NOW()
FROM Medical_CTN_Cascading_Dropdown_Lifecare;
```

**Advantages**:
- ✅ SQL-queryable (can analyze backup data)
- ✅ Run_ID linkage (know which extraction triggered backup)
- ✅ Can restore specific records
- ✅ Fast recovery with SQL queries

**Backup Comparison**:

| Feature | File Backup | Database Backup |
|---------|-------------|-----------------|
| **Retention** | 30 days | 7 days |
| **Format** | .sql / .csv | Database table |
| **Storage** | File system | Database |
| **Queryable** | No (must restore first) | Yes (direct SQL) |
| **Full Restore** | Easy (source backup.sql) | Requires data copy |
| **Partial Restore** | Manual extraction | Easy (WHERE clause) |
| **External Archive** | Easy | Requires export |

### Recovery Examples

**Scenario 1: Restore entire table from file backup**
```bash
mysql -u admin -p WebDB < database/backups/Medical_CTN_Cascading_Dropdown_Lifecare_backup_20260223_141939.sql
```

**Scenario 2: Restore specific company from database backup**
```sql
-- See what was backed up for MaxHealth in run X
SELECT * FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Run_ID = '20260223_141939'
AND Company = 'MaxHealth';

-- Restore those records to original table
INSERT INTO Medical_CTN_Cascading_Dropdown_Lifecare
(Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
SELECT Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value
FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Run_ID = '20260223_141939'
AND Company = 'MaxHealth';
```

**Scenario 3: Compare current vs backup**
```sql
-- Find what changed since backup
SELECT 
    b.Dropdown_Name,
    b.Selection_Value as backup_value,
    o.Selection_Value as current_value
FROM Medical_CTN_Cascading_Dropdown_Backup b
LEFT JOIN Medical_CTN_Cascading_Dropdown_Lifecare o 
    ON b.Original_CTN_ID = o.CTN_ID
WHERE b.Run_ID = '20260223_141939'
AND (o.CTN_ID IS NULL OR b.Selection_Value != o.Selection_Value);
```

---

## 📝 Audit Trail System

The audit table provides a **permanent, tamper-evident log** of all database changes.

### What Gets Logged

Every modification to the original table is logged with:
- 🔑 **Run_ID**: Which extraction run made the change
- 📝 **Change_Type**: INSERT / UPDATE / DELETE
- 🏢 **Context**: Company, TPA, Network, Region, Dropdown_Name
- 🔄 **Values**: Old value → New value
- 🔍 **Difference Type**: What kind of change occurred
- ⏰ **Timestamp**: Exact time of change

### Change Type Examples

#### INSERT (New Records)
```sql
Audit_ID: 1
Run_ID: 20260223_141939
Change_Type: INSERT
Company: MaxHealth
TPA: Direct
Network: MaxHealth Network
Region: UAE
Dropdown_Name: Quotation_For
Old_Value: NULL                    ← Nothing before
New_Value: "Corporate"             ← New value added
Difference_Type: NULL
Changed_At: 2026-02-23 14:19:45
```

**Meaning**: A new dropdown value "Corporate" was added for Quotation_For field

---

#### UPDATE (Modified Records)

**Example 1: Whitespace Change**
```sql
Audit_ID: 2
Run_ID: 20260223_141939
Change_Type: UPDATE
Company: MaxHealth
Dropdown_Name: Quotation_For
Old_Value: "Individual "           ← Trailing space
New_Value: "Individual"            ← Trimmed
Difference_Type: WHITESPACE_CHANGE
Changed_At: 2026-02-23 14:19:45
```

**Example 2: Value Change**
```sql
Audit_ID: 3
Run_ID: 20260223_141939
Change_Type: UPDATE
Company: SUKOON INSURANCE
Dropdown_Name: Dental
Old_Value: "Basic"
New_Value: "Basic Coverage"
Difference_Type: VALUE_CHANGE
Changed_At: 2026-02-23 14:19:45
```

---

#### DELETE (Removed Records)
```sql
Audit_ID: 4
Run_ID: 20260223_141939
Change_Type: DELETE
Company: MaxHealth
Dropdown_Name: Coverage_Type
Old_Value: "Legacy Plan"           ← What was removed
New_Value: NULL                    ← No longer exists
Difference_Type: NULL
Changed_At: 2026-02-23 14:19:45
```

**Meaning**: "Legacy Plan" was removed from the portal (no longer available)

---

### Audit Queries

**Find all changes for a specific run**:
```sql
SELECT * FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Run_ID = '20260223_141939'
ORDER BY Changed_At;
```

**Find all changes for a company**:
```sql
SELECT * FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Company = 'MaxHealth'
ORDER BY Changed_At DESC;
```

**Find history of a specific dropdown**:
```sql
SELECT 
    Run_ID,
    Change_Type,
    Old_Value,
    New_Value,
    Difference_Type,
    Changed_At
FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Company = 'MaxHealth'
AND Dropdown_Name = 'Quotation_For'
ORDER BY Changed_At DESC;
```

**Count changes by type**:
```sql
SELECT 
    Change_Type,
    COUNT(*) as count
FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Run_ID = '20260223_141939'
GROUP BY Change_Type;
```

**Find subtle changes (whitespace/case only)**:
```sql
SELECT * FROM Medical_CTN_Cascading_Dropdown_Audit
WHERE Difference_Type IN ('WHITESPACE_CHANGE', 'CASE_CHANGE', 'INTERNAL_WHITESPACE')
ORDER BY Changed_At DESC;
```

---

## ⚙️ Configuration Options

All settings are in `staging_config.py`:

### Table Names
```python
ORIGINAL_TABLE = "Medical_CTN_Cascading_Dropdown_Lifecare"
STAGING_TABLE = "Medical_CTN_Cascading_Dropdown_Staging"
BACKUP_TABLE = "Medical_CTN_Cascading_Dropdown_Backup"
AUDIT_TABLE = "Medical_CTN_Cascading_Dropdown_Audit"
MAPPING_TABLE = "Medical_CTN_Portal_Field_Mapping"
```

### Backup Settings
```python
# Database backup retention
BACKUP_RETENTION_DAYS = 7

# Enable full table file backup
ENABLE_FULL_TABLE_BACKUP = True

# Backup format: 'sql', 'csv', or 'both'
FULL_BACKUP_FORMAT = 'sql'

# Backup directory
FULL_BACKUP_DIR = 'database/backups'

# File backup retention
FULL_BACKUP_RETENTION_DAYS = 30
```

### Upload Settings
```python
# Only upload mapped dropdown names?
ONLY_UPLOAD_MAPPED = True  # Recommended

# Skip these dropdown names
SKIP_DROPDOWN_NAMES = {"", "TPA", "Network"}

# Batch size for inserts
BATCH_SIZE = 100
```

### Company Name Mapping
```python
COMPANY_NAME_MAPPING = {
    "Sukoon": "SUKOON INSURANCE",
    "Qatar": "QATAR INSURANCE CO",
    "Takaful": "TAKAFUL EMARAT",
    "ADNIC": "ADNIC",
    "MaxHealth": "MaxHealth",
}
```

---

## 🛡️ Error Handling & Recovery

### Transaction Safety

All database modifications are wrapped in transactions:

```python
try:
    db.begin_transaction()
    
    # 1. Clear staging
    # 2. Insert to staging
    # 3. Create backup
    # 4. Compare
    # 5. Apply changes
    # 6. Log to audit
    
    db.commit()  # All or nothing!
    
except Exception as e:
    db.rollback()  # Undo everything
    print(f"Error: {e}")
    # Original table unchanged
```

**Result**: If ANY step fails, the entire operation is rolled back. Production table remains untouched.

### Backup Recovery

If something goes wrong **after** commit, you can recover from backups:

**Recent Issue (< 7 days)**:
```sql
-- View backup for problematic run
SELECT * FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Run_ID = '20260223_141939';

-- Restore specific records if needed
```

**Older Issue (< 30 days)**:
```bash
# Restore from file backup
mysql -u admin -p WebDB < database/backups/Medical_CTN_Cascading_Dropdown_Lifecare_backup_20260223_141939.sql
```

### Common Issues & Solutions

**Issue 1: "Duplicate key" error during INSERT**
- **Cause**: Record already exists in original table
- **Solution**: System should detect in comparison step. Check staging comparison logic.
- **Recovery**: Automatic rollback, no damage done

**Issue 2: "Column 'Dropdown_Name' too long"**
- **Cause**: Dropdown name > TEXT limit (unlikely)
- **Solution**: Truncate or split data
- **Recovery**: Automatic rollback

**Issue 3: "No changes detected but portal shows new data"**
- **Cause**: Dropdown name not mapped, and ONLY_UPLOAD_MAPPED = True
- **Solution**: Add mapping to Medical_CTN_Portal_Field_Mapping table
- **Recovery**: Re-run extraction after adding mapping

**Issue 4: "Staging table locked"**
- **Cause**: Previous transaction still running
- **Solution**: Wait for previous run to complete, or kill long-running query
- **Recovery**: Safe - staging is temporary

---

## 📊 Complete Table Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          EXTRACTION FLOW                                │
└─────────────────────────────────────────────────────────────────────────┘

                    [Portal APIs]
                         ↓
                   Extract .txt files
                         ↓
              ┌──────────────────────┐
              │  Dropdown Mapping    │
              │  Medical_CTN_Portal_ │
              │  Field_Mapping       │ ← Reference data (pre-populated)
              └──────────┬───────────┘
                         ↓
                Map portal names → standard names
                         ↓
              ┌──────────────────────┐
              │  Staging Table       │
              │  (Temporary)         │ ← Cleared each run
              │                      │
              │  NEW extraction data │
              │  MAPPED names        │
              └──────────┬───────────┘
                         ↓
                    COMPARE ↔
                         ↓
              ┌──────────────────────┐
              │  Original Table      │
              │  (Production)        │ ← Live data
              │                      │
              │  Medical_CTN_        │
              │  Cascading_Dropdown_ │
              │  Lifecare            │
              └──────────┬───────────┘
                         ↓
              Detect: NEW / MODIFIED / DELETED / UNCHANGED
                         ↓
              ┌──────────────────────┐
              │  Backup Table        │
              │  (7-day retention)   │ ← Full table snapshot BEFORE changes
              └──────────────────────┘
                         ↓
              Apply changes to Original Table
                         ↓
              ┌──────────────────────┐
              │  Audit Table         │
              │  (Permanent)         │ ← Log every INSERT/UPDATE/DELETE
              │                      │
              │  Full change history │
              └──────────────────────┘
                         ↓
              ┌──────────────────────┐
              │  File Backup         │
              │  (30-day retention)  │ ← .sql/.csv files
              │                      │
              │  database/backups/   │
              └──────────────────────┘
```

---

## 📈 Performance Characteristics

### Typical Run Statistics

**Scenario**: Daily extraction with 3 portals

| Metric | Value |
|--------|-------|
| **Portals Extracted** | 3 (MaxHealth, Sukoon, Qatar) |
| **Records Extracted** | ~500 |
| **Staging Upload** | ~2 seconds |
| **Backup Creation** | ~10-15 seconds (full table) |
| **Comparison** | ~5 seconds |
| **Actual Changes** | ~20 (96% unchanged!) |
| **Apply Changes** | ~1 second |
| **Audit Logging** | ~0.5 seconds |
| **Total Duration** | ~20-25 seconds |

**Efficiency Gain**:
- Without staging: 500 DELETE + 500 INSERT = 1,000 operations
- With staging: 20 changes = **98% fewer operations!**

### Table Sizes

| Table | Typical Size | Growth Rate |
|-------|--------------|-------------|
| **Original (Lifecare)** | ~10,000 rows | Slow (only changes) |
| **Staging** | ~500 rows | Reset each run |
| **Backup** | ~70,000 rows | +10,000/run, -10,000/week |
| **Audit** | Growing | +20 rows/run (permanent) |
| **Mapping** | ~50 rows | Rare updates |

---

## 🎯 Best Practices

### 1. Always Review Change Report
Check the PDF report after each extraction to verify:
- ✅ Expected changes detected
- ✅ No unexpected deletions
- ✅ Whitespace changes are legitimate

### 2. Monitor Audit Table Growth
```sql
-- Check audit table size monthly
SELECT COUNT(*) FROM Medical_CTN_Cascading_Dropdown_Audit;

-- Optional: Archive old audit data after 6 months
```

### 3. Keep Backups External
Periodically copy `database/backups/` to external storage:
```bash
# Weekly backup archive
tar -czf backups_archive_2026-02-23.tar.gz database/backups/
```

### 4. Update Mapping Table Proactively
When portals add new dropdown fields:
```sql
-- Add new mapping
INSERT INTO Medical_CTN_Portal_Field_Mapping 
(Dropdown_Name, MaxHealth, Sukoon, Qatar)
VALUES 
('New_Field', 'New Field Name', 'NewField', 'new_field');
```

### 5. Verify Staging Comparison
If you suspect issues:
```sql
-- Manual comparison check
SELECT 
    (SELECT COUNT(*) FROM Medical_CTN_Cascading_Dropdown_Staging) as staging_count,
    (SELECT COUNT(*) FROM Medical_CTN_Cascading_Dropdown_Lifecare WHERE Company IN (...)) as original_count;
```

---

## 🔍 Troubleshooting

### No Changes Detected (But Portal Has New Data)

**Possible Causes**:
1. Dropdown name not mapped + `ONLY_UPLOAD_MAPPED = True`
2. Data filtered by `SKIP_DROPDOWN_NAMES`
3. Whitespace differences not detected

**Solution**:
```sql
-- Check if data reached staging
SELECT * FROM Medical_CTN_Cascading_Dropdown_Staging
WHERE Dropdown_Name = 'YourFieldName';

-- Check mapping
SELECT * FROM Medical_CTN_Portal_Field_Mapping
WHERE MaxHealth LIKE '%YourFieldName%';
```

### Unexpected Deletions

**Cause**: Portal API returned incomplete data (API error)

**Recovery**:
```sql
-- Restore from backup
SELECT * FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Run_ID = '20260223_141939'
AND Company = 'AffectedCompany';
```

### Staging Table Locked

**Cause**: Previous transaction still running

**Solution**:
```sql
-- Check running transactions
SHOW PROCESSLIST;

-- Kill long-running query if needed
KILL <process_id>;
```

---

## 📚 SQL Script Reference

### Create All Tables
```bash
mysql -u admin -p WebDB < database/sql_scripts/create_staging_tables.sql
```

### Manual Cleanup
```sql
-- Cleanup old backups
DELETE FROM Medical_CTN_Cascading_Dropdown_Backup 
WHERE Backup_Date < DATE_SUB(NOW(), INTERVAL 7 DAY);

-- Cleanup old audit (optional - not recommended)
DELETE FROM Medical_CTN_Cascading_Dropdown_Audit 
WHERE Changed_At < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### View Recent Activity
```sql
-- Recent changes
SELECT * FROM Medical_CTN_Cascading_Dropdown_Audit
ORDER BY Changed_At DESC
LIMIT 100;

-- Recent backups
SELECT Run_ID, COUNT(*) as records, Backup_Date
FROM Medical_CTN_Cascading_Dropdown_Backup
GROUP BY Run_ID, Backup_Date
ORDER BY Backup_Date DESC;
```

---

## 📞 Support

For issues or questions:
1. Check audit table for change history
2. Review backup data for affected run
3. Check PDF reports in `reports/` folder
4. Review logs in `logs/` folder

---

**Last Updated**: February 23, 2026  
**Version**: 2.0  
**Database**: WebDB (139.185.45.34)
