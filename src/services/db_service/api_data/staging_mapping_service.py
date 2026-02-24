"""
Dropdown Mapping Service

Handles loading and applying dropdown name mappings from the database.
Maps portal-specific dropdown names to standard database field names.

Example:
    Portal field "Dental Benefit" (Liva Globalcare) -> "Dental" (standard)
"""

import traceback
from typing import List, Dict, Tuple, Set

from .staging_config import MAPPING_TABLE, SKIP_DROPDOWN_NAMES, ONLY_UPLOAD_MAPPED


def load_dropdown_mappings(db, company: str) -> Dict[str, str]:
    """
    Load dropdown name mappings from Medical_CTN_Portal_Field_Mapping table.
    
    Maps portal-specific dropdown names to standard database names.
    
    Args:
        db: Database connection object with fetch_all method
        company: Company/portal name (column name in mapping table)
        
    Returns:
        Dict mapping {portal_dropdown_name: standard_dropdown_name}
    """
    mappings = {}
    
    try:
        # Query to get mappings for this company
        # Column name is the company name (e.g., MaxHealth, Sukoon, Qatar, Liva Globalcare)
        query = f"""
            SELECT `{company}`, Dropdown_Name 
            FROM {MAPPING_TABLE}
            WHERE `{company}` IS NOT NULL AND `{company}` != ''
        """
        rows = db.fetch_all(query)
        
        if rows:
            for row in rows:
                # Try both exact column name and stripped version
                portal_name = row.get(company, "") or row.get(company.strip(), "")
                standard_name = row.get("Dropdown_Name", "")
                
                # Strip whitespace from both values
                if portal_name:
                    portal_name = portal_name.strip()
                if standard_name:
                    standard_name = standard_name.strip()
                    
                if portal_name and standard_name:
                    mappings[portal_name] = standard_name
                    
        print(f"   Loaded {len(mappings)} dropdown mappings for {company}")
        
    except Exception as e:
        print(f"   ⚠️ Could not load mappings for {company}: {e}")
        print(f"   → Will use original dropdown names")
        traceback.print_exc()
    
    return mappings


def apply_dropdown_mapping(
    records: List[Dict], 
    mappings: Dict[str, str], 
    only_mapped: bool = None
) -> Tuple[List[Dict], int, int, Dict[str, str], Set[str]]:
    """
    Apply dropdown name mappings to records.
    
    Args:
        records: List of record dictionaries
        mappings: Dict mapping {portal_dropdown_name: standard_dropdown_name}
        only_mapped: If True, return only records that have a mapping (skip unmapped)
                    Defaults to ONLY_UPLOAD_MAPPED from config
        
    Returns:
        Tuple of (filtered_records, mapped_count, unmapped_count, applied_mappings, unmapped_names)
        - filtered_records: Records to upload (only mapped if only_mapped=True)
        - mapped_count: Number of records that were mapped
        - unmapped_count: Number of records that were not mapped
        - applied_mappings: Dict of {portal_name: db_name} that were actually applied
        - unmapped_names: Set of dropdown names that had no mapping
    """
    if only_mapped is None:
        only_mapped = ONLY_UPLOAD_MAPPED
        
    mapped_records = []
    unmapped_records = []
    unmapped_names = set()
    applied_mappings = {}  # Track which mappings were actually used
    
    for record in records:
        original_name = record.get("Dropdown_Name", "")
        # Try with stripped value
        original_name_stripped = original_name.strip() if original_name else ""
        
        if original_name in mappings:
            new_name = mappings[original_name]
            record["Dropdown_Name"] = new_name
            mapped_records.append(record)
            # Track the mapping (only add once per unique original name)
            if original_name not in applied_mappings:
                applied_mappings[original_name] = new_name
        elif original_name_stripped in mappings:
            new_name = mappings[original_name_stripped]
            record["Dropdown_Name"] = new_name
            mapped_records.append(record)
            if original_name_stripped not in applied_mappings:
                applied_mappings[original_name_stripped] = new_name
        else:
            unmapped_records.append(record)
            unmapped_names.add(original_name)
    
    # Return only mapped records if only_mapped is True
    if only_mapped:
        return mapped_records, len(mapped_records), len(unmapped_records), applied_mappings, unmapped_names
    else:
        # Return all records (mapped ones have been renamed, unmapped keep original names)
        return mapped_records + unmapped_records, len(mapped_records), len(unmapped_records), applied_mappings, unmapped_names


def filter_skip_dropdowns(records: List[Dict], skip_names: Set[str] = None) -> Tuple[List[Dict], int]:
    """
    Filter out records with dropdown names that should be skipped.
    
    Args:
        records: List of record dictionaries
        skip_names: Set of dropdown names to skip (defaults to SKIP_DROPDOWN_NAMES)
        
    Returns:
        Tuple of (filtered_records, skipped_count)
    """
    if skip_names is None:
        skip_names = SKIP_DROPDOWN_NAMES
    
    filtered = [
        r for r in records 
        if r.get("Dropdown_Name", "") not in skip_names
    ]
    skipped = len(records) - len(filtered)
    
    return filtered, skipped


def get_unique_dropdown_names(records: List[Dict]) -> Set[str]:
    """
    Get set of unique dropdown names from records.
    
    Args:
        records: List of record dictionaries
        
    Returns:
        Set of unique dropdown names
    """
    return {
        r.get("Dropdown_Name", "") 
        for r in records 
        if r.get("Dropdown_Name", "")
    }


def build_mapping_summary(
    applied_mappings: Dict[str, Dict[str, str]], 
    unmapped_names: Dict[str, Set[str]],
    only_mapped_mode: bool
) -> Dict:
    """
    Build a summary dictionary of mapping results.
    
    Args:
        applied_mappings: {company: {portal_name: db_name}}
        unmapped_names: {company: set of unmapped names}
        only_mapped_mode: Whether only mapped dropdowns were uploaded
        
    Returns:
        Summary dictionary for reports
    """
    return {
        'applied_mappings': applied_mappings,
        'unmapped_names': {k: list(v) for k, v in unmapped_names.items()},
        'only_mapped_mode': only_mapped_mode,
        'total_mappings': sum(len(m) for m in applied_mappings.values()),
        'total_unmapped': sum(len(u) for u in unmapped_names.values())
    }
