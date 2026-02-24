"""
Comparison Utilities for Staging Upload Service

Helper functions for comparing values and detecting differences
including whitespace and case changes.
"""

import re
from typing import Tuple


def highlight_difference(old_value: str, new_value: str) -> Tuple[str, str, str]:
    """
    Analyze the difference between two strings.
    Detects whitespace-only and case-only differences.
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Tuple of (old_highlighted, new_highlighted, difference_type)
        
        difference_type can be:
        - "NO_CHANGE": Values are identical
        - "WHITESPACE_CHANGE": Only leading/trailing whitespace differs
        - "INTERNAL_WHITESPACE": Internal whitespace differs (e.g., "3 %" vs "3%")
        - "CASE_CHANGE": Only letter case differs
        - "VALUE_CHANGE": Actual content differs
    """
    if old_value is None:
        old_value = ""
    if new_value is None:
        new_value = ""
        
    if old_value == new_value:
        return old_value, new_value, "NO_CHANGE"
    
    # Check for whitespace-only differences (leading/trailing)
    old_stripped = old_value.strip()
    new_stripped = new_value.strip()
    
    if old_stripped == new_stripped:
        return (
            f'"{old_value}"',
            f'"{new_value}"',
            "WHITESPACE_CHANGE"
        )
    
    # Check for internal whitespace differences
    old_normalized = re.sub(r'\s+', ' ', old_value.strip())
    new_normalized = re.sub(r'\s+', ' ', new_value.strip())
    
    if old_normalized == new_normalized:
        return (
            f'"{old_value}"',
            f'"{new_value}"',
            "INTERNAL_WHITESPACE"
        )
    
    # Check for case differences only
    if old_value.lower() == new_value.lower():
        return (
            f'"{old_value}"',
            f'"{new_value}"',
            "CASE_CHANGE"
        )
    
    # General value change
    return f'"{old_value}"', f'"{new_value}"', "VALUE_CHANGE"


def format_value_for_display(value: str, show_markers: bool = True) -> str:
    """
    Format a value for display, making whitespace visible if present.
    
    Uses middle dot (·) to show spaces when whitespace issues are detected.
    
    Args:
        value: The string value
        show_markers: Whether to show whitespace markers
        
    Returns:
        Formatted string with visible whitespace markers if applicable
        
    Examples:
        "test " -> 'test   [shown: test·]'
        " test" -> ' test  [shown: ·test]'
        "a  b"  -> 'a  b  [shown: a··b]'
    """
    if value is None:
        return "(null)"
    
    if not show_markers:
        return value
    
    # Check for leading/trailing spaces or multiple consecutive spaces
    has_leading = value != value.lstrip()
    has_trailing = value != value.rstrip()
    has_multiple_spaces = '  ' in value
    
    if has_leading or has_trailing or has_multiple_spaces:
        # Show spaces as visible markers (middle dot)
        visible = value.replace(' ', '·')
        return f'{value}  [shown: {visible}]'
    
    return value


def get_comparison_key(row: dict) -> tuple:
    """
    Create a comparison key tuple from a row dict.
    
    The key identifies a unique dropdown value across:
    Company + TPA + Network + Region + Dropdown_Name
    
    Args:
        row: Dictionary with column values
        
    Returns:
        Tuple of (Company, TPA, Network, Region, Dropdown_Name)
    """
    return (
        row.get("Company", "") or "",
        row.get("TPA", "") or "",
        row.get("Network", "") or "",
        row.get("Region", "") or "",
        row.get("Dropdown_Name", "") or ""
    )


def normalize_value(value: str) -> str:
    """
    Normalize a value for comparison (trim and handle None).
    
    Args:
        value: The value to normalize
        
    Returns:
        Normalized string (empty string if None)
    """
    if value is None:
        return ""
    return str(value)


def is_whitespace_only_change(old_value: str, new_value: str) -> bool:
    """
    Check if the difference between two values is whitespace-only.
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        True if only whitespace differs, False otherwise
    """
    _, _, diff_type = highlight_difference(old_value, new_value)
    return diff_type in ("WHITESPACE_CHANGE", "INTERNAL_WHITESPACE")


def is_case_only_change(old_value: str, new_value: str) -> bool:
    """
    Check if the difference between two values is case-only.
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        True if only case differs, False otherwise
    """
    _, _, diff_type = highlight_difference(old_value, new_value)
    return diff_type == "CASE_CHANGE"
