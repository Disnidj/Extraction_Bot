# 📊 Quick Reference: Database Tables

## Table Overview

| # | Table Name | Purpose | Cleared/Updated | Retention |
|---|------------|---------|-----------------|-----------|
| 1 | **Medical_CTN_Cascading_Dropdown_Lifecare** | Production table with live dropdown data | ❌ Never (only specific updates) | Permanent |
| 2 | **Medical_CTN_Cascading_Dropdown_Staging** | Temporary workspace for new extractions | ✅ Every run start | Until next run |
| 3 | **Medical_CTN_Cascading_Dropdown_Backup** | Full table snapshot before changes | ❌ Never (7-day auto-cleanup) | 7 days |
| 4 | **Medical_CTN_Cascading_Dropdown_Audit** | Permanent change log | ❌ Never | Permanent |
| 5 | **Medical_CTN_Portal_Field_Mapping** | Dropdown name translations | ❌ Never (manual updates) | Permanent |

---

## 1. Medical_CTN_Cascading_Dropdown_Lifecare (PRODUCTION)

```
┌─────────────┬──────────────┬───────────────────────────────────────┐
│ Column      │ Type         │ Description                           │
├─────────────┼──────────────┼───────────────────────────────────────┤
│ CTN_ID      │ INT PK       │ Primary key (auto-increment)          │
│ Broker_ID   │ INT          │ Broker identifier (usually 1)         │
│ Company     │ VARCHAR(100) │ Insurance company (standardized)      │
│ TPA         │ VARCHAR(100) │ Third Party Administrator             │
│ Network     │ VARCHAR(100) │ Network provider                      │
│ Region      │ VARCHAR(100) │ Geographic region                     │
│ Dropdown_Name│ TEXT        │ Standard dropdown field name          │
│ Selection_Value│ TEXT      │ Dropdown option value                 │
│ Created_At  │ DATETIME     │ Record creation timestamp             │
│ Updated_At  │ DATETIME     │ Last update timestamp                 │
└─────────────┴──────────────┴───────────────────────────────────────┘

📊 Current Size: ~10,000 rows
🔄 Updated By: staging_upload.py (INSERT/UPDATE/DELETE)
🎯 Purpose: Live production data used by applications
```

**Sample Data**:
```
CTN_ID: 1
Company: MaxHealth
TPA: Direct
Network: MaxHealth Network
Region: UAE
Dropdown_Name: Quotation_For
Selection_Value: Individual
```

---

## 2. Medical_CTN_Cascading_Dropdown_Staging (TEMPORARY)

```
┌─────────────┬──────────────┬───────────────────────────────────────┐
│ Column      │ Type         │ Description                           │
├─────────────┼──────────────┼───────────────────────────────────────┤
│ Staging_ID  │ INT PK       │ Primary key (auto-increment)          │
│ Broker_ID   │ INT          │ Broker identifier                     │
│ Company     │ VARCHAR(100) │ Insurance company                     │
│ TPA         │ VARCHAR(100) │ Third Party Administrator             │
│ Network     │ VARCHAR(100) │ Network provider                      │
│ Region      │ VARCHAR(100) │ Geographic region                     │
│ Dropdown_Name│ TEXT        │ Standard dropdown field name (MAPPED!)│
│ Selection_Value│ TEXT      │ Dropdown option value                 │
│ Run_ID      │ VARCHAR(50)  │ Extraction run timestamp              │
│ Created_At  │ DATETIME     │ Record creation timestamp             │
└─────────────┴──────────────┴───────────────────────────────────────┘

📊 Current Size: ~500 rows (from latest run)
🔄 Cleared: At START of each extraction run (DELETE FROM)
🎯 Purpose: Hold new data for comparison before applying
```

**Lifecycle**:
```
Run 1: [Empty] → Insert 500 rows → Compare → Keep
Run 2: DELETE ALL → Insert 500 rows → Compare → Keep
Run 3: DELETE ALL → Insert 500 rows → Compare → Keep
```

---

## 3. Medical_CTN_Cascading_Dropdown_Backup (SAFETY NET)

```
┌─────────────┬──────────────┬───────────────────────────────────────┐
│ Column      │ Type         │ Description                           │
├─────────────┼──────────────┼───────────────────────────────────────┤
│ Backup_ID   │ INT PK       │ Primary key (auto-increment)          │
│ Run_ID      │ VARCHAR(50)  │ Which run triggered this backup       │
│ Original_CTN_ID│ INT       │ Original record's CTN_ID              │
│ Broker_ID   │ INT          │ Broker identifier                     │
│ Company     │ VARCHAR(100) │ Insurance company                     │
│ TPA         │ VARCHAR(100) │ Third Party Administrator             │
│ Network     │ VARCHAR(100) │ Network provider                      │
│ Region      │ VARCHAR(100) │ Geographic region                     │
│ Dropdown_Name│ TEXT        │ Dropdown field name                   │
│ Selection_Value│ TEXT      │ Dropdown option value                 │
│ Backup_Date │ DATETIME     │ When backup was created               │
└─────────────┴──────────────┴───────────────────────────────────────┘

📊 Current Size: ~70,000 rows (7 runs × 10,000 rows)
🔄 Auto-Cleanup: DELETE WHERE Backup_Date < NOW() - 7 DAYS
🎯 Purpose: Roll back if something goes wrong
```

**How to Use**:
```sql
-- View backup for specific run
SELECT * FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Run_ID = '20260223_141939';

-- Restore specific company data
INSERT INTO Medical_CTN_Cascading_Dropdown_Lifecare (...)
SELECT Broker_ID, Company, TPA, ... 
FROM Medical_CTN_Cascading_Dropdown_Backup
WHERE Run_ID = '20260223_141939' AND Company = 'MaxHealth';
```

---

## 4. Medical_CTN_Cascading_Dropdown_Audit (HISTORY LOG)

```
┌─────────────┬──────────────┬───────────────────────────────────────┐
│ Column      │ Type         │ Description                           │
├─────────────┼──────────────┼───────────────────────────────────────┤
│ Audit_ID    │ INT PK       │ Primary key (auto-increment)          │
│ Run_ID      │ VARCHAR(50)  │ Which run made this change            │
│ Change_Type │ ENUM         │ INSERT / UPDATE / DELETE              │
│ Company     │ VARCHAR(100) │ Insurance company                     │
│ TPA         │ VARCHAR(100) │ Third Party Administrator             │
│ Network     │ VARCHAR(100) │ Network provider                      │
│ Region      │ VARCHAR(100) │ Geographic region                     │
│ Dropdown_Name│ TEXT        │ Dropdown field name                   │
│ Old_Value   │ TEXT         │ Value before change (NULL for INSERT) │
│ New_Value   │ TEXT         │ Value after change (NULL for DELETE)  │
│ Difference_Type│ VARCHAR(50)│ WHITESPACE_CHANGE, VALUE_CHANGE, etc.│
│ Changed_At  │ DATETIME     │ When change occurred                  │
└─────────────┴──────────────┴───────────────────────────────────────┘

📊 Current Size: Growing (append-only)
🔄 Never Cleared: Permanent audit history
🎯 Purpose: Track every change for compliance/debugging
```

**Sample Audit Records**:

**INSERT** (New value added):
```
Audit_ID: 1
Run_ID: 20260223_141939
Change_Type: INSERT
Company: MaxHealth
Dropdown_Name: Quotation_For
Old_Value: NULL
New_Value: "Corporate"
Difference_Type: NULL
Changed_At: 2026-02-23 14:19:45
```

**UPDATE** (Value changed):
```
Audit_ID: 2
Run_ID: 20260223_141939
Change_Type: UPDATE
Company: MaxHealth
Dropdown_Name: Quotation_For
Old_Value: "Individual "  (with space)
New_Value: "Individual"
Difference_Type: WHITESPACE_CHANGE
Changed_At: 2026-02-23 14:19:46
```

**DELETE** (Value removed):
```
Audit_ID: 3
Run_ID: 20260223_141939
Change_Type: DELETE
Company: MaxHealth
Dropdown_Name: Coverage_Type
Old_Value: "Legacy Plan"
New_Value: NULL
Difference_Type: NULL
Changed_At: 2026-02-23 14:19:47
```

---

## 5. Medical_CTN_Portal_Field_Mapping (REFERENCE DATA)

```
┌─────────────┬──────────────┬───────────────────────────────────────┐
│ Column      │ Type         │ Description                           │
├─────────────┼──────────────┼───────────────────────────────────────┤
│ Mapping_ID  │ INT PK       │ Primary key (auto-increment)          │
│ Dropdown_Name│ VARCHAR(100)│ Standard database field name          │
│ MaxHealth   │ VARCHAR(100) │ MaxHealth portal's field name         │
│ Sukoon      │ VARCHAR(100) │ Sukoon portal's field name            │
│ Qatar       │ VARCHAR(100) │ Qatar Insurance portal's field name   │
│ ADNIC       │ VARCHAR(100) │ ADNIC portal's field name             │
│ Liva Globalcare│ VARCHAR(100)│ Liva/NLGI portal's field name      │
│ ... (more portal columns) ...                                      │
└─────────────┴──────────────┴───────────────────────────────────────┘

📊 Current Size: ~50 rows (one per standard dropdown field)
🔄 Updated: Manually when portals add new fields
🎯 Purpose: Translate portal-specific names to standard names
```

**Sample Mapping**:
```
Mapping_ID: 1
Dropdown_Name: "Quotation_For"      ← Standard name (in database)
MaxHealth: "Quotation For"          ← How MaxHealth calls it
Sukoon: "Policy_Holder_Type"        ← How Sukoon calls it
Qatar: "Quotation For"              ← How Qatar calls it
ADNIC: "PolicyType"                 ← How ADNIC calls it
Liva Globalcare: "Quotation For"    ← How Liva calls it
```

**How It's Used**:
```python
# Portal extracts: "Quotation For" (MaxHealth-specific)
portal_dropdown = "Quotation For"

# Load mapping
SELECT MaxHealth, Dropdown_Name 
FROM Medical_CTN_Portal_Field_Mapping
WHERE MaxHealth = "Quotation For"
# Returns: ("Quotation For", "Quotation_For")

# Apply mapping
standard_name = "Quotation_For"  ← Used in staging & original tables
```

---

## 🔄 Data Flow Summary

```
┌────────────────────┐
│   Portal APIs      │ Extract data
└─────────┬──────────┘
          ↓
┌────────────────────┐
│  Mapping Table     │ Translate portal names → standard names
└─────────┬──────────┘
          ↓
┌────────────────────┐
│  Staging Table     │ Hold new data (mapped)
└─────────┬──────────┘
          ↓
    COMPARE with Original Table
          ↓
    Detect: NEW / MODIFIED / DELETED / UNCHANGED
          ↓
┌────────────────────┐
│  Backup Table      │ Snapshot BEFORE changes (7-day safety)
└────────────────────┘
          ↓
┌────────────────────┐
│  Original Table    │ Apply changes: INSERT/UPDATE/DELETE
└─────────┬──────────┘
          ↓
┌────────────────────┐
│  Audit Table       │ Log every change (permanent)
└────────────────────┘
```

---

## 🎯 Key Concepts

### 1. Why Staging Table?
**Without Staging** (Old Approach):
- DELETE all company data
- INSERT new data
- Result: 500 DELETE + 500 INSERT = 1,000 operations

**With Staging** (Current Approach):
- Compare new vs existing
- Only update what changed
- Result: 15 INSERT + 3 UPDATE + 2 DELETE = 20 operations
- **98% fewer operations!**

### 2. Why Two Backup Types?

**File Backup** (.sql/.csv):
- ✅ Can restore ENTIRE table with one command
- ✅ Can archive to external storage
- ✅ 30-day retention
- ❌ Not SQL-queryable (must restore first)

**Database Backup** (table):
- ✅ SQL-queryable (easy to analyze)
- ✅ Linked to Run_ID
- ✅ Can restore specific records
- ❌ Takes database storage
- 7-day retention

### 3. Why Audit Table?
- 📝 Compliance: Know who changed what and when
- 🔍 Debugging: Track down data issues
- 📊 Analytics: See trends in dropdown changes
- 🔒 Security: Tamper-evident log

### 4. Why Mapping Table?
Each portal uses different names for same field:
- MaxHealth: "Quotation For"
- Sukoon: "Policy_Holder_Type"
- ADNIC: "PolicyType"

**Without mapping**: Database has 3 separate fields  
**With mapping**: Database has 1 field: "Quotation_For"

---

## 📊 Typical Run Statistics

```
Extraction Run: 20260223_141939
─────────────────────────────────
Portals: 3 (MaxHealth, Sukoon, Qatar)
Duration: 25 seconds

Table Operations:
├─ Staging: DELETE 500 old + INSERT 500 new
├─ Backup: INSERT 10,000 (full table)
├─ Comparison: 500 staging ↔ 10,000 original
├─ Original: 15 INSERT + 3 UPDATE + 2 DELETE
└─ Audit: INSERT 20 change records

Changes Detected:
├─ NEW: 15 values
├─ MODIFIED: 3 values (whitespace)
├─ DELETED: 2 values
├─ UNCHANGED: 480 values (96%)
└─ Total Changes: 20 (4% of data)

Efficiency: 98% fewer operations vs DELETE+INSERT approach
```

---

## 🔧 Common Queries

### Check Latest Staging Data
```sql
SELECT * FROM Medical_CTN_Cascading_Dropdown_Staging
ORDER BY Created_At DESC
LIMIT 100;
```

### Check Latest Changes
```sql
SELECT * FROM Medical_CTN_Cascading_Dropdown_Audit
ORDER BY Changed_At DESC
LIMIT 50;
```

### Count Records by Company
```sql
SELECT Company, COUNT(*) as count
FROM Medical_CTN_Cascading_Dropdown_Lifecare
GROUP BY Company;
```

### View Available Backups
```sql
SELECT Run_ID, COUNT(*) as records, Backup_Date
FROM Medical_CTN_Cascading_Dropdown_Backup
GROUP BY Run_ID, Backup_Date
ORDER BY Backup_Date DESC;
```

### Check Mapping for Portal
```sql
SELECT Dropdown_Name, MaxHealth
FROM Medical_CTN_Portal_Field_Mapping
WHERE MaxHealth IS NOT NULL;
```

---

**Quick Summary**:
- **5 Tables**: Original (prod), Staging (temp), Backup (safety), Audit (history), Mapping (reference)
- **Smart Comparison**: Only 4% of data changes per run
- **Dual Backup**: 7-day DB backup + 30-day file backup
- **Full Audit**: Every INSERT/UPDATE/DELETE logged permanently
- **Name Standardization**: Portal names → Standard names via mapping

For detailed flow explanation, see: [DATABASE_FLOW_README.md](DATABASE_FLOW_README.md)
