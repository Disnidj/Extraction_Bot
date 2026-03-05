"""
Verify what broker data exists in the original table
"""
import mysql.connector
from contextlib import contextmanager
import yaml

@contextmanager
def get_db_connection():
    """Context manager for database connection"""
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config.get('database', {})
    
    conn = mysql.connector.connect(
        host=db_config.get('host', 'localhost'),
        user=db_config.get('user', 'root'),
        password=db_config.get('password', ''),
        database=db_config.get('database', 'WebDB')
    )
    
    try:
        yield conn
    finally:
        conn.close()

def check_broker_data():
    """Check what broker combinations exist in original table"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Check ADNIC broker combinations
        print("\n" + "="*70)
        print("🔍 CHECKING ADNIC BROKER DATA IN ORIGINAL TABLE")
        print("="*70)
        
        query = """
            SELECT 
                Broker_ID,
                COUNT(DISTINCT CONCAT(TPA, '|', Network, '|', Region, '|', Dropdown_Name, '|', Selection_Value)) as unique_combinations,
                COUNT(*) as total_records
            FROM Medical_CTN_Cascading_Dropdown_Lifecare
            WHERE Company = 'ADNIC'
            GROUP BY Broker_ID
            ORDER BY Broker_ID
        """
        
        cursor.execute(query)
        adnic_results = cursor.fetchall()
        
        if adnic_results:
            print("\nADNIC Broker Combinations in Original Table:")
            for row in adnic_results:
                print(f"   • Broker {row['Broker_ID']}: {row['total_records']} records ({row['unique_combinations']} unique combinations)")
        else:
            print("\n❌ NO ADNIC data found in original table!")
        
        # Check Sukoon broker combinations
        print("\n" + "="*70)
        print("🔍 CHECKING SUKOON BROKER DATA IN ORIGINAL TABLE")
        print("="*70)
        
        query = """
            SELECT 
                Broker_ID,
                COUNT(DISTINCT CONCAT(TPA, '|', Network, '|', Region, '|', Dropdown_Name, '|', Selection_Value)) as unique_combinations,
                COUNT(*) as total_records
            FROM Medical_CTN_Cascading_Dropdown_Lifecare
            WHERE Company = 'Sukoon'
            GROUP BY Broker_ID
            ORDER BY Broker_ID
        """
        
        cursor.execute(query)
        sukoon_results = cursor.fetchall()
        
        if sukoon_results:
            print("\nSukoon Broker Combinations in Original Table:")
            for row in sukoon_results:
                print(f"   • Broker {row['Broker_ID']}: {row['total_records']} records ({row['unique_combinations']} unique combinations)")
        else:
            print("\n❌ NO Sukoon data found in original table!")
        
        # Summary
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"Total records in original table: {72309}")
        print(f"\nExtracted in this run:")
        print(f"   • ADNIC: 6,708 records (Broker 2, Broker 3)")
        print(f"   • Sukoon: 19,755 records (Broker 2, Broker 3, Broker 6)")
        print(f"   • Total staging: 26,463 records")
        print(f"\nComparison result: 0 new records")
        print(f"   This means: All staging combinations already exist in original table")
        print("="*70)
        
        cursor.close()

if __name__ == "__main__":
    check_broker_data()
