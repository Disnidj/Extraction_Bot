"""
Find where the 48 NEW and 3 DELETED values come from - across ALL companies
"""
import pymysql

connection = pymysql.connect(
    host='139.185.45.34',
    user='admin',
    password='ad##876PPP*765',
    database='WebDB',
    port=3306
)
cursor = connection.cursor(pymysql.cursors.DictCursor)

STAGING_TABLE = "Medical_CTN_Cascading_Dropdown_Staging"
ORIGINAL_TABLE = "Medical_CTN_Cascading_Dropdown_Lifecare"

# Get all companies in staging
cursor.execute(f"SELECT DISTINCT Company FROM {STAGING_TABLE}")
companies = [row['Company'] for row in cursor.fetchall()]

print("=" * 80)
print("COMPARISON: ALL COMPANIES - Staging vs Original")
print("=" * 80)

total_new = 0
total_deleted = 0
total_unchanged = 0

for company in companies:
    # Get dropdown names that exist in staging for this company
    cursor.execute(f"""
        SELECT DISTINCT Dropdown_Name 
        FROM {STAGING_TABLE}
        WHERE Company = %s
    """, (company,))
    dropdown_names = [row['Dropdown_Name'] for row in cursor.fetchall()]
    
    if not dropdown_names:
        continue
    
    placeholders = ", ".join(["%s"] * len(dropdown_names))
    
    # Staging records (full key)
    cursor.execute(f"""
        SELECT Company, TPA, Network, Region, Dropdown_Name, Selection_Value
        FROM {STAGING_TABLE}
        WHERE Company = %s AND Dropdown_Name IN ({placeholders})
    """, tuple([company] + dropdown_names))
    staging_keys = set()
    for row in cursor.fetchall():
        key = (row['Company'], row['TPA'], row['Network'], row['Region'], row['Dropdown_Name'], row['Selection_Value'])
        staging_keys.add(key)
    
    # Original records (full key, same dropdowns only)
    cursor.execute(f"""
        SELECT Company, TPA, Network, Region, Dropdown_Name, Selection_Value
        FROM {ORIGINAL_TABLE}
        WHERE Company = %s AND Dropdown_Name IN ({placeholders})
    """, tuple([company] + dropdown_names))
    original_keys = set()
    for row in cursor.fetchall():
        key = (row['Company'], row['TPA'], row['Network'], row['Region'], row['Dropdown_Name'], row['Selection_Value'])
        original_keys.add(key)
    
    # Calculate differences
    new_records = staging_keys - original_keys
    deleted_records = original_keys - staging_keys
    unchanged_records = staging_keys & original_keys
    
    print(f"\n[{company}]")
    print(f"  Staging: {len(staging_keys)}, Original (common dropdowns): {len(original_keys)}")
    print(f"  [+] NEW: {len(new_records)}, [-] DELETED: {len(deleted_records)}, [=] UNCHANGED: {len(unchanged_records)}")
    
    total_new += len(new_records)
    total_deleted += len(deleted_records)
    total_unchanged += len(unchanged_records)
    
    # Show details if there are changes
    if new_records:
        print(f"\n  NEW VALUES ({len(new_records)}):")
        for i, key in enumerate(list(new_records)[:5]):
            print(f"    {i+1}. Dropdown: {key[4]}, Value: \"{key[5]}\"")
            print(f"       TPA: {key[1]}, Network: {key[2]}")
        if len(new_records) > 5:
            print(f"    ... and {len(new_records) - 5} more")
    
    if deleted_records:
        print(f"\n  DELETED VALUES ({len(deleted_records)}):")
        for i, key in enumerate(list(deleted_records)[:5]):
            print(f"    {i+1}. Dropdown: {key[4]}, Value: \"{key[5]}\"")
            print(f"       TPA: {key[1]}, Network: {key[2]}")
        if len(deleted_records) > 5:
            print(f"    ... and {len(deleted_records) - 5} more")

print("\n" + "=" * 80)
print("TOTAL ACROSS ALL COMPANIES:")
print("=" * 80)
print(f"  [+] NEW: {total_new}")
print(f"  [-] DELETED: {total_deleted}")
print(f"  [=] UNCHANGED: {total_unchanged}")
print(f"  TOTAL IN STAGING: {total_new + total_unchanged}")

connection.close()
