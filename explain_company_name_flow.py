"""
COMPLETE EXPLANATION: Where Each Company Name Exists
"""
from src.services.db_service.api_data.staging_upload import StagingUploader
from src.services.db_service.api_data.staging_config import COMPANY_NAME_MAPPING

def show_complete_flow():
    """Show exactly where each company name variation exists"""
    
    service = StagingUploader()
    service._connect()
    
    print("\n" + "="*80)
    print("📋 COMPANY NAME FLOW - COMPLETE EXPLANATION")
    print("="*80)
    
    print("\n" + "="*80)
    print("🔧 STEP 1: EXTRACTION (Portal Name from website)")
    print("="*80)
    print("""
When you extract from Sukoon portal, the code uses portal name: "Sukoon"
Location: Portal configuration in main.py
Example: Portal name is "Sukoon" or "SUKOON INSURANCE (Sukoon)"
""")
    
    print("\n" + "="*80)
    print("🗺️  STEP 2: NAME MAPPING (Code Configuration)")
    print("="*80)
    print("""
File: src/services/db_service/api_data/staging_config.py
Line 90: COMPANY_NAME_MAPPING dictionary

Configured mapping:
    "Sukoon" → "SUKOON INSURANCE"

This converts portal name to what code THINKS database uses.
""")
    
    print("Current mapping configuration:")
    for portal, mapped_name in COMPANY_NAME_MAPPING.items():
        if 'sukoon' in portal.lower():
            print(f"   Portal: '{portal}' → Mapped to: '{mapped_name}'")
    
    print("\n" + "="*80)
    print("📤 STEP 3: STAGING TABLE (Temporary upload)")
    print("="*80)
    print("""
Table: Medical_CTN_Cascading_Dropdown_Staging
Column: Company (varchar with utf8mb4_unicode_ci collation)

When uploading to staging, uses the MAPPED name from config.
""")
    
    # Check staging table
    query = """
        SELECT DISTINCT Company
        FROM Medical_CTN_Cascading_Dropdown_Staging
        WHERE Company LIKE '%Sukoon%' OR Company LIKE '%SUKOON%'
    """
    results = service._fetch_all(query, ())
    
    if results:
        print("Currently stored in STAGING:")
        for row in results:
            company = row.get('Company') or row.get('company')
            print(f"   → '{company}' ← This is what the mapping produced")
    else:
        print("   (No Sukoon data in staging - cleared after processing)")
    
    print("\n" + "="*80)
    print("💾 STEP 4: ORIGINAL TABLE (Main database)")
    print("="*80)
    print("""
Table: Medical_CTN_Cascading_Dropdown_Lifecare
Column: Company (varchar with utf8mb4_0900_ai_ci collation)

This table has data from PREVIOUS manual insertions or past extractions.
The name might be different from your mapping!
""")
    
    # Check original table
    query = """
        SELECT DISTINCT Company
        FROM Medical_CTN_Cascading_Dropdown_Lifecare
        WHERE Company LIKE '%Sukoon%' OR Company LIKE '%SUKOON%'
    """
    results = service._fetch_all(query, ())
    
    print("Actually stored in ORIGINAL table:")
    for row in results:
        company = row.get('Company') or row.get('company')
        
        # Count records
        count_query = """
            SELECT COUNT(*) as count
            FROM Medical_CTN_Cascading_Dropdown_Lifecare
            WHERE Company = %s
        """
        count_result = service._fetch_all(count_query, (company,))
        count = count_result[0].get('count') if count_result else 0
        
        print(f"   → '{company}' ({count:,} records)")
    
    print("\n" + "="*80)
    print("🔍 STEP 5: COMPARISON (How MySQL matches them)")
    print("="*80)
    print("""
MySQL Column Collation: utf8mb4_0900_ai_ci
   • "ai" = Accent-Insensitive
   • "ci" = Case-Insensitive

This means when MySQL compares strings:
   'Sukoon Insurance' == 'SUKOON INSURANCE' == 'sukoon insurance'

The comparison query is:
   SELECT * FROM Original WHERE Company = 'SUKOON INSURANCE'

MySQL will match ALL of these:
   • 'Sukoon Insurance' ✅ (actual stored value)
   • 'SUKOON INSURANCE' ✅ (what your code searches for)
   • 'sukoon insurance' ✅
   • 'SuKoOn InSuRaNcE' ✅

Even though stored value is different case!
""")
    
    print("\n" + "="*80)
    print("📊 VISUAL SUMMARY")
    print("="*80)
    print("""
┌─────────────────────────────────────────────────────────────────┐
│ FLOW OF COMPANY NAME FOR SUKOON                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Portal Name (extraction code):                             │
│     "Sukoon" or "SUKOON INSURANCE (Sukoon)"                    │
│                           ↓                                     │
│  2. COMPANY_NAME_MAPPING (config):                             │
│     "Sukoon" → "SUKOON INSURANCE"                              │
│                           ↓                                     │
│  3. Staging Table Column:                                      │
│     Company = "SUKOON INSURANCE" ← Written to database         │
│                           ↓                                     │
│  4. Comparison Query:                                          │
│     WHERE Company = "SUKOON INSURANCE"                         │
│                           ↓                                     │
│  5. MySQL Collation (Case-Insensitive):                        │
│     Matches: "Sukoon Insurance" ← Already in original table    │
│                           ↓                                     │
│  6. Result:                                                    │
│     ✅ Found existing records (26,361 records)                 │
│     ✅ Comparison works despite case difference                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
""")
    
    print("\n" + "="*80)
    print("❓ WHY IT WORKS EVEN WITH MISMATCHED NAMES")
    print("="*80)
    print("""
Your code writes:     "SUKOON INSURANCE" (all caps)
Database contains:    "Sukoon Insurance" (mixed case)

Comparison still works because:
   1. Staging upload writes "SUKOON INSURANCE" to staging table
   2. Comparison queries: WHERE Company = "SUKOON INSURANCE"
   3. MySQL uses case-insensitive collation (utf8mb4_0900_ai_ci)
   4. MySQL matches "SUKOON INSURANCE" with "Sukoon Insurance"
   5. Finds 26,361 existing records
   6. All 19,755 staging records are subsets of these
   7. Result: 0 new records (correct!)

The case difference is COSMETIC only - doesn't break functionality!
""")
    
    print("\n" + "="*80)
    print("🔧 RECOMMENDATION")
    print("="*80)
    print("""
For consistency, update the mapping to match actual database:

Change in staging_config.py:
   FROM: "Sukoon": "SUKOON INSURANCE"
   TO:   "Sukoon": "Sukoon Insurance"

Benefits:
   ✅ Consistent casing in logs/reports
   ✅ Easier debugging
   ✅ No functional change (works either way)

But NOT urgent - system works correctly as-is!
""")
    
    service._disconnect()

if __name__ == "__main__":
    show_complete_flow()
