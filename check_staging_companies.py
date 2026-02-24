"""
Check what's in the staging table for the latest run
"""
import mysql.connector

# Database credentials
DB_HOST = "139.185.45.34"
DB_NAME = "WebDB"
DB_USER = "admin"
DB_PASSWORD = "ad##876PPP*765"

# Table names
STAGING_TABLE = "Medical_CTN_Cascading_Dropdown_Staging"

# Connect
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cursor = conn.cursor(dictionary=True)

# Check what Run_IDs exist
cursor.execute(f"SELECT DISTINCT Run_ID FROM {STAGING_TABLE} ORDER BY Run_ID DESC LIMIT 5")
run_ids = cursor.fetchall()

print("=" * 80)
print(" RECENT RUN IDs IN STAGING TABLE:")
print("=" * 80)
for r in run_ids:
    print(f"  - {r['Run_ID']}")

# Check what companies exist for latest run
if run_ids:
    latest_run = run_ids[0]['Run_ID']
    cursor.execute(f"SELECT DISTINCT Company FROM {STAGING_TABLE} WHERE Run_ID = %s", (latest_run,))
    companies = cursor.fetchall()
    
    print(f"\n" + "=" * 80)
    print(f" COMPANIES IN RUN {latest_run}:")
    print("=" * 80)
    for c in companies:
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {STAGING_TABLE} WHERE Run_ID = %s AND Company = %s", (latest_run, c['Company']))
        count = cursor.fetchone()
        print(f"  - {c['Company']}: {count['cnt']} records")

cursor.close()
conn.close()
