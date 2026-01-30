"""
Sukoon API Extraction Module

Provides API-based extraction for Sukoon Insurance portal.
Uses single "Mega API" pattern - PopulateDDL returns all options.
"""

from .auth import SukoonAuth
from .client import SukoonApiClient, DropdownOption
from .extractor import SukoonApiExtractor
from .formatter import SukoonFormatter
from .mapping import (
    SUKOON_API_URL,
    PORTAL_NAME,
    REGIONS,
    RESPONSE_FIELD_MAPPING,
)

__all__ = [
    "SukoonAuth",
    "SukoonApiClient",
    "DropdownOption",
    "SukoonApiExtractor",
    "SukoonFormatter",
    "SUKOON_API_URL",
    "PORTAL_NAME",
    "REGIONS",
    "RESPONSE_FIELD_MAPPING",
]
