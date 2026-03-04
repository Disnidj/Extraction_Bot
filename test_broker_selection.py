"""
Test Broker Selection - Verify Interactive and CLI Selection Methods
"""

from src.services.broker_service.broker_manager import (
    select_brokers_interactive,
    select_brokers_from_cli,
    confirm_broker_selection
)
from src.config.broker_config import (
    get_active_broker_ids,
    get_broker_name,
    get_broker_summary,
    validate_broker_ids
)
from src.services.broker_service.portal_mapper import PortalMapper


def test_interactive_selection():
    """Test interactive broker selection menu"""
    print("=" * 70)
    print("TEST 1: Interactive Broker Selection")
    print("=" * 70)
    print("\nThis will display the interactive broker selection menu.")
    print("Try different inputs:")
    print("  • Enter '2' for single broker")
    print("  • Enter '2,3' for multiple brokers")
    print("  • Enter 'all' for all brokers")
    print("  • Enter 'q' to cancel\n")
    
    selected_brokers = select_brokers_interactive()
    
    if selected_brokers:
        print(f"\n✅ Successfully selected {len(selected_brokers)} broker(s):")
        for bid in selected_brokers:
            print(f"   • {get_broker_summary(bid)}")
        return selected_brokers
    else:
        print("\n❌ No brokers selected or cancelled")
        return None


def test_cli_selection():
    """Test CLI-based broker selection"""
    print("\n" + "=" * 70)
    print("TEST 2: CLI Broker Selection")
    print("=" * 70)
    
    test_cases = [
        ("all", "Select all brokers"),
        ("2", "Select single broker (2)"),
        ("2,3", "Select multiple brokers (2,3)"),
        ("2,3,6", "Select all three brokers"),
        ("999", "Invalid broker ID (should fail)"),
        ("2,999", "Mix of valid and invalid (should fail)"),
    ]
    
    for cli_input, description in test_cases:
        print(f"\n🔍 Test: {description}")
        print(f"   Input: --brokers={cli_input}")
        
        result = select_brokers_from_cli(cli_input)
        
        if result:
            print(f"   ✅ Result: {result}")
            for bid in result:
                print(f"      • {get_broker_summary(bid)}")
        else:
            print(f"   ❌ Result: None (validation failed)")


def test_broker_validation():
    """Test broker ID validation"""
    print("\n" + "=" * 70)
    print("TEST 3: Broker Validation")
    print("=" * 70)
    
    test_cases = [
        ([2], True, "Valid single broker"),
        ([2, 3, 6], True, "All valid brokers"),
        ([999], False, "Invalid broker ID"),
        ([2, 999], False, "Mix of valid and invalid"),
        ([], False, "Empty list"),
    ]
    
    for broker_ids, expected_valid, description in test_cases:
        print(f"\n🔍 Test: {description}")
        print(f"   Input: {broker_ids}")
        
        is_valid = validate_broker_ids(broker_ids)
        
        if is_valid == expected_valid:
            print(f"   ✅ Validation result: {is_valid} (as expected)")
        else:
            print(f"   ❌ Validation result: {is_valid} (expected {expected_valid})")
        
        # Also show detailed breakdown
        from src.config.broker_config import validate_broker_ids_detailed
        if broker_ids:
            detailed = validate_broker_ids_detailed(broker_ids)
            print(f"   📊 Detailed: Valid={detailed['valid']}, Disabled={detailed['disabled']}, Unknown={detailed['unknown']}")


def test_confirmation_with_portals():
    """Test confirmation display with portal analysis"""
    print("\n" + "=" * 70)
    print("TEST 4: Broker Confirmation with Portal Analysis")
    print("=" * 70)
    
    # Get active brokers
    active_brokers = get_active_broker_ids()
    
    if not active_brokers:
        print("❌ No active brokers found in configuration")
        return
    
    print(f"\n📋 Testing confirmation for {len(active_brokers)} active broker(s)")
    
    # Fetch portal analysis
    try:
        mapper = PortalMapper()
        portal_analysis = mapper.analyze_portal_distribution(active_brokers)
        
        print("\n🔍 Portal Analysis Results:")
        print(f"   Total unique portals: {portal_analysis['total_unique']}")
        print(f"   Shared portals: {len(portal_analysis['shared'])}")
        print(f"   Broker-specific portals: {len(portal_analysis['unique'])}")
        
        # Display confirmation
        print("\n" + "-" * 70)
        print("Testing confirmation display (enter 'y' to confirm, 'n' to cancel):")
        print("-" * 70 + "\n")
        
        confirmed = confirm_broker_selection(active_brokers, portal_analysis)
        
        if confirmed:
            print("\n✅ User confirmed selection")
        else:
            print("\n❌ User cancelled selection")
            
    except Exception as e:
        print(f"\n❌ Error fetching portal analysis: {e}")
        import traceback
        traceback.print_exc()


def test_active_broker_config():
    """Test active broker configuration"""
    print("\n" + "=" * 70)
    print("TEST 5: Active Broker Configuration")
    print("=" * 70)
    
    active_brokers = get_active_broker_ids()
    
    print(f"\n📋 Found {len(active_brokers)} active broker(s) in configuration:\n")
    
    for bid in active_brokers:
        print(f"   Broker {bid}:")
        print(f"      Name: {get_broker_name(bid)}")
        print(f"      Summary: {get_broker_summary(bid)}")
    
    if not active_brokers:
        print("   ⚠️  No active brokers found!")
        print("   Check src/config/broker_config.py")
    
    # Also show overall summary
    from src.config.broker_config import get_all_brokers_summary
    print(f"\n📊 Overall Summary:")
    print(get_all_brokers_summary())


def main():
    print("=" * 70)
    print("🧪 BROKER SELECTION TESTING SUITE")
    print("=" * 70)
    
    # Test 1: Interactive selection
    print("\n" + "=" * 70)
    print("Would you like to test interactive broker selection? (y/n): ", end="")
    if input().strip().lower() == 'y':
        test_interactive_selection()
    
    # Test 2: CLI selection
    test_cli_selection()
    
    # Test 3: Broker validation
    test_broker_validation()
    
    # Test 4: Confirmation with portals
    print("\n" + "=" * 70)
    print("Would you like to test broker confirmation with portal analysis? (y/n): ", end="")
    if input().strip().lower() == 'y':
        test_confirmation_with_portals()
    
    # Test 5: Active broker config
    test_active_broker_config()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
