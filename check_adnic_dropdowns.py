"""Quick script to check ADNIC dropdown names in database"""
from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

db = MySQLDatabase(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
db.connect()

# Get all unique dropdown names for ADNIC
result = db.fetch_all("""
    SELECT DISTINCT Dropdown_Name 
    FROM Medical_CTN_Cascading_Dropdown_Lifecare 
    WHERE Company='ADNIC' 
    ORDER BY Dropdown_Name
""")

print("Dropdown names in DATABASE for ADNIC:")
print("=" * 50)
for r in result:
    print(f"  - {r['Dropdown_Name']}")

print(f"\nTotal: {len(result)} dropdown names")

# Check if BrokerCommission exists
broker_comm = db.fetch_all("""
    SELECT COUNT(*) as count
    FROM Medical_CTN_Cascading_Dropdown_Lifecare 
    WHERE Company='ADNIC' AND Dropdown_Name='BrokerCommission'
""")

print(f"\nBrokerCommission records in database: {broker_comm[0]['count']}")

db.disconnect()
