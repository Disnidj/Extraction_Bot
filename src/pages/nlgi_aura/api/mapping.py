"""
NLGI Aura Portal Mapping Configuration
Updated to follow Orient Aura/Qatar pattern with dynamic API calls.

Group: GlobalCare SME (ID: 119)
Region: Dubai only
"""

# ============================================================================
# PORTAL CONSTANTS
# ============================================================================

PORTAL_NAME = "NLGI AURA"
PORTAL_REGION = "Dubai"  # Default region for all records
GROUP_NAME = "GlobalCare SME"  # Hardcoded group name

# ============================================================================
# HARDCODED MAPPING - NLGI Aura Configuration (matching Orient/Qatar pattern)
# ============================================================================

NLGI_MAPPING = {
    "portal_name": "NLGI AURA",
    "version_id": 36,  # Used to call group API
    
    # Group configuration - only group_name is hardcoded
    # group_id will be fetched from API by matching group_name
    "group": {
        "group_name": "GlobalCare SME"  # Target group to find in API response
    }
}

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_BASE_URL = "https://smehealth-api.aurainsure.tech"
PORTAL_BASE_URL = "https://smehealth.aurainsure.tech"

# API Endpoints (same pattern as Orient Aura/Qatar)
ENDPOINTS = {
    "industry": "/quotes/generate/industry",
    "group": "/quotes/generate/group/{version_id}",  # Group endpoint
    "emirates": "/quotes/generate/emirates",
    "tpa": "/quotes/generate/tpa",
    "plan": "/quotes/generate/plan",
    "benefits": "/quotes/generate/benefits"
}

# Additional headers required for NLGI
CUSTOM_HEADERS = {
    "insurerurl": "nlgi",
    "reinsurername": "nlgi-ri",
    "client_code": "null"
}
