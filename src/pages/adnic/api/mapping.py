"""
ADNIC API Configuration and Mapping

Contains hardcoded ADNIC API endpoints and configuration.
Similar to Takaful's mapping.py for TPA/emirate configuration.
"""

# Base URL for ADNIC AJAX services
ADNIC_API_BASE_URL = "https://www.adnicinsure.com/Eng/Services/INeedAjaxServices.asmx"

# Portal information
PORTAL_NAME = "ADNIC"
PORTAL_REGION = "UAE"

# =====================================================
# Level 0: Independent APIs (no dependencies)
# =====================================================
INDEPENDENT_APIS = [
    {
        "endpoint": "GetTPAByProduct",
        "category": "TPA",
        "display_name": "TPA (Network provider)",
        "description": "Third Party Administrators - ADNIC, NextCare, Nas"
    },
    {
        "endpoint": "GetAnnualLimit",
        "category": "ALimit",
        "display_name": "Annual Limit",
        "description": "Annual benefit limit options"
    },
    {
        "endpoint": "GetDeductible",
        "category": "Deductible",
        "display_name": "Deductible",
        "description": "Deductible amount options"
    },
    {
        "endpoint": "GetCoPay",
        "category": "Copay",
        "display_name": "Co-Payment on Outpatient Drugs",
        "description": "Co-payment percentage for drugs"
    },
    {
        "endpoint": "GetCopaymentdiagnostics",
        "category": "copayDig",
        "display_name": "Co-payment on Diagnostics",
        "description": "Co-payment percentage for diagnostics"
    },
    {
        "endpoint": "GetMaternity",
        "category": "Maternity",
        "display_name": "Maternity - Married Females",
        "description": "Maternity coverage options"
    },
    {
        "endpoint": "GetAlternativeMedicine",
        "category": "Alternative",
        "display_name": "Alternative Medicine",
        "description": "Alternative medicine coverage"
    },
    {
        "endpoint": "GetPsychiatry",
        "category": "psychiatry",
        "display_name": "Psychiatry",
        "description": "Psychiatry coverage options"
    },
]

# =====================================================
# Level 1: TPA-dependent APIs
# =====================================================
TPA_DEPENDENT_APIS = [
    {
        "endpoint": "GetNetworkTPA",
        "category": "Plan",
        "display_name": "Network Type",
        "description": "Network plans available for the TPA",
        "depends_on": ["TPA"]
    },
]

# =====================================================
# Level 2: TPA + Network dependent APIs
# =====================================================
NETWORK_DEPENDENT_APIS = [
    {
        "endpoint": "GetTerritorialCover",
        "category": "TCover",
        "display_name": "Territorial Cover - Elective",
        "description": "Geographical coverage for elective treatments",
        "depends_on": ["TPA", "Plan"]
    },
    {
        "endpoint": "GetPharmacylimit",
        "category": "PHlim",
        "display_name": "Pharmacy Limit",
        "description": "Pharmacy benefit limits",
        "depends_on": ["TPA", "Plan"]
    },
    {
        "endpoint": "GetDental",
        "category": "Dental",
        "display_name": "Dental",
        "description": "Dental coverage options",
        "depends_on": ["TPA", "Plan"]
    },
    {
        "endpoint": "GetOptical",
        "category": "Optical",
        "display_name": "Optical",
        "description": "Optical/vision coverage options",
        "depends_on": ["TPA", "Plan"]
    },
]

# =====================================================
# Level 3: TPA + Network + TCover dependent APIs
# =====================================================
TCOVER_DEPENDENT_APIS = [
    {
        "endpoint": "GetTerritorialCoverEmergency",
        "category": "TCoverEM",
        "display_name": "Territorial Cover - Emergency",
        "description": "Geographical coverage for emergency treatments",
        "depends_on": ["TPA", "Plan", "TCover"]
    },
]

# =====================================================
# Full API Configuration
# =====================================================
ADNIC_API_CONFIG = {
    "base_url": ADNIC_API_BASE_URL,
    "portal_name": PORTAL_NAME,
    "portal_region": PORTAL_REGION,
    "apis": {
        "level_0": INDEPENDENT_APIS,
        "level_1": TPA_DEPENDENT_APIS,
        "level_2": NETWORK_DEPENDENT_APIS,
        "level_3": TCOVER_DEPENDENT_APIS,
    }
}

# =====================================================
# Default Headers for API Calls
# =====================================================
DEFAULT_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.adnicinsure.com",
    "Referer": "https://www.adnicinsure.com/Eng/ProductDetails.aspx",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
