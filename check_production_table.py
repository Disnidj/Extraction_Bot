"""
Check if production table was already updated
"""
import mysql.connector

# Database credentials
DB_HOST = "139.185.45.34"
DB_NAME = "WebDB"
DB_USER = "admin"
DB_PASSWORD = "ad##876PPP*765"

# Table names
ORIGINAL_TABLE = "Medical_CTN_Cascading_Dropdown_Lifecare"

# Connect
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cursor = conn.cursor(dictionary=True)

# Check Orient Aura record count in production
cursor.execute(f"SELECT COUNT(*) as cnt FROM {ORIGINAL_TABLE} WHERE Company = 'Orient Aura'")
orient_count = cursor.fetchone()

print("=" * 80)
print(" PRODUCTION TABLE STATUS:")
print("=" * 80)
print(f"Orient Aura records in PRODUCTION: {orient_count['cnt']}")
print()

# Check all companies in production
cursor.execute(f"SELECT Company, COUNT(*) as cnt FROM {ORIGINAL_TABLE} GROUP BY Company ORDER BY Company")
all_companies = cursor.fetchall()

print("=" * 80)
print(" ALL COMPANIES IN PRODUCTION:")
print("=" * 80)
for c in all_companies:
    print(f"  - {c['Company']}: {c['cnt']:,} records")

cursor.close()
conn.close()
