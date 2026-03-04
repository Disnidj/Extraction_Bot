"""
Broker selection and management service.
Handles interactive broker selection menus and broker validation.
"""

from typing import List, Optional
from src.config.broker_config import (
    get_enabled_brokers,
    get_active_broker_ids,
    get_broker_name,
    validate_broker_ids,
    get_broker_summary
)


class BrokerSelectionMenu:
    """Interactive broker selection menu."""
    
    def __init__(self):
        self.enabled_brokers = get_enabled_brokers()
    
    def display_menu(self) -> None:
        """Display broker selection menu."""
        print("\n" + "=" * 70)
        print("📋 SELECT BROKERS FOR API EXTRACTION")
        print("=" * 70)
        
        if not self.enabled_brokers:
            print("❌ No active brokers configured!")
            print("   Please enable at least one broker in src/config/broker_config.py")
            print("=" * 70)
            return
        
        print("Available Brokers:")
        for broker in self.enabled_brokers:
            print(f"   Broker {broker['broker_id']} - {broker['name']}")
        
        print("-" * 70)
        print("0. Exit")
        print("all. Select ALL Active Brokers")
        print("=" * 70)
    
    def get_user_selection(self) -> Optional[List[int]]:
        """
        Get broker selection from user input (broker IDs only).
        
        Returns:
            List of selected broker IDs, or None if user exits
        """
        while True:
            self.display_menu()
            
            if not self.enabled_brokers:
                return None
            
            user_input = input("\nEnter broker IDs (comma-separated) or 'all': ").strip()
            
            # Handle exit
            if user_input == '0':
                print("\n👋 Exiting...")
                return None
            
            # Handle 'all' selection
            if user_input.lower() == 'all':
                selected_ids = get_active_broker_ids()
                self._display_selection(selected_ids)
                return selected_ids
            
            # Parse comma-separated broker IDs
            try:
                broker_ids = [int(i.strip()) for i in user_input.split(',')]
            except ValueError:
                print("❌ Invalid input. Please enter broker IDs (e.g., '3' or '2,6'), 'all', or '0' to exit.")
                continue
            
            # Get all active broker IDs for validation
            active_broker_ids = get_active_broker_ids()
            
            # Validate that all entered IDs are active
            invalid_ids = [bid for bid in broker_ids if bid not in active_broker_ids]
            
            if invalid_ids:
                print(f"❌ Invalid or inactive broker IDs: {invalid_ids}")
                print(f"   Valid broker IDs: {', '.join(map(str, active_broker_ids))}")
                continue
            
            # Remove duplicates while preserving order
            seen = set()
            selected_ids = [x for x in broker_ids if not (x in seen or seen.add(x))]
            
            self._display_selection(selected_ids)
            return selected_ids
    
    def _display_selection(self, broker_ids: List[int]) -> None:
        """Display selected brokers."""
        print(f"\n✅ Selected {len(broker_ids)} broker(s):")
        for broker_id in broker_ids:
            print(f"   • Broker {broker_id} - {get_broker_name(broker_id)}")


def select_brokers_interactive() -> Optional[List[int]]:
    """
    Interactive broker selection.
    
    Returns:
        List of selected broker IDs, or None if user exits
    """
    menu = BrokerSelectionMenu()
    return menu.get_user_selection()


def select_brokers_from_cli(broker_arg: str) -> Optional[List[int]]:
    """
    Parse broker selection from CLI argument.
    
    Args:
        broker_arg: Broker argument from command line ('all', '3', '3,6', etc.)
        
    Returns:
        List of validated broker IDs, or None if invalid
    """
    if broker_arg.lower() == 'all':
        return get_active_broker_ids()
    
    try:
        broker_ids = [int(b.strip()) for b in broker_arg.split(',')]
    except ValueError:
        print(f"❌ Invalid broker specification: {broker_arg}")
        return None
    
    # Get active broker IDs
    active_broker_ids = get_active_broker_ids()
    
    # Check if all broker IDs are valid and active
    invalid_ids = [bid for bid in broker_ids if bid not in active_broker_ids]
    
    if invalid_ids:
        print(f"❌ Invalid or inactive broker IDs: {invalid_ids}")
        print(f"   Valid active broker IDs: {', '.join(map(str, active_broker_ids))}")
        return None
    
    # Remove duplicates while preserving order
    seen = set()
    broker_ids = [x for x in broker_ids if not (x in seen or seen.add(x))]
    
    return broker_ids


def confirm_broker_selection(broker_ids: List[int], portal_summary: dict) -> bool:
    """
    Display confirmation prompt with broker and portal details.
    
    Args:
        broker_ids: Selected broker IDs
        portal_summary: Dict with portal counts and names
        
    Returns:
        True if user confirms, False otherwise
    """
    print("\n" + "=" * 70)
    print("📋 EXTRACTION PLAN SUMMARY")
    print("=" * 70)
    print(f"Selected Brokers: {len(broker_ids)}")
    for broker_id in broker_ids:
        print(f"  • Broker {broker_id} - {get_broker_name(broker_id)}")
    
    print(f"\nTotal Unique Portals: {portal_summary['total_unique']}")
    
    if portal_summary.get('shared'):
        print(f"Shared Portals: {len(portal_summary['shared'])}")
        for portal_name, broker_list in portal_summary['shared'].items():
            broker_names = [f"Broker {bid}" for bid in broker_list]
            print(f"  • {portal_name} → {', '.join(broker_names)}")
    
    if portal_summary.get('unique'):
        print(f"\nBroker-Specific Portals: {len(portal_summary['unique'])}")
        for portal_name, broker_id in portal_summary['unique'].items():
            print(f"  • {portal_name} → Broker {broker_id} - {get_broker_name(broker_id)}")
    
    print("=" * 70)
    
    if portal_summary.get('shared'):
        print("\n⚠️  Shared portals will be extracted ONCE and applied to all relevant brokers.")
    
    print("=" * 70)
    
    response = input("\nPress Enter to continue or 'q' to quit: ").strip().lower()
    return response != 'q'
