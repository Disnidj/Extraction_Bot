"""
Takaful Portal Mapping Configuration
Updated to follow Orient Aura/Qatar pattern with dynamic API calls.

Group: SME Medical (ID: 32)
Version ID: 28
Region: Dubai only
"""

# ============================================================================
# PORTAL CONSTANTS
# ============================================================================

PORTAL_NAME = "TAKAFUL EMARAT"
PORTAL_REGION = "Dubai"  # Default region for all records
GROUP_NAME = "SME Medical"  # Hardcoded group name

# ============================================================================
# HARDCODED MAPPING - Takaful SME Medical Configuration
# ============================================================================

TAKAFUL_MAPPING = {
    "portal_name": "TAKAFUL EMARAT",
    "version_id": 28,  # Used to call group API
    
    # Group configuration - only group_name is hardcoded
    # group_id will be fetched from API by matching group_name
    "group": {
        "group_name": "SME Medical"  # Target group to find in API response
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

# Additional headers required for Takaful (takafulemarat insurer)
CUSTOM_HEADERS = {
    "insurerurl": "takafulemarat",
    "reinsurername": "peakre",
    "client_code": "null"
}
