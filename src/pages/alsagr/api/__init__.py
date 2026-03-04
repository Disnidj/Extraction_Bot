"""
Al Sagr API Module
Provides API-based extraction for Al Sagr Insurance portal.

This module follows the same pattern as other API extractions (Orient Aura, ADNIC, Sukoon, etc.)

Components:
- auth.py: Token extraction from browser localStorage after Selenium login
- client.py: HTTP client for API calls to ndapi.alsagrins.ae
- extractor.py: Orchestrates API extraction for benefit structure
- mapping.py: Hardcoded Al Sagr API endpoints and configuration
- formatter.py: Converts extraction results to database-compatible text format
- quotation_creator.py: Creates quotations by filling portal form (hybrid flow)

Al Sagr uses JWT Bearer token authentication:
- Login via Selenium to https://sso.alsagrins.ae/login
- Extract JWT token from localStorage
- Use token for API calls to https://ndapi.alsagrins.ae/MiCore/api/GroupQuotation/

Hybrid Flow (new):
1. Login via Playwright
2. Create quotation by filling form (like old flow)
3. Get quotationId from created quotation
4. Use API extraction for benefit values
"""

from .auth import AlSagrAuthToken
from .client import AlSagrAPIClient
from .extractor import AlSagrAPIExtractor
from .formatter import AlSagrFormatter
from .quotation_creator import AlSagrQuotationCreator, create_quotation_with_excel
from .mapping import (
    PORTAL_NAME, 
    PORTAL_REGION, 
    API_BASE_URL, 
    BENEFIT_FIELD_MAPPING
)

__all__ = [
    "AlSagrAuthToken",
    "AlSagrAPIClient",
    "AlSagrAPIExtractor",
    "AlSagrFormatter",
    "AlSagrQuotationCreator",
    "create_quotation_with_excel",
    "PORTAL_NAME",
    "PORTAL_REGION",
    "API_BASE_URL",
    "BENEFIT_FIELD_MAPPING",
]
