"""
Takaful API Module
Provides API-based extraction of dropdown values from Takaful portal.
Updated to follow Orient Aura/Qatar pattern.
"""

from .auth import TakafulAuthToken
from .client import TakafulAPIClient
from .extractor import TakafulAPIExtractor
from .mapping import TAKAFUL_MAPPING, ENDPOINTS, CUSTOM_HEADERS, API_BASE_URL
from .formatter import TakafulFormatter

__all__ = [
    "TakafulAuthToken",
    "TakafulAPIClient", 
    "TakafulAPIExtractor",
    "TakafulFormatter",
    "TAKAFUL_MAPPING",
    "ENDPOINTS",
    "CUSTOM_HEADERS",
    "API_BASE_URL"
]
