"""
Al Sagr API Configuration and Mapping

Contains hardcoded Al Sagr API endpoints and benefit field mappings.
Al Sagr uses JWT Bearer token authentication for API calls.

Key Finding:
- Benefits are IDENTICAL across categories for the same plan
- Only ONE API call per plan is needed (not per plan+category combination)
- benefitId is the key for mapping response values to table rows
"""

# ============================================================================
# PORTAL CONSTANTS
# ============================================================================

PORTAL_NAME = "AL SAGR INSURANCE COMPANY"
PORTAL_REGION = "Dubai"

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_BASE_URL = "https://ndapi.alsagrins.ae/MiCore/api/GroupQuotation"

# Login URL (Selenium login)
LOGIN_URL = "https://sso.alsagrins.ae/login"

# Portal URL (after login, navigate here to get quotation)
PORTAL_URL = "https://miportal.alsagrins.ae"

# ============================================================================
# API ENDPOINTS
# ============================================================================

ENDPOINTS = {
    # Pre-Level: Get TPA options
    # Parameters: productTypeId (e.g., 183 for SME)
    "tpa_masters": "/GetTPAMastersByProductType",
    
    # Gets quotation metadata
    "quote_information": "/GetQuoteInformation",
    
    # Gets benefit structure: planBenefits[], category[], benefitLayout[], benefitStructure[], proposalMasters[]
    "benefit_structure": "/GetGroupQuotationBenefitStructure",
    
    # Gets benefit values for a specific plan
    # Parameters: planId, categoryId, quotationId, proposalId
    "benefits_by_plan": "/GetBenefitsByPlan",
}

# ============================================================================
# BENEFIT FIELD MAPPING
# ============================================================================

# Maps benefitId to display name (extracted from API response)
# This mapping is based on the benefitStructure[].benefitId values
# Display names MUST match FIELD_MAPPING[*][1] for proper database mapping
BENEFIT_FIELD_MAPPING = {
    8: "Visa Region",
    9: "Network",             # Portal's Network field (RN, GN, GN+) → maps to Plan_Selection dropdown
    10: "OP Co-Insurance",
    11: "Phar.Co-Ins",        # Pharmacy Co-Insurance
    12: "Aggregate Limit",
    13: "Geographical Area",
    14: "Consult.Ded",        # Consult Deductible
    15: "Maternity Limit",
    16: "Nursing Home",
    17: "Repatriation",
    18: "Psychiatric",
    57: "Dental",
    58: "Optical",
    59: "Alternative",        # Alternative Medicine
    125: "Pharmacy Limit",
    126: "IP- Room & Board",  # IP Room & Board with hyphen
    165: "Plan Type",
}

# Reverse mapping: name to benefitId
BENEFIT_NAME_TO_ID = {v: k for k, v in BENEFIT_FIELD_MAPPING.items()}

# ============================================================================
# CATEGORY MAPPING
# ============================================================================

# Known category IDs from Al Sagr portal
CATEGORY_MAPPING = {
    2: "Category B",
    47: "Category B1",
    # Add more categories as discovered
}

# ============================================================================
# DEFAULT HEADERS
# ============================================================================

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Content-Type": "application/json",
    "Origin": "https://miportal.alsagrins.ae",
    "Referer": "https://miportal.alsagrins.ae/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
}

# ============================================================================
# EXTRACTION CONFIGURATION
# ============================================================================

# Product Type IDs
PRODUCT_TYPE_SME = 183  # SME/Group product type

# Default categoryId to use for GetBenefitsByPlan since benefits are identical across categories
DEFAULT_CATEGORY_ID = 2

# Fields to extract from benefit structure response
PLAN_BENEFITS_FIELDS = [
    "planId",
    "planName", 
    "categoryId",
    "categoryName",
]

# Fields from proposalMasters
PROPOSAL_FIELDS = [
    "proposalId",
    "proposalName",
]

# ============================================================================
# DATABASE FIELD MAPPING
# Maps API field names to Database Dropdown_Name and Portal Field display names
# Format: api_field: (Dropdown_Name, Portal_Field_Name, MapID)
# ============================================================================

FIELD_MAPPING = {
    # TPA dropdown (pre-level)
    "tpa": ("TPA", "TPA", 1),
    
    # Visa Region - FILTER: Only 'Dubai' plans are extracted
    "visaRegion": ("Region", "Visa Region", 2),
    
    # Plan_Selection dropdown - Portal's "Network" field (RN, GN, GN+)
    "network": ("Plan_Selection", "Network", 63),
    
    # Network dropdown - Portal's "Plan" field (plan names like ASNIC-2-02-12-5)
    "plan": ("Network", "Plan", 3),
    
    # Benefit fields
    "aggregateLimit": ("Annual", "Aggregate Limit", 4),
    "geographicalArea": ("Terotory", "Geographical Area", 5),
    "nursingHome": ("HomeNursing", "Nursing Home", 6),
    "ipRoomBoard": ("RoomCategory", "IP- Room & Board", 67),
    "opCoInsurance": ("DiagnosticCopay", "OP Co-Insurance", 41),
    "pharCoIns": ("Phamacy", "Phar.Co-Ins", 12),
    "maternityLimit": ("Metanity", "Maternity Limit", 15),
    "repatriation": ("Motal", "Repatriation", 27),
    "dental": ("Dental", "Dental", 20),
    "optical": ("Optical", "Optical", 22),
    "alternative": ("Alternativemedecine", "Alternative", 24),
    "psychiatric": ("Psycharaty", "Psychiatric", 26),
    "consultDed": ("Deductable", "Consult.Ded", 8),
    "pharmacyLimit": ("ofpahamacy", "Pharmacy Limit", 11),
}

# Reverse mapping: Dropdown_Name to API field
DROPDOWN_TO_API_FIELD = {v[0]: k for k, v in FIELD_MAPPING.items()}

# MapID to Dropdown_Name
MAPID_TO_DROPDOWN = {v[2]: v[0] for k, v in FIELD_MAPPING.items()}

# ============================================================================
# TPA FILTER CONFIGURATION
# ============================================================================

# Only use this TPA (NEXT CARE MANAGEMENT LLC)
SELECTED_TPA_ID = 1
SELECTED_TPA_NAME = "NEXT CARE MANAGEMENT LLC"

# ============================================================================
# VISA REGION FILTER
# ============================================================================

# Only extract plans with this Visa Region
REQUIRED_VISA_REGION = "Dubai"

# ============================================================================
# BROKER CONFIGURATION
# ============================================================================

BROKER_ID = 3
COMPANY_NAME = "AL SAGR INSURANCE COMPANY"
