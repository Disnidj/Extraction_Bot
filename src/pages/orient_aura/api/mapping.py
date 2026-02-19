"""
Orient Aura Portal Mapping Configuration
Hardcoded mapping of Groups, Emirates, TPAs, and Plans for Orient Insurance.

Key Difference from Takaful/Qatar:
- Orient uses a GROUP endpoint before emirates
- Flow: Industry → Group → Emirates → TPA → Plan → Benefits
"""

# ============================================================================
# PORTAL CONSTANTS
# ============================================================================

PORTAL_NAME = "ORIENT AURA"
PORTAL_REGION = "Dubai"  # Default region for all records

# ============================================================================
# HARDCODED MAPPING - Orient Aura Configuration
# ============================================================================

ORIENT_MAPPING = {
    "portal_name": "Orient Aura",
    "version_id": 44,  # Used to call group API
    
    # Group configuration - only group_name is hardcoded
    # group_id will be fetched from API by matching group_name
    "group": {
        "group_name": "Nextcare Sme"  # Target group to find in API response
    },
    
    # Emirates configuration (example for Nextcare Sme group)
    # This will be fetched dynamically, but we document the structure here
    "emirates_example": {
        "Dubai": {
            "emirates_master_id": "501,501,501,501,501,501,501,501,501,501,501,501,501,501,501,501",
            "group_id": "173,173,173,173,173,173,173,173,173,173,173,173,173,173,173,173",
            "reinsurer_company_id": "22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22"
        },
        "Abu Dhabi": {
            "emirates_master_id": "503,503,503,503,503,503",
            "group_id": "173,173,173,173,173,173",
            "reinsurer_company_id": "22,22,22,22,22,22"
        },
        "Northern Emirates": {
            "emirates_master_id": "502,502,502,502,502,502,502,502,502,502,502,502,502,502,502,502",
            "group_id": "173,173,173,173,173,173,173,173,173,173,173,173,173,173,173,173",
            "reinsurer_company_id": "22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22"
        }
    }
}

# API Base URLs
API_BASE_URL = "https://smehealth-api.aurainsure.tech"
PORTAL_BASE_URL = "https://smehealth.aurainsure.tech/08/orient"

# API Endpoints
ENDPOINTS = {
    "industry": "/quotes/generate/industry",
    "group": "/quotes/generate/group/{version_id}",  # New endpoint for Orient
    "emirates": "/quotes/generate/emirates",
    "tpa": "/quotes/generate/tpa",
    "plan": "/quotes/generate/plan",
    "benefits": "/quotes/generate/benefits"
}

# Additional headers required for Orient
CUSTOM_HEADERS = {
    "insurerurl": "orient",
    "reinsurername": "ccr",  # Default, may vary by group
    "client_code": "null"
}
