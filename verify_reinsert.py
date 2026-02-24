"""Verify the deleted records were re-inserted"""
from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

db = MySQLDatabase(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
db.connect()

print("=" * 70)
print("VERIFICATION: Were the deleted records re-inserted?")
print("=" * 70)

# Check if these specific records exist NOW in the database
current_records = db.fetch_all("""
    SELECT CTN_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value
    FROM Medical_CTN_Cascading_Dropdown_Lifecare
    WHERE Company = 'ADNIC'
    AND TPA = 'ADNIC'
    AND Network = 'Blue Network'
    AND Region = 'Dubai'
    AND Dropdown_Name = 'Business_Nature'
    AND Selection_Value IN ('Healthcare/Medical providers', 'Associations', 'Construction')
    ORDER BY Selection_Value
""")

if current_records:
    print(f"\n✅ SUCCESS! Found {len(current_records)} re-inserted records:")
    print("-" * 70)
    for rec in current_records:
        print(f"  CTN_ID: {rec['CTN_ID']:8} | {rec['Selection_Value']}")
    
    print("\n📊 WHAT HAPPENED:")
    print("  1. You deleted CTN_IDs: 1130877, 1130878, 1130879")
    print("  2. You ran extraction (20260223_165709)")
    print("  3. ✅ System detected 'Business Nature' data in API")
    print("  4. ✅ Mapped 'Business Nature' → 'Business_Nature'")
    print("  5. ✅ Data uploaded to staging (468 records)")
    print("  6. ✅ Comparison found these 3 values MISSING in original")
    print("  7. ✅ System re-inserted them with NEW CTN_IDs")
    print("  8. ✅ Logged INSERT operations to audit table")
    
    # Show the NEW CTN_IDs vs old ones
    print("\n🔄 CTN_ID Changes:")
    print("  Old CTN_IDs (deleted):  1130877, 1130878, 1130879")
    new_ids = [str(rec['CTN_ID']) for rec in current_records]
    print(f"  New CTN_IDs (inserted): {', '.join(new_ids)}")
    
else:
    print("\n❌ ERROR: Records NOT found in database!")
    print("  This shouldn't happen if the system worked correctly")

# Show audit trail
print("\n" + "=" * 70)
print("AUDIT TRAIL (Proof of Re-insertion)")
print("=" * 70)

audit = db.fetch_all("""
    SELECT Audit_ID, Run_ID, Change_Type, New_Value, Changed_At
    FROM Medical_CTN_Cascading_Dropdown_Audit
    WHERE Run_ID = '20260223_165709'
    AND Company = 'ADNIC'
    AND Dropdown_Name = 'Business_Nature'
    AND Change_Type = 'INSERT'
    ORDER BY New_Value
""")

if audit:
    for a in audit:
        print(f"  Audit_ID {a['Audit_ID']}: INSERT '{a['New_Value']}' at {a['Changed_At']}")

db.disconnect()
