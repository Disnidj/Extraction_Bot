# 🔍 ALL COMPARISON QUERIES - Complete Reference

> **Every SQL query used to compare Staging vs Original tables with detailed explanations**

---

## 📚 TABLE OF CONTENTS

1. [Main Comparison Queries](#main-comparison-queries)
2. [Comparison Logic Breakdown](#comparison-logic-breakdown)
3. [Supporting Queries](#supporting-queries)
4. [Manual Comparison Scripts](#manual-comparison-scripts)
5. [Query Examples with Real Data](#query-examples-with-real-data)

---

# 1️⃣ MAIN COMPARISON QUERIES

## 🔵 Query 1: Fetch All Staging Records (by Company)

**Location:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L697-L704)

```sql
-- Get all staging records for a specific company and dropdown names
SELECT Broker_ID, Company, TPA, Network, Region, 
       Dropdown_Name, Selection_Value
FROM Medical_CTN_Cascading_Dropdown_Staging
WHERE Company = %s 
  AND Run_ID = %s 
  AND Dropdown_Name IN (%s, %s, %s, ...)  -- Dynamic list of dropdown names
```

### Parameters:
- `Company`: e.g., `'SUKOON INSURANCE'`
- `Run_ID`: e.g., `'20260226_153045'`
- `Dropdown_Names`: e.g., `('Quotation_For', 'Coverage_Amount', 'Policy_Type', ...)`

### Purpose:
Get **ALL dropdown values** from staging table for comparison.

### Example Execution:
```python
placeholders = ", ".join(["%s"] * len(dropdown_names))
staging_query = f"""
    SELECT Broker_ID, Company, TPA, Network, Region, 
           Dropdown_Name, Selection_Value
    FROM {STAGING_TABLE}
    WHERE Company = %s AND Run_ID = %s AND Dropdown_Name IN ({placeholders})
"""
params = tuple([company, self.run_id] + list(dropdown_names))
staging_rows = self._fetch_all(staging_query, params)
```

### Sample Result:
```
[
  {
    'Broker_ID': 3,
    'Company': 'SUKOON INSURANCE',
    'TPA': 'NextCare',
    'Network': 'Enhanced',
    'Region': 'Dubai',
    'Dropdown_Name': 'Quotation_For',
    'Selection_Value': 'Individual'
  },
  {
    'Broker_ID': 3,
    'Company': 'SUKOON INSURANCE',
    'TPA': 'NextCare',
    'Network': 'Enhanced',
    'Region': 'Dubai',
    'Dropdown_Name': 'Quotation_For',
    'Selection_Value': 'Family Floater'
  },
  ...
]
```

---

## 🔵 Query 2: Fetch All Original Records (by Company)

**Location:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L707-L714)

```sql
-- Get all original records for a specific company and dropdown names
SELECT Broker_ID, Company, TPA, Network, Region, 
       Dropdown_Name, Selection_Value
FROM Medical_CTN_Cascading_Dropdown_Lifecare
WHERE Company = %s 
  AND Dropdown_Name IN (%s, %s, %s, ...)  -- Dynamic list
```

### Parameters:
- `Company`: e.g., `'SUKOON INSURANCE'`
- `Dropdown_Names`: e.g., `('Quotation_For', 'Coverage_Amount', 'Policy_Type', ...)`

### Key Difference from Query 1:
- ❌ **NO Run_ID filter** (original table doesn't have Run_ID)
- ✅ Gets **current production data** for comparison

### Example Execution:
```python
original_query = f"""
    SELECT Broker_ID, Company, TPA, Network, Region, 
           Dropdown_Name, Selection_Value
    FROM {ORIGINAL_TABLE}
    WHERE Company = %s AND Dropdown_Name IN ({placeholders})
"""
params = tuple([company] + list(dropdown_names))
original_rows = self._fetch_all(original_query, params)
```

### Sample Result:
```
[
  {
    'Broker_ID': 3,
    'Company': 'SUKOON INSURANCE',
    'TPA': 'NextCare',
    'Network': 'Enhanced',
    'Region': 'Dubai',
    'Dropdown_Name': 'Quotation_For',
    'Selection_Value': 'Individual'
  },
  {
    'Broker_ID': 3,
    'Company': 'SUKOON INSURANCE',
    'TPA': 'NextCare',
    'Network': 'Enhanced',
    'Region': 'Dubai',
    'Dropdown_Name': 'Deductible',
    'Selection_Value': '5 %'    # Note the space!
  },
  ...
]
```

---

# 2️⃣ COMPARISON LOGIC BREAKDOWN

## 🧩 Step 1: Build Comparison Keys

**Location:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L717-L759)

After fetching data from both tables, the system builds **two types of keys**:

### A) Full Key (Exact Match)
```python
full_key = (Company, TPA, Network, Region, Dropdown_Name, Selection_Value)
```

**Example:**
```python
('SUKOON INSURANCE', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For', 'Individual')
```

**Purpose:** Check if **EXACT** record exists (including value)

### B) Base Key (Group Identifier)
```python
base_key = (Company, TPA, Network, Region, Dropdown_Name)
```

**Example:**
```python
('SUKOON INSURANCE', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For')
```

**Purpose:** Group all values under the same dropdown context

---

## 🧩 Step 2: Build Lookup Dictionaries

### Staging Lookup Structure:
```python
staging_full_keys = {
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For', 'Individual'),
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For', 'Family Floater'),
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Deductible', '5%'),  # No space
}

staging_by_base_key = {
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For'): [
        {'broker_id': 3, 'value': 'Individual'},
        {'broker_id': 3, 'value': 'Family Floater'}
    ],
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Deductible'): [
        {'broker_id': 3, 'value': '5%'}
    ]
}
```

### Original Lookup Structure:
```python
original_full_keys = {
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For', 'Individual'),
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Deductible', '5 %'),  # Has space!
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Policy_Type', 'Old Policy'),
}

original_by_base_key = {
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For'): [
        {'broker_id': 3, 'value': 'Individual'}
    ],
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Deductible'): [
        {'broker_id': 3, 'value': '5 %'}  # Has space!
    ],
    ('SUKOON', 'NextCare', 'Enhanced', 'Dubai', 'Policy_Type'): [
        {'broker_id': 3, 'value': 'Old Policy'}
    ]
}
```

---

## 🧩 Step 3: Detect NEW Records

**Location:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L763-L828)

### Logic:
```python
# For each base_key in staging
for base_key, staging_values in staging_by_base_key.items():
    original_values = original_by_base_key.get(base_key, [])
    original_value_set = {v['value'] for v in original_values}
    
    for staging_item in staging_values:
        staging_value = staging_item['value']
        
        # Check 1: Exact match exists?
        if staging_value in original_value_set:
            continue  # UNCHANGED - skip
        
        # Check 2: Similar value exists? (whitespace/case difference)
        found_similar = False
        for orig_item in original_values:
            orig_value = orig_item['value']
            _, _, diff_type = highlight_difference(orig_value, staging_value)
            
            if diff_type in ["WHITESPACE_CHANGE", "INTERNAL_WHITESPACE", "CASE_CHANGE"]:
                # MODIFIED (whitespace/case only)
                report.modified_records.append(...)
                found_similar = True
                break
        
        # Check 3: Completely new value
        if not found_similar:
            # NEW VALUE
            report.new_records.append(...)
```

### Example Detection:

**Scenario 1: NEW Value**
```
Staging:  'Family Floater'
Original: ['Individual'] only

Result: NEW record (INSERT needed)
```

**Scenario 2: MODIFIED Value (Whitespace)**
```
Staging:  '5%'
Original: '5 %'

Result: MODIFIED record (UPDATE needed)
Difference Type: WHITESPACE_CHANGE
```

**Scenario 3: UNCHANGED Value**
```
Staging:  'Individual'
Original: 'Individual'

Result: UNCHANGED (skip)
```

---

## 🧩 Step 4: Detect DELETED Records

**Location:** [staging_upload.py](src/services/db_service/api_data/staging_upload.py#L830-L880)

### Logic with Safety Check:
```python
# For each base_key in original
for base_key, original_values in original_by_base_key.items():
    
    # SAFETY CHECK: Only delete if this GROUP exists in staging
    if base_key not in staging_by_base_key:
        skipped_groups += 1
        skipped_values += len(original_values)
        continue  # DON'T DELETE - API might have failed!
    
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
        
        # DELETED record
        report.deleted_records.append(...)
```

### Example Detection:

**Scenario 1: DELETED Value**
```
Staging:  ['Individual', 'Family Floater']
Original: ['Individual', 'Family Floater', 'Old Policy']

Result: 'Old Policy' is DELETED (DELETE needed)
```

**Scenario 2: Protected Group (API Error Safety)**
```
Staging:  No records for this base_key (API error!)
Original: ['Value1', 'Value2', 'Value3']

Result: ALL VALUES PROTECTED (no deletion)
Reason: Entire group missing from staging = possible API failure
```

---

## 🧩 Step 5: Whitespace/Case Difference Detection

**Location:** [staging_comparison_utils.py](src/services/db_service/api_data/staging_comparison_utils.py#L11-L68)

### Function: `highlight_difference(old_value, new_value)`

```python
def highlight_difference(old_value: str, new_value: str) -> Tuple[str, str, str]:
    """
    Returns: (old_highlighted, new_highlighted, difference_type)
    
    Difference Types:
    - "NO_CHANGE": Identical
    - "WHITESPACE_CHANGE": Leading/trailing whitespace differs
    - "INTERNAL_WHITESPACE": Internal whitespace differs (e.g., "3 %" vs "3%")
    - "CASE_CHANGE": Only letter case differs
    - "VALUE_CHANGE": Actual content differs
    """
    
    if old_value == new_value:
        return old_value, new_value, "NO_CHANGE"
    
    # Check leading/trailing whitespace
    if old_value.strip() == new_value.strip():
        return f'"{old_value}"', f'"{new_value}"', "WHITESPACE_CHANGE"
    
    # Check internal whitespace
    old_normalized = re.sub(r'\s+', ' ', old_value.strip())
    new_normalized = re.sub(r'\s+', ' ', new_value.strip())
    if old_normalized == new_normalized:
        return f'"{old_value}"', f'"{new_value}"', "INTERNAL_WHITESPACE"
    
    # Check case only
    if old_value.lower() == new_value.lower():
        return f'"{old_value}"', f'"{new_value}"', "CASE_CHANGE"
    
    # General value change
    return f'"{old_value}"', f'"{new_value}"', "VALUE_CHANGE"
```

### Example Detections:

```python
# Whitespace - Leading/Trailing
highlight_difference("test ", "test")
# Result: ('"test "', '"test"', "WHITESPACE_CHANGE")

# Whitespace - Internal
highlight_difference("5 %", "5%")
# Result: ('"5 %"', '"5%"', "INTERNAL_WHITESPACE")

# Case Change
highlight_difference("INDIVIDUAL", "individual")
# Result: ('"INDIVIDUAL"', '"individual"', "CASE_CHANGE")

# Value Change
highlight_difference("Individual", "Family Floater")
# Result: ('"Individual"', '"Family Floater"', "VALUE_CHANGE")
```

---

# 3️⃣ SUPPORTING QUERIES

## 🟢 Query 3: Get Latest Run ID (Manual Scripts)

```sql
-- Get the most recent extraction run ID
SELECT DISTINCT Run_ID 
FROM Medical_CTN_Cascading_Dropdown_Staging 
ORDER BY Run_ID DESC 
LIMIT 1
```

**Used in:** [compare_staging_original.py](compare_staging_original.py#L17-L18)

---

## 🟢 Query 4: Get Dropdown Names in Staging

```sql
-- Get all unique dropdown names for a company in staging
SELECT DISTINCT Dropdown_Name 
FROM Medical_CTN_Cascading_Dropdown_Staging 
WHERE Company = %s 
  AND Run_ID = %s
```

**Used in:** [compare_staging_original.py](compare_staging_original.py#L26-L27)

---

## 🟢 Query 5: Get Dropdown Names in Original

```sql
-- Get all unique dropdown names for a company in original
SELECT DISTINCT Dropdown_Name 
FROM Medical_CTN_Cascading_Dropdown_Lifecare 
WHERE Company = %s
```

**Used in:** [compare_staging_original.py](compare_staging_original.py#L36-L37)

---

## 🟢 Query 6: Count Values per Dropdown (Staging)

```sql
-- Count how many values each dropdown has in staging
SELECT COUNT(*) as cnt 
FROM Medical_CTN_Cascading_Dropdown_Staging 
WHERE Company = %s 
  AND Run_ID = %s 
  AND Dropdown_Name = %s
```

---

## 🟢 Query 7: Count Values per Dropdown (Original)

```sql
-- Count how many values each dropdown has in original
SELECT COUNT(*) as cnt 
FROM Medical_CTN_Cascading_Dropdown_Lifecare 
WHERE Company = %s 
  AND Dropdown_Name = %s
```

---

# 4️⃣ MANUAL COMPARISON SCRIPTS

## 📄 Script: compare_staging_original.py

**Purpose:** Manual comparison of staging vs original for debugging

### Full Query Flow:

```python
# Step 1: Get latest run
cursor.execute(f"""
    SELECT DISTINCT Run_ID 
    FROM {STAGING_TABLE} 
    ORDER BY Run_ID DESC 
    LIMIT 1
""")
run_id = cursor.fetchone()['Run_ID']

# Step 2: Get staging dropdown names
cursor.execute(f"""
    SELECT DISTINCT Dropdown_Name 
    FROM {STAGING_TABLE} 
    WHERE Company = %s 
      AND Run_ID = %s
""", ('Orient Aura', run_id))
staging_dropdowns = [r['Dropdown_Name'] for r in cursor.fetchall()]

# Step 3: Count staging values
for dropdown in staging_dropdowns:
    cursor.execute(f"""
        SELECT COUNT(*) as cnt 
        FROM {STAGING_TABLE} 
        WHERE Company = %s 
          AND Run_ID = %s 
          AND Dropdown_Name = %s
    """, ('Orient Aura', run_id, dropdown))
    count = cursor.fetchone()['cnt']
    print(f"  - {dropdown}: {count} values")

# Step 4: Get original dropdown names
cursor.execute(f"""
    SELECT DISTINCT Dropdown_Name 
    FROM {ORIGINAL_TABLE} 
    WHERE Company = %s
""", ('Orient Aura',))
original_dropdowns = [r['Dropdown_Name'] for r in cursor.fetchall()]

# Step 5: Count original values
for dropdown in original_dropdowns:
    cursor.execute(f"""
        SELECT COUNT(*) as cnt 
        FROM {ORIGINAL_TABLE} 
        WHERE Company = %s 
          AND Dropdown_Name = %s
    """, ('Orient Aura', dropdown))
    count = cursor.fetchone()['cnt']
    print(f"  - {dropdown}: {count} values")

# Step 6: Compare dropdown types
common = set(staging_dropdowns) & set(original_dropdowns)
only_staging = set(staging_dropdowns) - set(original_dropdowns)
only_original = set(original_dropdowns) - set(staging_dropdowns)
```

---

# 5️⃣ QUERY EXAMPLES WITH REAL DATA

## 🎯 Example 1: Complete Comparison for SUKOON INSURANCE

### Step 1: Fetch Staging Data
```sql
SELECT Broker_ID, Company, TPA, Network, Region, 
       Dropdown_Name, Selection_Value
FROM Medical_CTN_Cascading_Dropdown_Staging
WHERE Company = 'SUKOON INSURANCE'
  AND Run_ID = '20260226_153045'
  AND Dropdown_Name IN ('Quotation_For', 'Coverage_Amount', 'Deductible')
```

**Result (3 records):**
```
Broker_ID | Company           | TPA      | Network  | Region | Dropdown_Name    | Selection_Value
----------|-------------------|----------|----------|--------|------------------|----------------
3         | SUKOON INSURANCE  | NextCare | Enhanced | Dubai  | Quotation_For    | Individual
3         | SUKOON INSURANCE  | NextCare | Enhanced | Dubai  | Quotation_For    | Family Floater
3         | SUKOON INSURANCE  | NextCare | Enhanced | Dubai  | Deductible       | 5%
```

### Step 2: Fetch Original Data
```sql
SELECT Broker_ID, Company, TPA, Network, Region, 
       Dropdown_Name, Selection_Value
FROM Medical_CTN_Cascading_Dropdown_Lifecare
WHERE Company = 'SUKOON INSURANCE'
  AND Dropdown_Name IN ('Quotation_For', 'Coverage_Amount', 'Deductible')
```

**Result (3 records):**
```
Broker_ID | Company           | TPA      | Network  | Region | Dropdown_Name    | Selection_Value
----------|-------------------|----------|----------|--------|------------------|----------------
3         | SUKOON INSURANCE  | NextCare | Enhanced | Dubai  | Quotation_For    | Individual
3         | SUKOON INSURANCE  | NextCare | Enhanced | Dubai  | Deductible       | 5 %
3         | SUKOON INSURANCE  | NextCare | Enhanced | Dubai  | Policy_Type      | Old Policy
```

### Step 3: Comparison Result

**Comparison Keys Built:**

**Staging Full Keys:**
```python
{
    ('SUKOON INSURANCE', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For', 'Individual'),
    ('SUKOON INSURANCE', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For', 'Family Floater'),
    ('SUKOON INSURANCE', 'NextCare', 'Enhanced', 'Dubai', 'Deductible', '5%')
}
```

**Original Full Keys:**
```python
{
    ('SUKOON INSURANCE', 'NextCare', 'Enhanced', 'Dubai', 'Quotation_For', 'Individual'),
    ('SUKOON INSURANCE', 'NextCare', 'Enhanced', 'Dubai', 'Deductible', '5 %'),
    ('SUKOON INSURANCE', 'NextCare', 'Enhanced', 'Dubai', 'Policy_Type', 'Old Policy')
}
```

**Changes Detected:**
1. ✅ **UNCHANGED**: `Quotation_For = Individual` (exact match in both)
2. 🆕 **NEW**: `Quotation_For = Family Floater` (only in staging)
3. 🔄 **MODIFIED**: `Deductible = '5%'` vs `'5 %'` (WHITESPACE_CHANGE)
4. 🗑️ **DELETED**: `Policy_Type = Old Policy` (only in original)

---

## 🎯 Example 2: API Error Protection

### Scenario: Portal API Failed (No Data Extracted)

**Staging Data:**
```sql
SELECT * FROM Medical_CTN_Cascading_Dropdown_Staging
WHERE Company = 'DAMAN HEALTH'
  AND Run_ID = '20260226_153045'
```
**Result:** 0 records (API failed!)

**Original Data:**
```sql
SELECT * FROM Medical_CTN_Cascading_Dropdown_Lifecare
WHERE Company = 'DAMAN HEALTH'
```
**Result:** 2,456 records (production data)

**Comparison Logic:**
```python
# base_key for DAMAN HEALTH groups
for base_key, original_values in original_by_base_key.items():
    # SAFETY CHECK
    if base_key not in staging_by_base_key:  # True - no staging data!
        skipped_groups += 1
        skipped_values += len(original_values)
        continue  # ✅ PROTECTED - Don't delete!
```

**Result:**
- ❌ **NO DELETIONS** (all 2,456 records protected)
- 🛡️ **Safety message**: `Protected 2,456 values in 45 groups (not in staging - possible API issue)`

---

# 📊 COMPARISON QUERY SUMMARY

| Query | Purpose | Tables | Key Filters |
|-------|---------|--------|-------------|
| **Staging Fetch** | Get new extraction data | Staging | `Company`, `Run_ID`, `Dropdown_Name IN (...)` |
| **Original Fetch** | Get current production data | Original | `Company`, `Dropdown_Name IN (...)` |
| **Latest Run** | Get most recent extraction | Staging | `ORDER BY Run_ID DESC LIMIT 1` |
| **Dropdown Count** | Count values per dropdown | Both | `Company`, `Dropdown_Name` |
| **Distinct Dropdowns** | List all dropdown types | Both | `Company` |

---

# 🔧 COMPARISON ALGORITHM FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: FETCH STAGING DATA                                      │
├─────────────────────────────────────────────────────────────────┤
│ SELECT ... FROM Staging                                         │
│ WHERE Company = ? AND Run_ID = ? AND Dropdown_Name IN (...)    │
│                                                                  │
│ Result: staging_rows[] (8,523 records)                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: FETCH ORIGINAL DATA                                     │
├─────────────────────────────────────────────────────────────────┤
│ SELECT ... FROM Original                                        │
│ WHERE Company = ? AND Dropdown_Name IN (...)                   │
│                                                                  │
│ Result: original_rows[] (8,398 records)                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: BUILD COMPARISON KEYS (In-Memory)                       │
├─────────────────────────────────────────────────────────────────┤
│ For each staging row:                                           │
│   full_key = (Company, TPA, Network, Region, Dropdown, Value)  │
│   base_key = (Company, TPA, Network, Region, Dropdown)         │
│                                                                  │
│ For each original row:                                          │
│   full_key = (Company, TPA, Network, Region, Dropdown, Value)  │
│   base_key = (Company, TPA, Network, Region, Dropdown)         │
│                                                                  │
│ Result: Dictionaries for fast lookup                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: COMPARE & DETECT CHANGES (In-Memory)                    │
├─────────────────────────────────────────────────────────────────┤
│ For each staging value:                                         │
│   ✓ Exact match in original? → UNCHANGED                       │
│   ✓ Similar (whitespace/case)? → MODIFIED                      │
│   ✓ Completely new? → NEW                                      │
│                                                                  │
│ For each original value:                                        │
│   ✓ Group missing from staging? → PROTECTED (no delete)        │
│   ✓ Value missing from staging? → DELETED                      │
│                                                                  │
│ Result: ChangeReport with all changes categorized              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FINAL RESULT                                                     │
├─────────────────────────────────────────────────────────────────┤
│ • 45 NEW records                                                │
│ • 12 MODIFIED records (whitespace/case)                         │
│ • 68 DELETED records                                            │
│ • 8,398 UNCHANGED records                                       │
│ • 234 PROTECTED values (15 groups missing from staging)         │
└─────────────────────────────────────────────────────────────────┘
```

---

# ✅ KEY POINTS

1. **Only 2 Main Queries** - Fetch staging and original data
2. **All Comparison In-Memory** - No complex SQL joins
3. **Exact Match First** - Check full key for unchanged records
4. **Whitespace Detection** - Uses Python `highlight_difference()` function
5. **Safety First** - Protects groups missing from staging (API error handling)
6. **Efficient** - Builds dictionaries for O(1) lookup instead of nested loops

---

# 📖 CODE REFERENCES

| Operation | File | Line |
|-----------|------|------|
| Staging Query | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 697-704 |
| Original Query | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 707-714 |
| Key Building | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 717-759 |
| NEW Detection | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 763-828 |
| DELETE Detection | [staging_upload.py](src/services/db_service/api_data/staging_upload.py) | 830-880 |
| Whitespace Detection | [staging_comparison_utils.py](src/services/db_service/api_data/staging_comparison_utils.py) | 11-68 |
| Manual Comparison | [compare_staging_original.py](compare_staging_original.py) | Full file |

---

**End of Reference** ✅
