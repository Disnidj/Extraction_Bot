"""
Check MySQL collation settings for the Company column
"""
from src.services.db_service.api_data.staging_upload import StagingUploader

def check_collation():
    """Check collation settings that affect string comparison"""
    
    service = StagingUploader()
    service._connect()
    
    print("\n" + "="*80)
    print("🔍 CHECKING DATABASE COLLATION SETTINGS")
    print("="*80)
    
    # Check table collation
    query = """
        SELECT 
            TABLE_NAME,
            TABLE_COLLATION
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = 'WebDB' 
        AND TABLE_NAME IN (
            'Medical_CTN_Cascading_Dropdown_Lifecare',
            'Medical_CTN_Cascading_Dropdown_Staging'
        )
    """
    
    results = service._fetch_all(query, ())
    
    print("\nTable Collations:")
    for row in results:
        table = row.get('TABLE_NAME')
        collation = row.get('TABLE_COLLATION')
        print(f"   • {table}: {collation}")
    
    # Check column collation
    query = """
        SELECT 
            COLUMN_NAME,
            COLLATION_NAME,
            DATA_TYPE,
            CHARACTER_SET_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'WebDB'
        AND TABLE_NAME = 'Medical_CTN_Cascading_Dropdown_Lifecare'
        AND COLUMN_NAME = 'Company'
    """
    
    results = service._fetch_all(query, ())
    
    print("\nCompany Column Collation:")
    for row in results:
        col = row.get('COLUMN_NAME')
        collation = row.get('COLLATION_NAME')
        dtype = row.get('DATA_TYPE')
        charset = row.get('CHARACTER_SET_NAME')
        print(f"   Column: {col}")
        print(f"   Type: {dtype}")
        print(f"   Charset: {charset}")
        print(f"   Collation: {collation}")
        
        if 'ci' in collation.lower():
            print(f"   ✅ Case-Insensitive (ci) collation - explains why comparison works!")
        else:
            print(f"   ⚠️  Case-Sensitive collation")
    
    # Test actual comparison behavior
    print("\n" + "="*80)
    print("🧪 TESTING ACTUAL COMPARISON BEHAVIOR")
    print("="*80)
    
    # Get actual stored value
    query = """
        SELECT DISTINCT Company
        FROM Medical_CTN_Cascading_Dropdown_Lifecare
        WHERE Company LIKE '%Sukoon%'
        LIMIT 1
    """
    
    results = service._fetch_all(query, ())
    if results:
        actual_value = results[0].get('Company')
        print(f"\nActual stored value: '{actual_value}'")
        
        # Test different case queries
        test_values = ['Sukoon Insurance', 'SUKOON INSURANCE', 'sukoon insurance', 'SuKoOn InSuRaNcE']
        
        for test_val in test_values:
            query = f"""
                SELECT COUNT(*) as count
                FROM Medical_CTN_Cascading_Dropdown_Lifecare
                WHERE Company = %s
            """
            
            results = service._fetch_all(query, (test_val,))
            count = results[0].get('count') if results else 0
            
            match_indicator = "✅" if count > 0 else "❌"
            print(f"   {match_indicator} WHERE Company = '{test_val}': {count} records")
    
    service._disconnect()

if __name__ == "__main__":
    check_collation()
