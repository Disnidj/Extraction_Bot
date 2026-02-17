"""
Orient Aura API Module
Provides API-based extraction for Orient Aura insurance portal.

This module follows the same pattern as Takaful and Qatar API extractions.

Components:
- auth.py: Token extraction from browser localStorage
- client.py: HTTP client for API calls
- extractor.py: Orchestrates API extraction (Industry → Groups → Emirates → TPAs → Plans → Benefits)
- mapping.py: Hardcoded Orient Aura API endpoints and configuration
- formatter.py: Converts extraction results to database-compatible text format
"""

from .auth import OrientAuraAuthToken
from .client import OrientAuraAPIClient
from .extractor import OrientAuraAPIExtractor
from .formatter import OrientAuraFormatter
from .mapping import ORIENT_MAPPING

__all__ = [
    "OrientAuraAuthToken",
    "OrientAuraAPIClient",
    "OrientAuraAPIExtractor",
    "OrientAuraFormatter",
    "ORIENT_MAPPING",
]
