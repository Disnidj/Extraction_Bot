"""
Takaful Portal Mapping Configuration
Hardcoded mapping of Emirates, TPAs, and Plans for Dubai.
Excludes Aafiya Ebp as requested.
"""

# ============================================================================
# HARDCODED MAPPING - Dubai Only, Excluding Aafiya Ebp
# ============================================================================

TAKAFUL_MAPPING = {
    "group_id": 31,
    "emirates": {
        "Dubai": {
            "emirates_id": "84",
            "emirates_master_id": "84",
            "tpas": {
                "Aafiya": {
                    "tpa_id": "386",
                    "reinsurer_company_id": 2
                },
                # "Aafiya Ebp" excluded as requested (tpa_id: 385)
                "Mednet": {
                    "tpa_id": "387",
                    "reinsurer_company_id": 2
                },
                "Nas": {
                    "tpa_id": "388",
                    "reinsurer_company_id": 2
                },
                "Nextcare": {
                    "tpa_id": "389",
                    "reinsurer_company_id": 2
                }
            }
        }
    }
}

# API Base URLs
API_BASE_URL = "https://smehealth-api.aurainsure.tech"
PORTAL_BASE_URL = "https://smehealth.aurainsure.tech"

# API Endpoints
ENDPOINTS = {
    "emirates": "/quotes/generate/emirates",
    "tpa": "/quotes/generate/tpa",
    "plan": "/quotes/generate/plan",
    "benefits": "/quotes/generate/benefits"
}
