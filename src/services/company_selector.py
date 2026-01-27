"""
Company Selection Service
Handles interactive company selection for insurance portal processing.
"""

import json
import os
import asyncio
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from src.services.db_config.db_connect import MySQLDatabase
from src.utils.load_yaml import BROKER_ID

# Fallback mapping for when request data is not available
FALLBACK_COMPANY_MAPPING = {
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
    18: "MaxHealth"
}

def get_companies_from_request():
    """Fetch unique company names from the current pending request's individualDataList."""
    db = None
    try:
        db = MySQLDatabase(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
        if not db.connect():
            print("⚠️ Could not connect to database for company list. Using fallback.")
            return None

        # Get the first pending request
        query = """
        SELECT Req_Data FROM medical_cloud_requests_portal_check
        WHERE broker_id = %s AND status = 'pending'
        ORDER BY Req_Id ASC
        LIMIT 1
        """
        request = db.fetch_one(query, (BROKER_ID,))

        if not request or not request.get('Req_Data'):
            print("⚠️ No pending request found or no Req_Data. Using fallback.")
            return None

        # Parse the request data
        req_data_json = json.loads(request['Req_Data']) if isinstance(request['Req_Data'], str) else request['Req_Data']

        individual_data_list = req_data_json.get('individualDataList', [])
        if not individual_data_list:
            print("⚠️ No individualDataList found in request. Using fallback.")
            return None

        # Extract unique company names
        companies = []
        seen_companies = set()

        for item in individual_data_list:
            company_name = item.get('Company', '').strip()
            if company_name and company_name not in seen_companies:
                companies.append(company_name)
                seen_companies.add(company_name)

        if not companies:
            print("⚠️ No companies found in request data. Using fallback.")
            return None

        # Create numbered mapping
        company_mapping = {i+1: company for i, company in enumerate(companies)}
        return company_mapping

    except Exception as e:
        print(f"⚠️ Error fetching companies from request: {e}. Using fallback.")
        return None
    finally:
        if db and db.is_connected():
            db.disconnect()

def get_company_mapping():
    """Get company mapping from request data or fallback to hardcoded values."""
    mapping = get_companies_from_request()
    if mapping:
        print("✅ Loaded company names from current pending request")
        return mapping
    else:
        print("⚠️ Using fallback company mapping")
        return FALLBACK_COMPANY_MAPPING.copy()

# Mapping between request company names and portal function names
COMPANY_TO_PORTAL_MAPPING = {
    # Request Company Name -> Portal Function Name
    "DUBAI INSURANCE CO": "Dubaiinsurance",
    "MaxHealth": "MaxHealth",
    "Watania Takaful": "Wataniatakaful",
    "TAKAFUL EMARAT": "Takaful",
    "ORIENT INSURANCE PJSC": "Orient",
    "Al Ittihad Al Watani": "Alittihad_Alwatani",
    "ADNIC": "ADNIC",
    "AL SAGR INSURANCE COMPANY": "ALSAGR",
    "GIG Insurance": "GIG",
    "SUKOON INSURANCE": "Sukoon",
    "Dubai National Insurance And Reinsurance Co": "DNI",
    "QATAR INSURANCE CO": "QATAR",
    "ISON": "ISON",
    "NLGIC": "NLG",
    "Fidelity United": "Fidelity",
    "Daman Insurance": "Daman",
    "RAK INSURANCE": "RAK",
    "Medgulf": "Medgulf"
}

def show_company_mapping():
    """Display the company mapping with numbers."""
    global COMPANY_MAPPING
    if COMPANY_MAPPING is None:
        COMPANY_MAPPING = get_company_mapping()

    print("\n🏢 Available Companies for Processing:")
    print("=" * 50)
    for num, company in COMPANY_MAPPING.items():
        print(f"{num:2d}. {company}")
    print("=" * 50)

def get_user_selection():
    """Get user selection for company processing."""
    global COMPANY_MAPPING
    if COMPANY_MAPPING is None:
        COMPANY_MAPPING = get_company_mapping()

    while True:
        print("\nSelect processing mode:")
        print("1. Process ALL companies")
        print("2. Select SPECIFIC companies by number")
        print("3. Load previous selection from config")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            return list(COMPANY_MAPPING.values())  # All companies
        elif choice == "2":
            return get_specific_companies()
        elif choice == "3":
            loaded = load_company_config()
            if loaded:
                print(f"\n✅ Loaded previous selection: {', '.join(loaded)}")
                return loaded
            else:
                print("\n❌ No previous config found. Please select companies manually.")
                continue
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

def get_specific_companies():
    """Get specific company selection from user."""
    global COMPANY_MAPPING
    if COMPANY_MAPPING is None:
        COMPANY_MAPPING = get_company_mapping()

    selected = []
    while True:
        try:
            nums_input = input("\nEnter company numbers (comma-separated, e.g., 1,3,5) or 'all': ").strip().lower()

            if nums_input == "all":
                return list(COMPANY_MAPPING.values())

            nums = [int(x.strip()) for x in nums_input.split(",")]

            # Validate numbers
            invalid_nums = [n for n in nums if n not in COMPANY_MAPPING]
            if invalid_nums:
                print(f"❌ Invalid company numbers: {invalid_nums}")
                print("Please enter valid numbers from the list above.")
                continue

            selected = [COMPANY_MAPPING[n] for n in nums]
            print(f"\n✅ Selected companies: {', '.join(selected)}")

            # Confirm selection
            confirm = input("Confirm selection? (y/n): ").strip().lower()
            if confirm == "y":
                return selected
            else:
                print("Selection cancelled. Try again.")
                continue

        except ValueError:
            print("❌ Invalid input. Please enter numbers separated by commas.")

def create_company_config(selected_companies):
    """Save selected companies to config file."""
    config = {
        "selected_companies": selected_companies,
        "last_updated": str(asyncio.get_event_loop().time()) if asyncio.get_event_loop() else "manual"
    }

    try:
        with open("company_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("💾 Company selection saved to company_config.json")
    except Exception as e:
        print(f"⚠️ Could not save config: {e}")

def load_company_config():
    """Load selected companies from config file."""
    if not os.path.exists("company_config.json"):
        return None

    try:
        with open("company_config.json", "r") as f:
            config = json.load(f)
        return config.get("selected_companies", [])
    except Exception as e:
        print(f"⚠️ Could not load config: {e}")
        return None

def filter_portal_list(portal_list, selected_companies):
    """Filter portal list based on selected companies."""
    if not selected_companies:
        return portal_list  # Return all if no filter

    # Convert selected company names to portal names using the mapping
    selected_portal_names = []
    for company in selected_companies:
        portal_name = COMPANY_TO_PORTAL_MAPPING.get(company, company)  # Fallback to original name if not found
        selected_portal_names.append(portal_name)

    filtered = []
    for portal in portal_list:
        if portal["name"] in selected_portal_names:
            filtered.append(portal)

    return filtered

def get_company_selection():
    """Main function to handle complete company selection process."""
    global COMPANY_MAPPING
    COMPANY_MAPPING = get_company_mapping()  # Initialize with fresh data from request

    show_company_mapping()
    selected_companies = get_user_selection()
    create_company_config(selected_companies)
    return selected_companies