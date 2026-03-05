"""
Simulate what the comparison does with mismatched company names
"""
from src.services.db_service.api_data.staging_upload import StagingUploader

def trace_comparison_flow():
    """Trace the exact SQL queries used in comparison"""
    
    service = StagingUploader()
    service._connect()
    
    # Companies passed to compare_tables (from standardize_company_name)
    companies_from_staging = ["ADNIC", "SUKOON INSURANCE"]
    
    print("\n" + "="*80)
    print("🔍 TRACING COMPARISON FLOW")
    print("="*80)
    
    for company in companies_from_staging:
        print(f"\n📊 Processing company: '{company}'")
        print("-" * 80)
        
        # Query 1: Get staging records
        staging_query = """
            SELECT COUNT(*) as count
            FROM Medical_CTN_Cascading_Dropdown_Staging
            WHERE Company = %s
        """
        
        staging_result = service._fetch_all(staging_query, (company,))
        staging_count = staging_result[0].get('count') if staging_result else 0
        
        print(f"   Staging query: WHERE Company = '{company}'")
        print(f"      → Found: {staging_count} records")
        
        # Query 2: Get original records (uses SAME company name)
        original_query = """
            SELECT COUNT(*) as count
            FROM Medical_CTN_Cascading_Dropdown_Lifecare
            WHERE Company = %s
        """
        
        original_result = service._fetch_all(original_query, (company,))
        original_count = original_result[0].get('count') if original_result else 0
        
        print(f"   Original query: WHERE Company = '{company}'")
        print(f"      → Found: {original_count} records")
        
        if staging_count > 0 and original_count == 0:
            print(f"   ⚠️  PROBLEM: {staging_count} staging records but 0 original records!")
            print(f"      → Comparison will treat all {staging_count} as NEW records")
            print(f"      → But log showed 0 NEW records... Why?")
        elif staging_count > 0 and original_count > 0:
            print(f"   ✅ Both tables have data - comparison will work correctly")
        
        print()
    
    # Check what the actual company name is in original for Sukoon
    print("\n" + "="*80)
    print("🔍 CHECKING ACTUAL SUKOON COMPANY NAME IN ORIGINAL TABLE")
    print("="*80)
    
    sukoon_query = """
        SELECT DISTINCT Company
        FROM Medical_CTN_Cascading_Dropdown_Lifecare
        WHERE Company LIKE '%Sukoon%' OR Company LIKE '%SUKOON%' OR Company LIKE '%Insurance%'
    """
    
    results = service._fetch_all(sukoon_query, ())
    
    print("\nCompanies in original table matching 'Sukoon' or 'Insurance':")
    for row in results:
        company = row.get('Company') or row.get('company')
        print(f"   • '{company}'")
    
    service._disconnect()

if __name__ == "__main__":
    trace_comparison_flow()
