"""
Centralized broker configuration management.
Controls which brokers are active for scheduled API extraction runs.

This file defines active brokers without hardcoding broker-portal mappings.
Portal mappings are stored in the database table: Medical_CTN_Broker_Portal_Mapping
"""

from typing import List, Dict, Optional

# ============================================================================
# ACTIVE BROKERS CONFIGURATION
# ============================================================================
# To enable/disable brokers for scheduled runs, modify the 'enabled' flag.
# This list controls which brokers appear in interactive selection menus
# and which brokers run in scheduled batch jobs.

ACTIVE_BROKERS = [
    {
        "broker_id": 2,
        "name": "Unitrust",
        "enabled": True,
        "contact_email": "unitrust@example.com",
        "description": "Unitrust Insurance Brokers"
    },
    {
        "broker_id": 3,
        "name": "Lifecare International",
        "enabled": True,
        "contact_email": "rpa-dev@lifecareinternational.com",
        "description": "Primary broker - Lifecare International Insurance Brokers"
    },
    {
        "broker_id": 6,
        "name": "VIVA",
        "enabled": True,
        "contact_email": "viva@example.com",
        "description": "VIVA Insurance Brokers"
    },
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_active_broker_ids() -> List[int]:
    """
    Get list of enabled broker IDs.
    
    Returns:
        List of broker IDs where enabled=True
        
    Example:
        >>> get_active_broker_ids()
        [2, 3, 6]
    """
    return [b["broker_id"] for b in ACTIVE_BROKERS if b["enabled"]]


def get_all_configured_brokers() -> List[Dict]:
    """
    Get all configured brokers (both enabled and disabled).
    
    Returns:
        List of broker configuration dictionaries
        
    Example:
        >>> brokers = get_all_configured_brokers()
        >>> len(brokers)
        3
    """
    return ACTIVE_BROKERS


def get_enabled_brokers() -> List[Dict]:
    """
    Get only enabled brokers with full metadata.
    
    Returns:
        List of enabled broker dictionaries
    """
    return [b for b in ACTIVE_BROKERS if b["enabled"]]


def get_broker_metadata(broker_id: int) -> Optional[Dict]:
    """
    Get metadata for a specific broker.
    
    Args:
        broker_id: The broker ID to lookup
        
    Returns:
        Broker metadata dict or None if not found
        
    Example:
        >>> meta = get_broker_metadata(3)
        >>> meta['name']
        'Lifecare International'
    """
    for broker in ACTIVE_BROKERS:
        if broker["broker_id"] == broker_id:
            return broker
    return None


def get_broker_name(broker_id: int) -> str:
    """
    Get broker display name by ID.
    
    Args:
        broker_id: The broker ID to lookup
        
    Returns:
        Broker name or fallback string
        
    Example:
        >>> get_broker_name(3)
        'Lifecare International'
        >>> get_broker_name(999)
        'Broker 999'
    """
    metadata = get_broker_metadata(broker_id)
    if metadata:
        return metadata["name"]
    return f"Broker {broker_id}"


def is_broker_enabled(broker_id: int) -> bool:
    """
    Check if a specific broker is enabled.
    
    Args:
        broker_id: The broker ID to check
        
    Returns:
        True if broker exists and enabled=True, False otherwise
        
    Example:
        >>> is_broker_enabled(3)
        True
        >>> is_broker_enabled(999)
        False
    """
    metadata = get_broker_metadata(broker_id)
    if metadata:
        return metadata.get("enabled", False)
    return False


def get_broker_contact(broker_id: int) -> Optional[str]:
    """
    Get broker contact email.
    
    Args:
        broker_id: The broker ID to lookup
        
    Returns:
        Contact email or None
    """
    metadata = get_broker_metadata(broker_id)
    if metadata:
        return metadata.get("contact_email")
    return None


def validate_broker_ids(broker_ids: List[int]) -> bool:
    """
    Validate that all broker IDs exist and are enabled.
    
    Args:
        broker_ids: List of broker IDs to validate
        
    Returns:
        True if all broker IDs are valid and enabled, False otherwise
        
    Example:
        >>> validate_broker_ids([2, 3])
        True
        >>> validate_broker_ids([2, 999])
        False
    """
    if not broker_ids:
        return False
    
    enabled_ids = set(get_active_broker_ids())
    return all(broker_id in enabled_ids for broker_id in broker_ids)


def validate_broker_ids_detailed(broker_ids: List[int]) -> Dict[str, List[int]]:
    """
    Validate a list of broker IDs with detailed breakdown.
    
    Args:
        broker_ids: List of broker IDs to validate
        
    Returns:
        Dict with 'valid', 'disabled', and 'unknown' broker ID lists
        
    Example:
        >>> validate_broker_ids_detailed([3, 6, 999])
        {
            'valid': [3, 6],
            'disabled': [],
            'unknown': [999]
        }
    """
    valid = []
    disabled = []
    unknown = []
    
    configured_ids = {b["broker_id"] for b in ACTIVE_BROKERS}
    enabled_ids = set(get_active_broker_ids())
    
    for broker_id in broker_ids:
        if broker_id not in configured_ids:
            unknown.append(broker_id)
        elif broker_id not in enabled_ids:
            disabled.append(broker_id)
        else:
            valid.append(broker_id)
    
    return {
        "valid": valid,
        "disabled": disabled,
        "unknown": unknown
    }


def get_broker_summary(broker_id: int) -> str:
    """
    Get formatted summary for a specific broker.
    
    Args:
        broker_id: The broker ID to get summary for
        
    Returns:
        Formatted string with broker information
        
    Example:
        >>> get_broker_summary(3)
        'Broker 3 - Lifecare International'
    """
    metadata = get_broker_metadata(broker_id)
    if metadata:
        return f"Broker {broker_id} - {metadata['name']}"
    return f"Broker {broker_id}"


def get_all_brokers_summary() -> str:
    """
    Get formatted summary of all broker configuration.
    
    Returns:
        Multi-line string with broker status
        
    Example output:
        Active Brokers: 3
          • Broker 2 - Unitrust
          • Broker 3 - Lifecare International
          • Broker 6 - VIVA
    """
    enabled = get_enabled_brokers()
    disabled = [b for b in ACTIVE_BROKERS if not b["enabled"]]
    
    summary = f"Active Brokers: {len(enabled)}\n"
    for broker in enabled:
        summary += f"  • Broker {broker['broker_id']} - {broker['name']}\n"
    
    if disabled:
        summary += f"\nDisabled Brokers: {len(disabled)}\n"
        for broker in disabled:
            summary += f"  • Broker {broker['broker_id']} - {broker['name']}\n"
    
    return summary
