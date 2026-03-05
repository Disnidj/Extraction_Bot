"""
Compare COMPANY_NAME_MAPPING with actual database names
"""
from src.services.db_service.api_data.staging_upload import StagingUploader
from src.services.db_service.api_data.staging_config import COMPANY_NAME_MAPPING

def compare_mappings():
    """Compare configured mappings with actual database company names"""
    
    service = StagingUploader()
    service._connect()
    
    # Get all company names from original table
    query = """
        SELECT DISTINCT Company
        FROM Medical_CTN_Cascading_Dropdown_Lifecare
        ORDER BY Company
    """
    
    results = service._fetch_all(query, ())
    db_companies = [row.get('Company') or row.get('company') for row in results]
    
    print("\n" + "="*80)
    print("🔍 COMPANY NAME MAPPING VERIFICATION")
    print("="*80)
    
    print("\n📋 CONFIGURED MAPPINGS:")
    print("-" * 80)
    for portal, mapped_name in COMPANY_NAME_MAPPING.items():
        print(f"   {portal:20} → {mapped_name}")
    
    print("\n📊 DATABASE COMPANIES:")
    print("-" * 80)
    for company in db_companies:
        print(f"   • {company}")
    
    print("\n⚠️  MISMATCH DETECTION:")
    print("-" * 80)
    
    mismatches = []
    for portal, mapped_name in COMPANY_NAME_MAPPING.items():
        if mapped_name not in db_companies:
            # Check if there's a case-insensitive match
            case_insensitive_match = None
            for db_comp in db_companies:
                if db_comp.lower() == mapped_name.lower():
                    case_insensitive_match = db_comp
                    break
            
            if case_insensitive_match:
                mismatches.append({
                    'portal': portal,
                    'mapped': mapped_name,
                    'actual': case_insensitive_match,
                    'type': 'CASE_MISMATCH'
                })
                print(f"❌ {portal}:")
                print(f"      Mapped to: '{mapped_name}'")
                print(f"      DB has:    '{case_insensitive_match}'")
                print(f"      Issue: Case mismatch (will cause comparison failures!)")
                print()
            else:
                mismatches.append({
                    'portal': portal,
                    'mapped': mapped_name,
                    'actual': None,
                    'type': 'NOT_FOUND'
                })
                print(f"❌ {portal}:")
                print(f"      Mapped to: '{mapped_name}'")
                print(f"      DB has:    NOT FOUND")
                print(f"      Issue: Company doesn't exist in database!")
                print()
    
    if not mismatches:
        print("✅ All mappings match database company names!")
    else:
        print("\n" + "="*80)
        print(f"⚠️  FOUND {len(mismatches)} MISMATCHES")
        print("="*80)
        print("\n💡 RECOMMENDED FIXES:")
        print("-" * 80)
        for mm in mismatches:
            if mm['type'] == 'CASE_MISMATCH':
                print(f'   "{mm["portal"]}": "{mm["actual"]}",  # Changed from "{mm["mapped"]}"')
    
    service._disconnect()

if __name__ == "__main__":
    compare_mappings()
