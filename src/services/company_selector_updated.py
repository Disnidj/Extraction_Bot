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
    19: "Orient Aura",
    20: "Liva Globalcare",
    21: "QIC HealthX Exclusive"
}

# Mapping between company names and portal function names
COMPANY_TO_FUNCTION_MAPPING = {
    "Medgulf": "Medgulf",
    "TAKAFUL EMARAT": "Takaful",
    "ORIENT INSURANCE PJSC": "Orient",
    "Al Ittihad Al Watani": "Alittihad_Alwatani",
    "ADNIC": "ADNIC",
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
    "Orient Aura": "Orient Aura",
    "Liva Globalcare": "NLGI Aura",
    "QIC HealthX Exclusive": "QIC HealthX Exclusive",
    "AL SAGR INSURANCE COMPANY": "AL SAGR"

}


# Reverse mapping: portal function name → proper company display name
# Shows both friendly name and technical name for clarity
FUNCTION_TO_COMPANY_MAPPING = {
    "ADNIC": "ADNIC",
    "Takaful": "TAKAFUL EMARAT (Takaful)",
    "QATAR": "QATAR INSURANCE CO (QATAR)",
    "MaxHealth": "MaxHealth",
    "Sukoon": "SUKOON INSURANCE (Sukoon)",
    "Orient Aura": "Orient Aura",
    "NLGI Aura": "Liva Globalcare (NLGI Aura)",
    "AL SAGR": "AL SAGR INSURANCE COMPANY (AL SAGR)",
    "QIC HealthX Exclusive": "QIC HealthX Exclusive",
    # Legacy mappings for standard extraction
    "Medgulf": "Medgulf",
    "Orient": "ORIENT INSURANCE PJSC",
    "Alittihad_Alwatani": "Al Ittihad Al Watani",
    "GIG": "GIG Insurance",
    "Dubaiinsurance": "DUBAI INSURANCE CO",
    "DNI": "Dubai National Insurance And Reinsurance Co",
    "ISON": "ISON",
    "Wataniatakaful": "Watania Takaful",
    "NLG": "NLGIC",
    "Fidelity": "Fidelity United",
    "Daman": "Daman Insurance",
    "RAK": "RAK INSURANCE"
}


# Companies that have API extraction implemented
API_ENABLED_COMPANIES = [
    "ADNIC",                    # #5
    "TAKAFUL EMARAT (Takaful)",           # #2
    "QATAR INSURANCE CO (QATAR)",       # #11
    "MaxHealth",                # #18
    "SUKOON INSURANCE (Sukoon)",         # #9
    "Orient Aura",              # #19
    "Liva Globalcare (NLGI Aura)",          # #20 (NLGI Aura)
    "AL SAGR INSURANCE COMPANY (AL SAGR)", # #6
    "QIC HealthX Exclusive"     # #21
]


def get_filtered_company_mapping(mode='standard', available_api_companies=None):
    """
    Get company mapping filtered by extraction mode.
    
    Args:
        mode: 'standard' shows all companies, 'api' shows only API-enabled companies
        available_api_companies: dynamic list of company names available for API mode.
                                 If None, falls back to the hardcoded API_ENABLED_COMPANIES.
    
    Returns:
        Filtered COMPANY_MAPPING dict
    """
    if mode == 'api':
        filter_list = available_api_companies if available_api_companies is not None else API_ENABLED_COMPANIES
        return {k: v for k, v in COMPANY_MAPPING.items() if v in filter_list}
    return COMPANY_MAPPING


def show_company_menu(mode='standard', available_api_companies=None):
    """
    Display the company selection menu.
    
    Args:
        mode: 'standard' or 'api' to filter available companies
        available_api_companies: dynamic list of available company names for API mode
    """
    filtered_mapping = get_filtered_company_mapping(mode, available_api_companies)
    
    # Renumber filtered companies sequentially starting from 1
    renumbered_mapping = {i: company for i, company in enumerate(filtered_mapping.values(), start=1)}
    
    mode_label = "API Extraction" if mode == 'api' else "Standard Extraction"
    print("\n" + "=" * 70)
    print(f"🏢 COMPANY SELECTION - {mode_label} Mode")
    print("=" * 70)
    print(f"{'#':<4} {'Company Name':<45} {'Portal':<15}")
    print("-" * 70)
    for num, company in renumbered_mapping.items():
        portal_name = COMPANY_TO_FUNCTION_MAPPING.get(company, company)
        print(f"{num:<4} {company:<45} {portal_name:<15}")
    print("-" * 70)
    print(f"{'0':<4} {'Exit':<45}")
    print("=" * 70)
    
    if mode == 'api':
        print(f"\n💡 Showing {len(renumbered_mapping)} companies with API extraction available")


def get_user_selection(mode='standard', available_api_companies=None):
    """
    Get user selection for company processing from command line.
    
    Args:
        mode: 'standard' or 'api' to filter available companies
        available_api_companies: dynamic list of available company names for API mode
    """
    filtered_mapping = get_filtered_company_mapping(mode, available_api_companies)
    
    # Renumber filtered companies sequentially starting from 1
    renumbered_mapping = {i: company for i, company in enumerate(filtered_mapping.values(), start=1)}
    
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
            selected = list(renumbered_mapping.values())
            print(f"\n✅ Selected ALL {len(selected)} companies")
            if _confirm_selection(selected):
                return selected
            continue
        
        # Specific companies
        try:
            nums = [int(x.strip()) for x in user_input.split(",")]
            
            # Remove duplicates while preserving order
            nums = list(dict.fromkeys(nums))
            
            # Validate numbers against renumbered mapping
            invalid_nums = [n for n in nums if n not in renumbered_mapping]
            if invalid_nums:
                print(f"\n❌ Invalid number(s): {invalid_nums}")
                valid_nums = sorted(renumbered_mapping.keys())
                print(f"   Valid options: {', '.join(map(str, valid_nums))}")
                continue
            
            selected = [renumbered_mapping[n] for n in nums]
            
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


def get_company_selection(mode='standard', available_api_companies=None):
    """
    Main function - shows menu and returns selected companies.
    No database connection needed.
    
    Args:
        mode: 'standard' for all companies, 'api' for API-enabled only
        available_api_companies: dynamic list of company names available for API mode.
                                 Passed from main.py based on active API_PORTAL_GROUPS.
    
    Returns:
        List of selected company names
    """
    # Check for previous selection
    previous = load_previous_selection()
    if previous:
        # Validate previous selection against current mode
        filtered_mapping = get_filtered_company_mapping(mode, available_api_companies)
        valid_previous = [c for c in previous if c in filtered_mapping.values()]
        
        if valid_previous:
            print(f"\n📁 Found previous selection: {', '.join(valid_previous)}")
            if len(valid_previous) < len(previous):
                removed = [c for c in previous if c not in valid_previous]
                print(f"   ⚠️  Filtered out (not available in {mode} mode): {', '.join(removed)}")
            
            use_previous = input("   Use previous selection? (y/n): ").strip().lower()
            if use_previous == 'y':
                print(f"\n✅ Using previous selection: {len(valid_previous)} company(s)")
                return valid_previous
    
    # Show menu and get new selection
    show_company_menu(mode, available_api_companies)
    selected_companies = get_user_selection(mode, available_api_companies)
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
