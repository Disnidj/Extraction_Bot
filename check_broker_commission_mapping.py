"""Check BrokerCommission mapping"""
from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

db = MySQLDatabase(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
db.connect()

# Check mapping for Broker Commission / BrokerCommission
result = db.fetch_all("""
    SELECT Dropdown_Name, ADNIC
    FROM Medical_CTN_Portal_Field_Mapping 
    WHERE ADNIC LIKE '%Broker%' OR ADNIC LIKE '%Commission%'
       OR Dropdown_Name LIKE '%Broker%' OR Dropdown_Name LIKE '%Commission%'
""")

print("BrokerCommission mappings:")
print("=" * 70)
for r in result:
    print(f"  Standard: {r['Dropdown_Name']:30} | ADNIC: {r['ADNIC']}")

if not result:
    print("  ⚠️ NO MAPPING FOUND for BrokerCommission!")

# Also check if "Broker Commission" exists with exact match
exact = db.fetch_all("""
    SELECT Dropdown_Name, ADNIC
    FROM Medical_CTN_Portal_Field_Mapping 
    WHERE ADNIC = 'Broker Commission'
""")

print("\nExact match for 'Broker Commission':")
if exact:
    for r in exact:
        print(f"  Standard: {r['Dropdown_Name']:30} | ADNIC: {r['ADNIC']}")
else:
    print("  ❌ NO MAPPING")

# Check staging config
from src.services.db_service.api_data.staging_config import ONLY_UPLOAD_MAPPED

print(f"\nConfiguration:")
print(f"  ONLY_UPLOAD_MAPPED: {ONLY_UPLOAD_MAPPED}")

if ONLY_UPLOAD_MAPPED and not exact:
    print("\n⚠️  CONCLUSION:")
    print("  'Broker Commission' has NO MAPPING in Medical_CTN_Portal_Field_Mapping")
    print("  ONLY_UPLOAD_MAPPED = True")
    print("  → Records with 'Broker Commission' are being SKIPPED during upload!")

db.disconnect()
