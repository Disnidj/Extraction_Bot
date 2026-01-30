"""
Sukoon API Configuration and Mapping

Sukoon uses a "Mega API" pattern - one endpoint returns all dropdown options
based on the indemnityId (master switch).

Unlike ADNIC (14 separate APIs), Sukoon's PopulateDDL returns everything in one call.
"""

# Portal information
PORTAL_NAME = "SUKOON INSURANCE"
PORTAL_REGION = "UAE"

# The single master API endpoint
SUKOON_API_URL = "https://smeonline.sukoon.com/GenerateQuotes.aspx/PopulateDDL"

# Regions to extract (can be expanded)
REGIONS = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "RAK", "Fujairah", "UAQ"]

# Product types
PRODUCTS = [
    {"id": 1, "name": "SME Health"},
]

# Response field mappings
# Maps API response keys to UI dropdown names
RESPONSE_FIELD_MAPPING = {
    "ProductIndemnity": {
        "display_name": "Indemnity Limit",
        "description": "Annual insurance limit options",
        "is_master": True  # This is the master switch
    },
    "IndemnityGeographical": {
        "display_name": "Geographical Area",
        "description": "Territory/region coverage options"
    },
    "IndemnityNetwork": {
        "display_name": "Applicable Network",
        "description": "Network plan options (Premium, Edge, Advance, etc.)"
    },
    "IndemnityDeductible": {
        "display_name": "Deductible (OP)",
        "description": "Per-visit deductible options (Nil, 30, 50, 100)"
    },
    "IndemnityCoinsurance": {
        "display_name": "Co-Insurance",
        "description": "Member contribution percentage options"
    },
    "IndemnityLabXRay": {
        "display_name": "Lab & X-Ray Co-Payment",
        "description": "Diagnostics co-pay options (Nil, 10%, 20%)"
    },
    "IndemnityNetworkEP": {
        "display_name": "Enhanced Plan Network",
        "description": "Network options for enhanced plan"
    },
    "IndemnityCoinsuranceEP": {
        "display_name": "Enhanced Plan Co-Insurance",
        "description": "Co-insurance for enhanced plan"
    },
}

# Default headers for API calls
DEFAULT_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://smeonline.sukoon.com",
    "Referer": "https://smeonline.sukoon.com/GenerateQuotes.aspx"
}
