"""
Test Portal Mapper - Verify Database Connection and Portal Queries
"""

from src.services.broker_service.portal_mapper import PortalMapper
from src.config.broker_config import get_active_broker_ids, get_broker_name

def main():
    print("=" * 70)
    print("🧪 TESTING PORTAL MAPPER")
    print("=" * 70)
    
    # Initialize portal mapper
    mapper = PortalMapper()
    
    # Get active brokers
    active_brokers = get_active_broker_ids()
    print(f"\n✅ Active brokers in config: {active_brokers}")
    
    # Test 1: Fetch portals for each active broker
    print(f"\n{'=' * 70}")
    print("TEST 1: Fetch Portals for Each Broker")
    print("=" * 70)
    
    for broker_id in active_brokers:
        print(f"\n📋 Broker {broker_id} - {get_broker_name(broker_id)}:")
        try:
            portals = mapper.fetch_portals_for_broker(broker_id)
            if portals:
                print(f"   Found {len(portals)} portal(s):")
                for portal in portals:
                    print(f"      • {portal}")
            else:
                print(f"   ⚠️  No portals found in database")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 2: Analyze portal distribution across all brokers
    print(f"\n{'=' * 70}")
    print("TEST 2: Analyze Portal Distribution")
    print("=" * 70)
    
    try:
        analysis = mapper.analyze_portal_distribution(active_brokers)
        
        print(f"\n📊 Summary:")
        print(f"   Total unique portals: {analysis['total_unique']}")
        print(f"   Shared portals: {len(analysis['shared'])}")
        print(f"   Broker-specific portals: {len(analysis['unique'])}")
        
        if analysis['shared']:
            print(f"\n🔗 Shared Portals:")
            for portal, broker_list in analysis['shared'].items():
                broker_names = [f"Broker {bid} ({get_broker_name(bid)})" for bid in broker_list]
                print(f"   • {portal}")
                print(f"      → Used by: {', '.join(broker_names)}")
        
        if analysis['unique']:
            print(f"\n🔒 Broker-Specific Portals:")
            for portal, broker_id in analysis['unique'].items():
                print(f"   • {portal}")
                print(f"      → Only used by: Broker {broker_id} ({get_broker_name(broker_id)})")
        
        if not analysis['shared'] and not analysis['unique']:
            print("\n⚠️  No portal mappings found in database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Find which brokers use specific portals
    print(f"\n{'=' * 70}")
    print("TEST 3: Find Brokers Using Specific Portals")
    print("=" * 70)
    
    test_portals = ["adnic", "daman", "orient", "medgulf", "gig"]
    
    for portal in test_portals:
        print(f"\n🔍 Searching for portal: {portal}")
        try:
            brokers_using_portal = mapper.get_brokers_using_portal(portal)
            if brokers_using_portal:
                print(f"   ✅ Found {len(brokers_using_portal)} broker(s):")
                for bid in brokers_using_portal:
                    print(f"      • Broker {bid} - {get_broker_name(bid)}")
            else:
                print(f"   ℹ️  No brokers using this portal")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 4: Database connection status
    print(f"\n{'=' * 70}")
    print("TEST 4: Database Connection Status")
    print("=" * 70)
    
    try:
        # Try a simple query
        conn = mapper.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Medical_CTN_Broker_Portal_Mapping")
        total_mappings = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"\n✅ Database connection successful")
        print(f"   Total mappings in table: {total_mappings}")
        
    except Exception as e:
        print(f"\n❌ Database connection failed")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'=' * 70}")
    print("✅ TESTING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
