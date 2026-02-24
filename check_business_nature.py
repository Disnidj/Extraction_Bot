"""
Compare Business_Nature full records with TPA/Network/Region
"""
import mysql.connector

conn = mysql.connector.connect(host='139.185.45.34', user='admin', password='ad##876PPP*765', database='WebDB')
cursor = conn.cursor(dictionary=True)

# Get Business_Nature FULL records from STAGING
cursor.execute('''SELECT Company, TPA, Network, Region, Dropdown_Name, Selection_Value 
    FROM Medical_CTN_Cascading_Dropdown_Staging 
    WHERE Company = %s AND Dropdown_Name = %s AND Run_ID = %s''', 
    ('Orient Aura', 'Business_Nature', '20260224_132056'))
staging_rows = cursor.fetchall()

# Get Business_Nature FULL records from ORIGINAL  
cursor.execute('''SELECT Company, TPA, Network, Region, Dropdown_Name, Selection_Value 
    FROM Medical_CTN_Cascading_Dropdown_Lifecare 
    WHERE Company = %s AND Dropdown_Name = %s''', ('Orient Aura', 'Business_Nature'))
original_rows = cursor.fetchall()

print("="*80)
print("Business_Nature FULL RECORD COMPARISON")
print("="*80)
print(f"Staging records: {len(staging_rows)}")
print(f"Original records: {len(original_rows)}")

def make_key(r):
    return (r['Company'], r['TPA'] or '', r['Network'] or '', r['Region'] or '', r['Dropdown_Name'], r['Selection_Value'])

staging_keys = set(make_key(r) for r in staging_rows)
original_keys = set(make_key(r) for r in original_rows)

new = staging_keys - original_keys
deleted = original_keys - staging_keys
unchanged = staging_keys & original_keys

print(f"\n[+] NEW (in staging, not in original): {len(new)}")
print(f"[-] DELETED (in original, not in staging): {len(deleted)}")
print(f"[=] UNCHANGED (exact match): {len(unchanged)}")

print("\n" + "="*80)
print("Sample TPA/Network combinations in STAGING:")
print("="*80)
tpa_networks = list(set((r['TPA'], r['Network']) for r in staging_rows))
for i, (tpa, net) in enumerate(tpa_networks[:5]):
    tpa_short = tpa[:50] if tpa else 'N/A'
    net_short = net[:40] if net else 'N/A'
    print(f"  {i+1}. TPA: {tpa_short}")
    print(f"     Network: {net_short}")

print("\n" + "="*80)
print("Sample TPA/Network combinations in ORIGINAL:")
print("="*80)
tpa_networks = list(set((r['TPA'], r['Network']) for r in original_rows))
for i, (tpa, net) in enumerate(tpa_networks[:5]):
    tpa_short = tpa[:50] if tpa else 'N/A'
    net_short = net[:40] if net else 'N/A'
    print(f"  {i+1}. TPA: {tpa_short}")
    print(f"     Network: {net_short}")

if new:
    print("\n" + "="*80)
    print("NEW RECORDS (sample):")
    print("="*80)
    for i, key in enumerate(list(new)[:3]):
        print(f"  {i+1}. TPA: {key[1][:40]}")
        print(f"     Network: {key[2][:40] if key[2] else 'N/A'}")
        print(f"     Value: {key[5][:50]}")

if deleted:
    print("\n" + "="*80)
    print("DELETED RECORDS (sample):")
    print("="*80)
    for i, key in enumerate(list(deleted)[:3]):
        print(f"  {i+1}. TPA: {key[1][:40]}")
        print(f"     Network: {key[2][:40] if key[2] else 'N/A'}")
        print(f"     Value: {key[5][:50]}")

cursor.close()
conn.close()
