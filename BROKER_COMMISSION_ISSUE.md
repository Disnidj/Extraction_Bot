"""
ISSUE SUMMARY: BrokerCommission Not Being Uploaded
===================================================

PROBLEM:
- User manually deleted BrokerCommission records (CTN_IDs 670780-670782)
- System did NOT detect these deletions
- User expected deleted records to be re-inserted from extraction

ROOT CAUSE:
-----------
1. ✅ ADNIC API EXTRACTS "Broker Commission" data
   - Code: src/pages/adnic/process_page.py line 179
   - field_name = "Broker Commission"
   
2. ❌ "Broker Commission" has NO MAPPING in Medical_CTN_Portal_Field_Mapping table
   - ADNIC column: NULL (no mapping exists)
   - Should map to: "BrokerCommission"
   
3. 🚫 Configuration: ONLY_UPLOAD_MAPPED = True
   - Only uploads records that have mappings
   - Unmapped records are SKIPPED
   
4. ⚠️  Result: "Broker Commission" records never reach staging table
   - Not in staging = not in comparison
   - Deleted records NOT detected

DATABASE EVIDENCE:
------------------
- Database has: 237 BrokerCommission records (including deleted ones)
- Staging has: 0 BrokerCommission records (skipped during upload)
- Deletion detection only works for dropdowns IN staging

COMPARISON LOGIC:
-----------------
SQL for detecting deletions:
  SELECT * FROM Original_Table 
  WHERE Company = 'ADNIC'
  AND Dropdown_Name IN ('Business Nature', 'Dental', ...) ← Only extracted!
  
Since "BrokerCommission" is NOT extracted (due to missing mapping),
it's NOT in the comparison list, so deletions won't be detected.

SOLUTION:
---------
Add mapping to Medical_CTN_Portal_Field_Mapping table:

INSERT INTO Medical_CTN_Portal_Field_Mapping (Dropdown_Name, ADNIC)
VALUES ('BrokerCommission', 'Broker Commission');

After adding mapping:
1. Next extraction will include "Broker Commission" → "BrokerCommission"
2. Records will reach staging table
3. Comparison will detect missing values
4. System will INSERT any values present in API but missing in database

IMPORTANT NOTE:
---------------
The 3 records you manually deleted (670780-670782) will NOT be re-inserted
UNLESS those exact TPA/Network/Value combinations exist in the ADNIC API.

The system only inserts what the API returns. If those specific combinations
are not in the current API response, they won't be re-inserted.

To verify what will be inserted, check the extraction logs or the 
extract_dropdown_values() output for "Broker Commission" field.
"""
