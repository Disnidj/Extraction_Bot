"""
ADNIC API Module

This module provides API-based extraction for ADNIC insurance portal.
Uses the same pattern as Takaful API extraction.

Components:
- auth.py: Session management and authentication
- client.py: HTTP client for API calls
- extractor.py: Orchestrates API extraction for all TPAs/plans
- mapping.py: Hardcoded ADNIC API endpoints and configuration
- formatter.py: Converts extraction results to text format
"""

from .auth import ADNICAuth
from .client import ADNICApiClient
from .extractor import ADNICApiExtractor
from .mapping import ADNIC_API_CONFIG
from .formatter import ADNICFormatter

__all__ = [
    "ADNICAuth",
    "ADNICApiClient", 
    "ADNICApiExtractor",
    "ADNIC_API_CONFIG",
    "ADNICFormatter",
]
