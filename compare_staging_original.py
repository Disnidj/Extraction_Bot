"""
Check staging vs original dropdown comparison
"""
import mysql.connector

DB_HOST = "139.185.45.34"
DB_NAME = "WebDB"
DB_USER = "admin" 
DB_PASSWORD = "ad##876PPP*765"

STAGING_TABLE = "Medical_CTN_Cascading_Dropdown_Staging"
ORIGINAL_TABLE = "Medical_CTN_Cascading_Dropdown_Lifecare"

conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = conn.cursor(dictionary=True)

# Get latest run
cursor.execute(f"SELECT DISTINCT Run_ID FROM {STAGING_TABLE} ORDER BY Run_ID DESC LIMIT 1")
run_id = cursor.fetchone()['Run_ID']

print("="*80)
print(f"STAGING vs ORIGINAL COMPARISON - Orient Aura - Run: {run_id}")
print("="*80)

# Get dropdown names in staging
cursor.execute(f"SELECT DISTINCT Dropdown_Name FROM {STAGING_TABLE} WHERE Company = %s AND Run_ID = %s", ('Orient Aura', run_id))
staging_dropdowns = [r['Dropdown_Name'] for r in cursor.fetchall()]

print(f"\n[STAGING TABLE] Orient Aura has {len(staging_dropdowns)} dropdown types (MAPPED names):")
for d in staging_dropdowns:
    cursor.execute(f"SELECT COUNT(*) as cnt FROM {STAGING_TABLE} WHERE Company = %s AND Run_ID = %s AND Dropdown_Name = %s", ('Orient Aura', run_id, d))
    cnt = cursor.fetchone()['cnt']
    print(f"  - {d}: {cnt} values")

# Get dropdown names in original
cursor.execute(f"SELECT DISTINCT Dropdown_Name FROM {ORIGINAL_TABLE} WHERE Company = %s", ('Orient Aura',))
original_dropdowns = [r['Dropdown_Name'] for r in cursor.fetchall()]

print(f"\n[ORIGINAL TABLE] Orient Aura has {len(original_dropdowns)} dropdown types:")
for d in original_dropdowns:
    cursor.execute(f"SELECT COUNT(*) as cnt FROM {ORIGINAL_TABLE} WHERE Company = %s AND Dropdown_Name = %s", ('Orient Aura', d))
    cnt = cursor.fetchone()['cnt']
    print(f"  - {d}: {cnt} values")

# Compare dropdown types
common = set(staging_dropdowns) & set(original_dropdowns)
only_staging = set(staging_dropdowns) - set(original_dropdowns)
only_original = set(original_dropdowns) - set(staging_dropdowns)

print(f"\n" + "="*80)
print("DROPDOWN TYPE COMPARISON:")
print("="*80)
print(f"  Common dropdowns (in BOTH): {len(common)}")
print(f"  Only in STAGING (new mapped types): {len(only_staging)}")
print(f"  Only in ORIGINAL (not extracted today): {len(only_original)}")

if only_staging:
    print(f"\n  NEW dropdown types (will be added):")
    for d in only_staging:
        print(f"    + {d}")

if only_original:
    print(f"\n  Dropdown types ONLY in Original (NOT in staging extraction):")
    for d in only_original:
        print(f"    - {d}")

# Now compare values for COMMON dropdowns
if common:
    print(f"\n" + "="*80)
    print(f"VALUE COMPARISON (for {len(common)} common dropdowns):")
    print("="*80)
    
    placeholders = ", ".join(["%s"] * len(common))
    
    # Get staging values for common dropdowns
    cursor.execute(f"""
        SELECT Company, TPA, Network, Region, Dropdown_Name, Selection_Value
        FROM {STAGING_TABLE}
        WHERE Company = %s AND Run_ID = %s AND Dropdown_Name IN ({placeholders})
    """, tuple(['Orient Aura', run_id] + list(common)))
    staging_values = cursor.fetchall()
    
    # Get original values for common dropdowns
    cursor.execute(f"""
        SELECT Company, TPA, Network, Region, Dropdown_Name, Selection_Value
        FROM {ORIGINAL_TABLE}
        WHERE Company = %s AND Dropdown_Name IN ({placeholders})
    """, tuple(['Orient Aura'] + list(common)))
    original_values = cursor.fetchall()
    
    # Create full keys
    def make_key(r):
        return (r['Company'], r['TPA'] or '', r['Network'] or '', r['Region'] or '', r['Dropdown_Name'], r['Selection_Value'])
    
    staging_keys = set(make_key(r) for r in staging_values)
    original_keys = set(make_key(r) for r in original_values)
    
    new_values = staging_keys - original_keys
    deleted_values = original_keys - staging_keys
    unchanged = staging_keys & original_keys
    
    print(f"\n  Staging records (common dropdowns): {len(staging_values)}")
    print(f"  Original records (common dropdowns): {len(original_values)}")
    print(f"  -----------------------------------------")
    print(f"  [+] NEW values (in staging, not original): {len(new_values)}")
    print(f"  [-] DELETED values (in original, not staging): {len(deleted_values)}")
    print(f"  [=] UNCHANGED (exact match): {len(unchanged)}")
    
    # Show some examples
    if new_values:
        print(f"\n  Sample NEW values:")
        for i, key in enumerate(list(new_values)[:5]):
            print(f"    {i+1}. {key[4]}: '{key[5][:50]}...' (TPA: {key[1][:30]})")
    
    if deleted_values:
        print(f"\n  Sample DELETED values:")
        for i, key in enumerate(list(deleted_values)[:5]):
            print(f"    {i+1}. {key[4]}: '{key[5][:50]}...' (TPA: {key[1][:30]})")

cursor.close()
conn.close()
print(f"\n" + "="*80)
print("Done!")
