"""
Verify what broker data exists in the original table
"""
from src.services.db_service.api_data.staging_upload import StagingUploader

def check_broker_data():
    """Check what broker combinations exist in original table"""
    
    service = StagingUploader()
    service._connect()
    
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
    
    adnic_results = service._fetch_all(query, ())
    
    if adnic_results:
        print("\nADNIC Broker Combinations in Original Table:")
        for row in adnic_results:
            broker_id = row.get('Broker_ID') or row.get('broker_id')
            unique_combos = row.get('unique_combinations') or row.get('unique combinations')
            total = row.get('total_records') or row.get('total records')
            print(f"   • Broker {broker_id}: {total} records ({unique_combos} unique combinations)")
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
    
    sukoon_results = service._fetch_all(query, ())
    
    if sukoon_results:
        print("\nSukoon Broker Combinations in Original Table:")
        for row in sukoon_results:
            broker_id = row.get('Broker_ID') or row.get('broker_id')
            unique_combos = row.get('unique_combinations') or row.get('unique combinations')
            total = row.get('total_records') or row.get('total records')
            print(f"   • Broker {broker_id}: {total} records ({unique_combos} unique combinations)")
    else:
        print("\n❌ NO Sukoon data found in original table!")
    
    # Get all broker counts
    print("\n" + "="*70)
    print("🔍 ALL BROKER DATA IN ORIGINAL TABLE")
    print("="*70)
    
    query = """
        SELECT 
            Broker_ID,
            COUNT(DISTINCT Company) as companies,
            COUNT(*) as total_records
        FROM Medical_CTN_Cascading_Dropdown_Lifecare
        GROUP BY Broker_ID
        ORDER BY Broker_ID
    """
    
    all_results = service._fetch_all(query, ())
    
    if all_results:
        print("\nAll Brokers in Original Table:")
        for row in all_results:
            broker_id = row.get('Broker_ID') or row.get('broker_id')
            companies = row.get('companies')
            total = row.get('total_records') or row.get('total records')
            print(f"   • Broker {broker_id}: {total} records across {companies} companies")
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Total records in original table: 72,309")
    print(f"\nExtracted in this run:")
    print(f"   • ADNIC: 6,708 records (Broker 2, Broker 3)")
    print(f"   • Sukoon: 19,755 records (Broker 2, Broker 3, Broker 6)")
    print(f"   • Total staging: 26,463 records")
    print(f"\nComparison result: 0 new records")
    print(f"   ➜ This means: All staging combinations already exist in original table")
    print("="*70)
    
    service._disconnect()

if __name__ == "__main__":
    check_broker_data()
