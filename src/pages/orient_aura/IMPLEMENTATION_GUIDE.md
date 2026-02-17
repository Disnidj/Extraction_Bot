# Orient Aura - Complete Implementation Checklist

## ✅ Already Completed

### 1. **API Extraction Module** ✅
- [x] `orient_aura_main_api.py` - Main entry point
- [x] `api/auth.py` - Token extraction from browser
- [x] `api/client.py` - API HTTP client (industries, groups, emirates, TPAs, plans, benefits)
- [x] `api/extractor.py` - Orchestrates extraction flow
- [x] `api/formatter.py` - Converts JSON to database format
- [x] `api/mapping.py` - Configuration (hardcoded group_id=173, version_id=44)
- [x] `login_page.py` - Browser login with hardcoded credentials

### 2. **Integration with main.py** ✅
- [x] Imported `run_orient_aura_api_extraction` 
- [x] Added to `API_PORTAL_GROUPS` (option 19)
- [x] Selectable in API extraction mode

### 3. **Configuration Files** ✅
- [x] `config.yaml` - Added credentials (email, password)
- [x] `load_yaml.py` - Added ORIENT_AURA_EMAIL, ORIENT_AURA_PASSWORD constants
- [x] `company_selector_updated.py` - Added "Orient Aura" as ID 19

### 4. **Database Upload Logic** ✅
- [x] Company name mapping: "Orient Aura" → "ORIENT INSURANCE"
- [x] Upload function auto-handles Orient Aura (deletion + insertion)
- [x] Transaction support (rollback on error)

---

## 🔧 **Required: Database Changes**

### Step 1: Add ORIENT INSURANCE Column
**File**: `database/sql_scripts/add_orient_insurance_column.sql`

```sql
ALTER TABLE Medical_CTN_Portal_Field_Mapping
ADD COLUMN IF NOT EXISTS `ORIENT INSURANCE` VARCHAR(500) NULL
AFTER ADNIC;
```

**Action**: Run this SQL script in your database (WebDB)

---

### Step 2: Populate Dropdown Mappings
**File**: `database/sql_scripts/populate_orient_insurance_mappings.sql`

Maps Orient Aura's API field names to standard database dropdown names:

| Orient Aura API Field | Standard Dropdown_Name |
|----------------------|------------------------|
| Industry Categories | Industry Categories |
| Annual Limit | Plan Annual Limit |
| Territory | Territory |
| Room Category | Accomodation(room) |
| Deductable | Deductable |
| Limit of Phamacy | Phamiacy |
| Pharmacy | oPharmacy |
| Diagnostic Copay | RadiologyandDiagnostic |
| Dental | Dental |
| Optical | Optical |
| Broker Commission | BrokerCommission |

**Action**: Run this SQL script after Step 1

---

## ⚠️ **Important Notes**

### Dropdown Name Mapping
Orient Aura uses **raw benefit names** from the API as `Dropdown_Name` values. These must be mapped to standard database names in the `Medical_CTN_Portal_Field_Mapping` table.

**How it works:**
1. API returns benefits with `benefits_name` field (e.g., "Room Category")
2. Formatter uses this as `Dropdown_Name` in output
3. Upload function looks up mapping: `Room Category (Orient)` → `Accomodation(room) (Standard)`
4. Records are inserted with STANDARD names into `Medical_CTN_Cascading_Dropdown_Lifecare`

### If Dropdown Names Don't Match
If you see warnings like this during upload:
```
⚠️ Unmapped dropdown names: Room Category, Limit of Phamacy
```

**Solutions:**
1. **Preferred**: Add mappings to database (Step 2 above)
2. **Alternative**: Modify formatter to use standard names directly (hardcode in code)
3. **Temporary**: Records will be inserted with original names (may break frontend dropdowns)

---

## 🧪 **Testing the Complete Flow**

### Test Extraction
```bash
python main.py
# Select option: Extract using APIs
# Select company: Orient Aura (19)
```

**Expected Output:**
1. ✅ Login successful, token obtained
2. ✅ Industry Categories: X options
3. ✅ Processing Group: Nextcare Sme (ID: 173)
4. ✅ Emirates → TPAs → Plans → Benefits extracted
5. ✅ JSON file saved to `extracted_data/{timestamp}/orient_aura/`
6. ✅ Text file saved (with TPA/Network expansion)
7. ✅ Database upload: X rows deleted, Y rows inserted
8. ✅ PDF report generated

### Verify Database
```sql
-- Check if Orient Insurance data is present
SELECT COUNT(*) AS Total_Records
FROM Medical_CTN_Cascading_Dropdown_Lifecare
WHERE Company = 'ORIENT INSURANCE';

-- Check unique dropdown names
SELECT DISTINCT Dropdown_Name, COUNT(*) AS Count
FROM Medical_CTN_Cascading_Dropdown_Lifecare
WHERE Company = 'ORIENT INSURANCE'
GROUP BY Dropdown_Name
ORDER BY Dropdown_Name;

-- Check TPA/Network breakdown
SELECT TPA, Network, COUNT(*) AS Records
FROM Medical_CTN_Cascading_Dropdown_Lifecare
WHERE Company = 'ORIENT INSURANCE'
GROUP BY TPA, Network
ORDER BY TPA, Network;
```

---

## 🎯 **Comparison with Other API Portals**

| Feature | Takaful | Qatar | ADNIC | Sukoon | MaxHealth | Orient Aura |
|---------|---------|-------|-------|--------|-----------|-------------|
| **API Extraction** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Hardcoded Credentials** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Hardcoded Group** | ✅ (31) | ✅ (272) | ✅ | ✅ | ✅ | ✅ (173) |
| **Database Upload** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Company Name Mapping** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Dropdown Field Mapping** | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ **Need to add** |
| **PDF Report** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RPA Flow (non-API)** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ (API only) |

---

## 📝 **Quick Start (After Database Setup)**

1. **Run the SQL scripts** (Steps 1 & 2 above)
2. **Test extraction**:
   ```bash
   python main.py
   # Choose API extraction → Orient Aura
   ```
3. **Verify output files** in `extracted_data/{timestamp}/orient_aura/`
4. **Check database** for "ORIENT INSURANCE" records
5. **Review PDF report** in `reports/`

---

## 🆘 **Troubleshooting**

### Issue: "Column 'ORIENT INSURANCE' doesn't exist"
**Solution**: Run Step 1 SQL script to add the column

### Issue: "Unmapped dropdown names" warning
**Solution**: Run Step 2 SQL script to populate mappings

### Issue: "No records inserted"
**Solution**: Check if:
- API extraction returned data (check JSON file)
- Text file has records (check .txt file)
- Company name is correct ("Orient Aura" in formatter)

### Issue: Records inserted but frontend dropdowns empty
**Solution**: Dropdown names don't match - run Step 2 mapping script

---

## ✅ **Final Checklist**

- [ ] Database: Add "ORIENT INSURANCE" column (Step 1)
- [ ] Database: Populate dropdown mappings (Step 2)
- [ ] Test: Run full extraction flow
- [ ] Verify: Check database records
- [ ] Verify: Confirm dropdown names are mapped correctly
- [ ] Test: Check frontend portal dropdowns work

Once these are complete, Orient Aura is **fully implemented** like Qatar, Takaful, ADNIC, Sukoon, and MaxHealth! 🎉
