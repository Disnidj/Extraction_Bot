"""
QIC HealthX Exclusive Portal Mapping Configuration
API-based extraction with Dubai-only filtering.

Key Details:
- Portal: QIC HealthX Exclusive (wellx.ai)
- Region: Dubai only (filter from API response)
- TPA: NAS (NAS Network)
- Network: Plan names from API (GN, CN, RN, WN, SRN variants)
- Product ID: df4ae7bd-0e27-4901-9574-54aea6194675
"""

# ============================================================================
# PORTAL CONSTANTS
# ============================================================================

PORTAL_NAME = "QIC HealthX Exclusive"
PORTAL_REGION = "Dubai"  # Filter to Dubai only
TPA_NAME = "NAS"  # NAS Network as TPA

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_BASE_URL = "https://api-hqt.wellx.ai"
PORTAL_BASE_URL = "https://app-hqt.wellx.ai"

# Product ID for QIC HealthX Exclusive
PRODUCT_ID = "df4ae7bd-0e27-4901-9574-54aea6194675"

# API Endpoints
ENDPOINTS = {
    "plans": "/api/v1/plans",
    "quotes": "/api/v1/quotes"
}

# Default query params for plans API
DEFAULT_PLANS_PARAMS = {
    "page": 1,
    "page_size": 100,
    "by_product_id": PRODUCT_ID,
    "by_status": "published"
}

# ============================================================================
# FIELD MAPPING - Uses API 'name' field directly (not codes)
# ============================================================================

# Nested benefits - these have separate limit in 'data' and copay in 'options'
# Key = API benefit name, Value = config for limit/copay field names
NESTED_BENEFITS = {
    "Maternity": {
        "limit_name": "Maternity Limit",
        "copay_name": "Maternity copay"
    },
    "Dental": {
        "limit_name": "Dental Limit",
        "copay_name": "Dental copay"
    },
    "Optical": {
        "limit_name": "Optical Limit",
        "copay_name": "Optical copay"
    },
    "Outpatient Psychiatric": {
        "limit_name": "Outpatient Psychiatric Limit",
        "copay_name": "Outpatient Psychiatric copay"
    },
    "Alternative Medicine": {
        "limit_name": "Alternative Medicine Limit",
        "copay_name": "Alternative Medicine copay"
    },
    "Physiotherapy": {
        "limit_name": "Physiotherapy Limit",
        "copay_name": "Physiotherapy copay"
    }
}

# Simple benefits - API 'name' field is used directly
# No mapping needed! API returns names like:
# - "Annual Policy Limit"
# - "Inpatient Room Type"
# - "Outpatient Co-insurance for Diagnostics"
# etc.

# ============================================================================
# DUBAI FILTER - Plan names containing "Dubai"
# ============================================================================

# Filter plans to only include Dubai ones
# API returns plans like: "GN Dubai", "CN Dubai", "RN Dubai", etc.
DUBAI_FILTER_KEYWORD = "Dubai"

# ============================================================================
# NETWORK MAPPING - Extract network prefix from plan name
# ============================================================================

# Network codes from plan names (e.g., "GN Dubai" -> "GN")
NETWORK_PREFIXES = {
    "GN": "GN (General Network)",
    "CN": "CN (Contract Network)",
    "RN": "RN (Regular Network)",
    "WN": "WN (Wide Network)",
    "SRN": "SRN (Single Room Network)"
}

# ============================================================================
# REQUIRED FIELDS - All 23 fields that must be extracted
# ============================================================================

REQUIRED_FIELDS = [
    # From Simple Benefits (11)
    "Annual Policy Limit",
    "Inpatient Room Type",
    "Inpatient Co-insurance",
    "Deductible for Consultation",
    "Area of Cover",
    "Outpatient Co-insurance for Diagnostics",
    "Pharmacy Co-insurance",
    "Pharmacy Limit",
    "Pre-existing Conditions Limit",
    "Enhanced Coverage (RTA,Transplant,Dialysis,Congenital)",
    "Routine Health Check-up",
    # From Nested Benefits - Limits (6)
    "Maternity Limit",
    "Dental Limit",
    "Optical Limit",
    "Outpatient Psychiatric Limit",
    "Alternative Medicine Limit",
    "Physiotherapy Limit",
    # From Nested Benefits - Copays (6)
    "Maternity copay",
    "Dental copay",
    "Optical copay",
    "Outpatient Psychiatric copay",
    "Alternative Medicine copay",
    "Physiotherapy copay"
]
