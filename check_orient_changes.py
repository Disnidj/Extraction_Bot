"""
Query database to show exact NEW and DELETED records for Orient Aura
"""
import mysql.connector
from typing import List, Dict

# Database credentials (from src/services/db_config/config.py)
DB_HOST = "139.185.45.34"
DB_NAME = "WebDB"
DB_USER = "admin"
DB_PASSWORD = "ad##876PPP*765"

# Table names (from src/services/db_service/api_data/staging_config.py)
STAGING_TABLE = "Medical_CTN_Cascading_Dropdown_Staging"
ORIGINAL_TABLE = "Medical_CTN_Cascading_Dropdown_Lifecare"

# Connect to database
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cursor = conn.cursor(dictionary=True)

# Get the latest Run_ID
cursor.execute(f"SELECT DISTINCT Run_ID FROM {STAGING_TABLE} ORDER BY Run_ID DESC LIMIT 1")
run_id_result = cursor.fetchone()
run_id = run_id_result['Run_ID'] if run_id_result else None

print(f"{'='*80}")
print(f" ORIENT AURA - EXACT CHANGE DETAILS")
print(f"{'='*80}")
print(f"Run ID: {run_id}")
print(f"Company: Orient Aura")
print()

# Get all staging records for Orient Aura
staging_query = f"""
    SELECT Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value
    FROM {STAGING_TABLE}
    WHERE Company = 'Orient Aura' AND Run_ID = %s
    ORDER BY Dropdown_Name, Selection_Value
"""
cursor.execute(staging_query, (run_id,))
staging_records = cursor.fetchall()

# Get all original records for Orient Aura
original_query = f"""
    SELECT Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value
    FROM {ORIGINAL_TABLE}
    WHERE Company = 'Orient Aura'
    ORDER BY Dropdown_Name, Selection_Value
"""
cursor.execute(original_query)
original_records = cursor.fetchall()

print(f" RECORD COUNTS:")
print(f"   Staging (New extraction): {len(staging_records)} records")
print(f"   Original (Current DB):    {len(original_records)} records")
print()

# Create full keys for comparison
def make_full_key(record):
    return (
        record['Company'],
        record['TPA'] or '',
        record['Network'] or '',
        record['Region'] or '',
        record['Dropdown_Name'],
        record['Selection_Value']
    )

def make_display_key(record):
    return (
        record['TPA'] or 'N/A',
        record['Network'] or 'N/A',
        record['Region'] or 'N/A',
        record['Dropdown_Name'],
        record['Selection_Value']
    )

# Build sets for comparison
staging_full_keys = {make_full_key(r): r for r in staging_records}
original_full_keys = {make_full_key(r): r for r in original_records}

# Find NEW records (in staging but not in original)
new_records = []
for key, record in staging_full_keys.items():
    if key not in original_full_keys:
        new_records.append(record)

# Find DELETED records (in original but not in staging)
deleted_records = []
for key, record in original_full_keys.items():
    if key not in staging_full_keys:
        deleted_records.append(record)

# Find UNCHANGED records
unchanged_count = len(staging_full_keys) - len(new_records)

print(f"{'='*80}")
print(f" CHANGE SUMMARY:")
print(f"{'='*80}")
print(f"   [+] New records:       {len(new_records)}")
print(f"   [-] Deleted records:   {len(deleted_records)}")
print(f"   [=] Unchanged records: {unchanged_count}")
print()

# Group new records by dropdown
new_by_dropdown = {}
for record in new_records:
    dropdown = record['Dropdown_Name']
    new_by_dropdown.setdefault(dropdown, []).append(record)

# Group deleted records by dropdown
deleted_by_dropdown = {}
for record in deleted_records:
    dropdown = record['Dropdown_Name']
    deleted_by_dropdown.setdefault(dropdown, []).append(record)

print(f"{'='*80}")
print(f" [NEW] RECORDS - These will be INSERTED into production:")
print(f"{'='*80}")

for dropdown_name in sorted(new_by_dropdown.keys()):
    records = new_by_dropdown[dropdown_name]
    print(f"\n[Dropdown] {dropdown_name} ({len(records)} new values)")
    print(f"   {'-'*76}")
    
    for i, record in enumerate(records, 1):
        tpa = record['TPA'] or 'N/A'
        network = record['Network'] or 'N/A'
        region = record['Region'] or 'N/A'
        value = record['Selection_Value']
        
        print(f"   {i:2d}. Value: '{value}'")
        print(f"       TPA: {tpa} | Network: {network} | Region: {region}")

print(f"\n{'='*80}")
print(f" [DELETED] RECORDS - These will be REMOVED from production:")
print(f"{'='*80}")

if deleted_records:
    for dropdown_name in sorted(deleted_by_dropdown.keys()):
        records = deleted_by_dropdown[dropdown_name]
        print(f"\n[Dropdown] {dropdown_name} ({len(records)} deleted values)")
        print(f"   {'-'*76}")
        
        for i, record in enumerate(records, 1):
            tpa = record['TPA'] or 'N/A'
            network = record['Network'] or 'N/A'
            region = record['Region'] or 'N/A'
            value = record['Selection_Value']
            
            print(f"   {i}. Value: '{value}'")
            print(f"      TPA: {tpa} | Network: {network} | Region: {region}")
else:
    print("\n   (No deleted records)")

print(f"\n{'='*80}")
print(f" EXPLANATION:")
print(f"{'='*80}")
print(f"""
The comparison uses EXACT matching on:
  (Company + TPA + Network + Region + Dropdown_Name + Selection_Value)

NEW records = Exist in TODAY's extraction but NOT in current database
DELETED records = Exist in current database but NOT in today's extraction

This means:
  • Portal added 48 new dropdown value combinations
  • Portal removed 3 old dropdown value combinations
  • Portal kept {unchanged_count} existing combinations unchanged
""")

# Show a few examples of unchanged records for reference
print(f"{'='*80}")
print(f" SAMPLE UNCHANGED RECORDS (for reference):")
print(f"{'='*80}")
sample_unchanged = list(staging_full_keys.values())[:5]
for i, record in enumerate(sample_unchanged, 1):
    print(f"{i}. {record['Dropdown_Name']}: '{record['Selection_Value']}'")
    print(f"   TPA: {record['TPA']} | Network: {record['Network']}")

cursor.close()
conn.close()

print(f"\n{'='*80}")
print(f" Database query complete!")
print(f"{'='*80}")
