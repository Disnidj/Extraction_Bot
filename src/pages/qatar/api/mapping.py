"""
Qatar Insurance Portal Mapping Configuration
Updated to follow Orient Aura pattern with dynamic API calls.

Group: SME NAS (ID: 281)
Region: Dubai only
TPA: NAS
"""

# ============================================================================
# PORTAL CONSTANTS
# ============================================================================

PORTAL_NAME = "QATAR INSURANCE CO"
PORTAL_REGION = "Dubai"  # Default region for all records
GROUP_NAME = "SME NAS"  # Hardcoded group name

# ============================================================================
# HARDCODED MAPPING - Qatar SME NAS Configuration
# ============================================================================

QATAR_MAPPING = {
    "portal_name": "QATAR INSURANCE CO",
    "version_id": 50,  # Used to call group API
    
    # Group configuration - only group_name is hardcoded
    # group_id will be fetched from API by matching group_name
    "group": {
        "group_name": "SME NAS"  # Target group to find in API response
    }
}

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_BASE_URL = "https://smehealth-api.aurainsure.tech"
PORTAL_BASE_URL = "https://smehealth.aurainsure.tech"

# API Endpoints (same pattern as Orient Aura)
ENDPOINTS = {
    "industry": "/quotes/generate/industry",
    "group": "/quotes/generate/group/{version_id}",  # Group endpoint
    "emirates": "/quotes/generate/emirates",
    "tpa": "/quotes/generate/tpa",
    "plan": "/quotes/generate/plan",
    "benefits": "/quotes/generate/benefits"
}

# Additional headers required for Qatar (qic insurer)
CUSTOM_HEADERS = {
    "insurerurl": "qic",
    "reinsurername": "icici",
    "client_code": "null"
}
