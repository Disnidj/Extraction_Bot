"""
Liva Insurance API Configuration and Mapping

Contains API endpoints for health.livainsurance.ae cascading dropdown extraction.
Dependency hierarchy:
- Level 0: TPA (independent)
- Level 1: Region (depends on TPA)
- Level 2: Network (depends on TPA + Region)
- Level 3: Benefit fields (depends on TPA + Region + Network) - 20 APIs in parallel
- Level 4: Dental Limit (depends on TPA + Region + Network + Annual Limit)
- Level 5: Dental Copay (depends on TPA + Region + Network + Annual Limit + Dental Limit)
"""

# Base URL for Liva Insurance AJAX services
LIVA_API_BASE_URL = "https://health.livainsurance.ae/Portal/Eng/Services/SMEservice.asmx"

# Portal information
PORTAL_NAME = "Liva Insurance"
PORTAL_REGION = "Dubai"

# Portal URLs
PORTAL_LOGIN_URL = "https://health.livainsurance.ae/Portal/"
PORTAL_PRODUCTS_URL = "https://health.livainsurance.ae/Portal/Home/Products.aspx"

# =====================================================
# Level 0: Independent APIs (no dependencies)
# =====================================================
INDEPENDENT_APIS = [
    {
        "endpoint": "GetDropDownTPA",
        "category": "tpa",
        "display_name": "TPA Name",
        "description": "Third Party Administrators - Nas, NextCare, Almadhallah, Mednet, Inayah"
    },
]

# =====================================================
# Level 1: TPA-dependent APIs
# =====================================================
TPA_DEPENDENT_APIS = [
    {
        "endpoint": "GetDropDownRegion",
        "category": "region",
        "display_name": "Region",
        "description": "Geographical region - AUH, DXB / NE",
        "depends_on": ["tpa"]
    },
]

# =====================================================
# Level 2: TPA + Region dependent APIs
# =====================================================
REGION_DEPENDENT_APIS = [
    {
        "endpoint": "GetDropDownNWRegion",
        "category": "nw",
        "display_name": "Network",
        "description": "Network plans available for the TPA and Region",
        "depends_on": ["tpa", "region"]
    },
]

# =====================================================
# Level 3: TPA + Region + Network dependent APIs
# These can all be called in parallel
# =====================================================
NETWORK_DEPENDENT_APIS = [
    {
        "endpoint": "GetDropDownALNw",
        "category": "al",
        "display_name": "Plan Annual Limit",
        "description": "Annual benefit limit options",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownTerritoyNw",
        "category": "tritory",
        "display_name": "Geographical Area of Cover",
        "description": "Territorial/geographical coverage area",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownHomeNursing",
        "category": "HomeNursing",
        "display_name": "Home Nursing Charges",
        "description": "Home nursing benefit limits",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownRoom",
        "category": "room",
        "display_name": "Hospital accommodation, room and board",
        "description": "Room type for hospital accommodation",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownDeductable",
        "category": "deductable",
        "display_name": "Deductible",
        "description": "Deductible amount options",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownSPAccess",
        "category": "SPAccess1",
        "display_name": "Specialist Access",
        "description": "Specialist access type",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownCopay",
        "category": "copay",
        "display_name": "Co-pay Lab / Radiology and Diagnostics",
        "description": "Co-payment percentage for lab/radiology/diagnostics",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownPharmacyLimit",
        "category": "phlimit",
        "display_name": "Pharmacy Limit",
        "description": "Pharmacy benefit limit",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownPharmacyCopay",
        "category": "phcopay",
        "display_name": "Pharmacy Co-Pay",
        "description": "Pharmacy co-payment percentage",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownPhysiotherapyLimit",
        "category": "phytheLimit",
        "display_name": "Physiotherapy Limit",
        "description": "Physiotherapy sessions limit",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownPhysiotherapyCopay",
        "category": "phcopay",
        "display_name": "Physiotherapy Co-Pay",
        "description": "Physiotherapy co-payment percentage",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownMatLimit",
        "category": "matLimit",
        "display_name": "Maternity Benefit Limit",
        "description": "Maternity benefit limit options",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownMatOPCopay",
        "category": "matOPcopay",
        "display_name": "Maternity Benefit OP Co-pay",
        "description": "Maternity outpatient co-payment",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownMatIPCopay",
        "category": "matIPcopay",
        "display_name": "Maternity Benefit IP Co-pay",
        "description": "Maternity inpatient co-payment",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownRenalDialysis",
        "category": "RenalDialysis",
        "display_name": "Renal Dialysis",
        "description": "Renal dialysis coverage",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownOrganTransplantation",
        "category": "OrganTransplantation",
        "display_name": "Organ Transplantation",
        "description": "Organ transplantation coverage",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownOpticalLimit",
        "category": "opticalLimit",
        "display_name": "Optical Benefit Limit",
        "description": "Optical/vision benefit limit",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownOpticalCopay",
        "category": "opticalCopay",
        "display_name": "Optical Benefit Co-Pay",
        "description": "Optical co-payment percentage",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownAlternativeMedicine",
        "category": "AltMedLimit",
        "display_name": "Alternative Medicine Benefit Limit",
        "description": "Alternative medicine benefit limit",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownAlternativeMedicineCopay",
        "category": "AltMedCopay",
        "display_name": "Alternative Medicine Benefit Co-Pay",
        "description": "Alternative medicine co-payment",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownPsychiatric",
        "category": "Psychiatric",
        "display_name": "Psychiatric Benefit",
        "description": "Psychiatric coverage options",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownRepartiation",
        "category": "Repartiation",
        "display_name": "Repatriation of mortal remains",
        "description": "Repatriation benefit limits",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownInternationalAssistance",
        "category": "InternationalAssistance",
        "display_name": "International Assistance",
        "description": "International assistance coverage",
        "depends_on": ["tpa", "region", "nw"]
    },
    {
        "endpoint": "GetDropDownTeleconsultation",
        "category": "Teleconsultation",
        "display_name": "Teleconsultation",
        "description": "Teleconsultation coverage",
        "depends_on": ["tpa", "region", "nw"]
    },
]

# =====================================================
# Level 4: TPA + Region + Network + Annual Limit dependent
# =====================================================
ANNUAL_LIMIT_DEPENDENT_APIS = [
    {
        "endpoint": "GetDropDowndentalLimit",
        "category": "dentalLim",
        "display_name": "Dental Benefit Limit",
        "description": "Dental benefit limit options",
        "depends_on": ["tpa", "region", "nw", "al"]
    },
]

# =====================================================
# Level 5: TPA + Region + Network + Annual Limit + Dental Limit dependent
# =====================================================
DENTAL_LIMIT_DEPENDENT_APIS = [
    {
        "endpoint": "GetDropDowndentalCopay",
        "category": "dentalcopay",
        "display_name": "Dental Benefit Co-Pay",
        "description": "Dental co-payment percentage",
        "depends_on": ["tpa", "region", "nw", "al", "dentalLim"]
    },
]

# =====================================================
# Full API Configuration
# =====================================================
LIVA_API_CONFIG = {
    "base_url": LIVA_API_BASE_URL,
    "portal_name": PORTAL_NAME,
    "portal_region": PORTAL_REGION,
    "apis": {
        "level_0": INDEPENDENT_APIS,
        "level_1": TPA_DEPENDENT_APIS,
        "level_2": REGION_DEPENDENT_APIS,
        "level_3": NETWORK_DEPENDENT_APIS,
        "level_4": ANNUAL_LIMIT_DEPENDENT_APIS,
        "level_5": DENTAL_LIMIT_DEPENDENT_APIS,
    }
}

# =====================================================
# Default Headers for API Calls
# =====================================================
DEFAULT_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://health.livainsurance.ae",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}
