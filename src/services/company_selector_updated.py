"""
Company Selection Service (Standalone)
Handles interactive company selection WITHOUT database dependency.
Use this instead of company_selector.py when you want to run portals
without waiting for pending database requests.

Usage:
    from src.services.company_selector_updated import get_company_selection, filter_portal_list
"""

import json
import os


# All available companies - hardcoded, no database needed
COMPANY_MAPPING = {
    1: "Medgulf",
    2: "TAKAFUL EMARAT",
    3: "ORIENT INSURANCE PJSC",
    4: "Al Ittihad Al Watani",
    5: "ADNIC",
    6: "AL SAGR INSURANCE COMPANY",
    7: "GIG Insurance",
    8: "DUBAI INSURANCE CO",
    9: "SUKOON INSURANCE",
    10: "Dubai National Insurance And Reinsurance Co",
    11: "QATAR INSURANCE CO",
    12: "ISON",
    13: "Watania Takaful",
    14: "NLGIC",
    15: "Fidelity United",
    16: "Daman Insurance",
    17: "RAK INSURANCE",
    18: "MaxHealth",
    19: "Orient Aura"
}

# Mapping between company names and portal function names
COMPANY_TO_FUNCTION_MAPPING = {
    "Medgulf": "Medgulf",
    "TAKAFUL EMARAT": "Takaful",
    "ORIENT INSURANCE PJSC": "Orient",
    "Al Ittihad Al Watani": "Alittihad_Alwatani",
    "ADNIC": "ADNIC",
    "AL SAGR INSURANCE COMPANY": "ALSAGR",
    "GIG Insurance": "GIG",
    "DUBAI INSURANCE CO": "Dubaiinsurance",
    "SUKOON INSURANCE": "Sukoon",
    "Dubai National Insurance And Reinsurance Co": "DNI",
    "QATAR INSURANCE CO": "QATAR",
    "ISON": "ISON",
    "Watania Takaful": "Wataniatakaful",
    "NLGIC": "NLG",
    "Fidelity United": "Fidelity",
    "Daman Insurance": "Daman",
    "RAK INSURANCE": "RAK",
    "MaxHealth": "MaxHealth",
    "Orient Aura": "Orient Aura"
}


def show_company_menu():
    """Display the company selection menu."""
    print("\n" + "=" * 70)
    print("🏢 COMPANY SELECTION - Choose Insurance Company(s) to Run")
    print("=" * 70)
    print(f"{'#':<4} {'Company Name':<45} {'Portal':<15}")
    print("-" * 70)
    for num, company in COMPANY_MAPPING.items():
        portal_name = COMPANY_TO_FUNCTION_MAPPING.get(company, company)
        print(f"{num:<4} {company:<45} {portal_name:<15}")
    print("-" * 70)
    print(f"{'0':<4} {'Exit':<45}")
    print("=" * 70)


def get_user_selection():
    """Get user selection for company processing from command line."""
    while True:
        print("\n📝 How to select:")
        print("   • Single company:    Enter number (e.g., 2)")
        print("   • Multiple companies: Enter comma-separated (e.g., 2,3,5)")
        print("   • All companies:      Enter 'all'")
        print("   • Exit:             Enter '0'")
        
        user_input = input("\n👉 Your selection: ").strip().lower()
        
        # Exit
        if user_input == '0':
            print("\n👋 Exiting...")
            return []
        
        # All companies
        if user_input == 'all':
            selected = list(COMPANY_MAPPING.values())
            print(f"\n✅ Selected ALL {len(selected)} companies")
            if _confirm_selection(selected):
                return selected
            continue
        
        # Specific companies
        try:
            nums = [int(x.strip()) for x in user_input.split(",")]
            
            # Remove duplicates while preserving order
            nums = list(dict.fromkeys(nums))
            
            # Validate numbers
            invalid_nums = [n for n in nums if n not in COMPANY_MAPPING]
            if invalid_nums:
                print(f"\n❌ Invalid number(s): {invalid_nums}")
                print(f"   Valid range: 1-{len(COMPANY_MAPPING)}")
                continue
            
            selected = [COMPANY_MAPPING[n] for n in nums]
            
            if _confirm_selection(selected):
                return selected
            continue
                
        except ValueError:
            print("\n❌ Invalid input. Please enter numbers separated by commas.")
            print("   Example: 2 or 1,3,5 or all")


def _confirm_selection(selected_companies):
    """Show selection summary and ask for confirmation."""
    print(f"\n📋 Selected {len(selected_companies)} company(s):")
    print("-" * 50)
    for i, company in enumerate(selected_companies, 1):
        portal_name = COMPANY_TO_FUNCTION_MAPPING.get(company, company)
        print(f"   {i}. {company} → {portal_name}")
    print("-" * 50)
    
    confirm = input("\n✔️  Confirm selection? (y/n): ").strip().lower()
    if confirm == 'y':
        _save_selection(selected_companies)
        return True
    else:
        print("❌ Selection cancelled. Try again.")
        return False


def _save_selection(selected_companies):
    """Save selected companies to config file for future reference."""
    config = {
        "selected_companies": selected_companies,
        "mode": "standalone"
    }
    try:
        with open("company_selection.json", "w") as f:
            json.dump(config, f, indent=2)
        print("💾 Selection saved to company_selection.json")
    except Exception as e:
        print(f"⚠️ Could not save selection: {e}")


def load_previous_selection():
    """Load previously saved selection."""
    if not os.path.exists("company_selection.json"):
        return None
    try:
        with open("company_selection.json", "r") as f:
            config = json.load(f)
        return config.get("selected_companies", [])
    except Exception as e:
        print(f"⚠️ Could not load previous selection: {e}")
        return None


def filter_portal_list(portal_list, selected_companies):
    """
    Filter portal list based on selected companies.
    PRESERVES the order in which user selected the companies.
    
    Args:
        portal_list: List of dicts with 'function' and 'name' keys
        selected_companies: List of company names selected by user
    
    Returns:
        Filtered list of portal dicts in user's selection order
    """
    if not selected_companies:
        return portal_list
    
    # Convert company names to portal function names (preserving order)
    selected_portal_names = []
    for company in selected_companies:
        portal_name = COMPANY_TO_FUNCTION_MAPPING.get(company, company)
        selected_portal_names.append(portal_name)
    
    # Create a lookup dict for quick portal access
    portal_lookup = {p["name"]: p for p in portal_list}
    
    # Build filtered list IN THE ORDER user selected (not portal_list order)
    filtered = []
    for portal_name in selected_portal_names:
        if portal_name in portal_lookup:
            filtered.append(portal_lookup[portal_name])
    
    return filtered


def get_company_selection():
    """
    Main function - shows menu and returns selected companies.
    No database connection needed.
    
    Returns:
        List of selected company names
    """
    # Check for previous selection
    previous = load_previous_selection()
    if previous:
        print(f"\n📁 Found previous selection: {', '.join(previous)}")
        use_previous = input("   Use previous selection? (y/n): ").strip().lower()
        if use_previous == 'y':
            print(f"\n✅ Using previous selection: {len(previous)} company(s)")
            return previous
    
    # Show menu and get new selection
    show_company_menu()
    selected_companies = get_user_selection()
    return selected_companies


# Allow running this file directly for testing
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 COMPANY SELECTOR MODE")
    print("=" * 70)
    
    selected = get_company_selection()
    
    if selected:
        print(f"\n🎯 Final selection: {selected}")
        print(f"   Portal names: {[COMPANY_TO_FUNCTION_MAPPING.get(c, c) for c in selected]}")
    else:
        print("\n❌ No companies selected")
