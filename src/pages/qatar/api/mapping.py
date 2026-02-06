"""
Qatar Insurance Portal Mapping Configuration
Hardcoded values for Dubai region and NAS TPA only.
"""
# Default region for all records
PORTAL_REGION = "Dubai"
# Qatar uses group_id 272
QATAR_MAPPING = {
    "portal_name": "QATAR INSURANCE CO",
    "group_id": 272,
    "reinsurer_company_id": 7,
    "reinsurer_company_name": "icici-ri",
    
    # Only Dubai emirate
    "emirates": {
        "Dubai": {
            "emirates_id": "861,861,861,861,861,861",
            "group_id": "272,272,272,272,272,272",
            "reinsurer_company_id": "7,7,7,7,7,7",
            
            # Only NAS TPA
            "tpas": {
                "NAS": {
                    "tpa_id": "990,990,990,990,990,990",
                    "reinsurer_company_id": 7
                }
            }
        }
    }
}

# API endpoints (same base as Takaful - Aura platform)
API_BASE_URL = "https://smehealth-api.aurainsure.tech"

API_ENDPOINTS = {
    "emirates": f"{API_BASE_URL}/quotes/generate/emirates",
    "tpa": f"{API_BASE_URL}/quotes/generate/tpa", 
    "plan": f"{API_BASE_URL}/quotes/generate/plan",
    "benefits": f"{API_BASE_URL}/quotes/generate/benefits",
    "industry": f"{API_BASE_URL}/quotes/generate/industry"
}
