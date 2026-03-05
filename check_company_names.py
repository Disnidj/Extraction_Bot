"""
Check for Sukoon company name variations
"""
from src.services.db_service.api_data.staging_upload import StagingUploader

def check_sukoon_names():
    """Check what company names exist with 'sukoon' in them"""
    
    service = StagingUploader()
    service._connect()
    
    # Check all companies in original table
    print("\n" + "="*70)
    print("🔍 ALL COMPANIES IN ORIGINAL TABLE")
    print("="*70)
    
    query = """
        SELECT 
            DISTINCT Company,
            COUNT(*) as total_records
        FROM Medical_CTN_Cascading_Dropdown_Lifecare
        GROUP BY Company
        ORDER BY Company
    """
    
    results = service._fetch_all(query, ())
    
    print(f"\nTotal companies: {len(results)}\n")
    for row in results:
        company = row.get('Company') or row.get('company')
        total = row.get('total_records') or row.get('total records')
        marker = "🎯" if 'sukoon' in company.lower() or 'insurance' in company.lower() else "  "
        print(f"   {marker} {company}: {total} records")
    
    # Check staging table for comparison
    print("\n" + "="*70)
    print("🔍 COMPANIES IN STAGING TABLE (Current Run)")
    print("="*70)
    
    query = """
        SELECT 
            DISTINCT Company,
            COUNT(*) as total_records
        FROM Medical_CTN_Cascading_Dropdown_Staging
        GROUP BY Company
        ORDER BY Company
    """
    
    results = service._fetch_all(query, ())
    
    if results:
        print(f"\nTotal companies in staging: {len(results)}\n")
        for row in results:
            company = row.get('Company') or row.get('company')
            total = row.get('total_records') or row.get('total records')
            print(f"   • {company}: {total} records")
    else:
        print("\n❌ Staging table is empty!")
    
    service._disconnect()

if __name__ == "__main__":
    check_sukoon_names()
