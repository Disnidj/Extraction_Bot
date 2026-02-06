"""
TPA/Network Expansion Service

Provides shared functionality for expanding records with empty TPA/Network values
to all TPA/Network combinations. This service is portal-agnostic and can be used
by any formatter that needs to expand cascading dropdown data.

Usage:
    from src.services.formatter_service import expand_empty_tpa_network
    
    expanded_records = expand_empty_tpa_network(parsed_records)
"""

from typing import List, Dict, Set
from itertools import product


def expand_empty_tpa_network(records: List[Dict]) -> List[Dict]:
    """
    Expand records with empty TPA/Network to all TPA/Network combinations.
    
    This is a shared utility used by all portal formatters to ensure cascading
    dropdowns work regardless of TPA/Network selection in the web application.
    
    IMPORTANT: This function is FIELD-AGNOSTIC - it works for ANY dropdown field
    that has empty TPA/Network values, not just specific fields like Business Nature.
    The expansion logic doesn't care about field names, it only looks at whether
    TPA/Network fields are empty.
    
    Common use cases:
    - Pre-Level fields (Business Nature, Industry Categories) extracted with empty TPA/Network
    - Any other dropdown that happens to be extracted with empty TPA/Network
    - Fields that should appear for all TPA/Network combinations
    
    For records where TPA and/or Network is empty:
    - Collects all unique TPA values from records that have TPA
    - Collects all unique Network values from records that have Network
    - Creates combinations for records with missing TPA/Network
    
    Pre-Level fields (like Business Nature, Industry Categories) are extracted
    with empty TPA/Network and then expanded to all combinations found in the
    extraction results.
    
    Args:
        records: List of record dictionaries with database schema format:
                 {"Broker_ID": int, "Company": str, "TPA": str, "Network": str,
                  "Region": str, "Dropdown_Name": str, "Selection_Value": str}
        
    Returns:
        Expanded list of records with TPA/Network combinations populated
        
    Example:
        Input: [
            {"TPA": "", "Network": "", "Dropdown_Name": "Business Nature", "Selection_Value": "Manufacturing"},
            {"TPA": "Mednet", "Network": "Gold", "Dropdown_Name": "Room Category", "Selection_Value": "Private"}
        ]
        
        Output: [
            {"TPA": "Mednet", "Network": "Gold", "Dropdown_Name": "Business Nature", "Selection_Value": "Manufacturing"},
            {"TPA": "Mednet", "Network": "Gold", "Dropdown_Name": "Room Category", "Selection_Value": "Private"}
        ]
    """
    if not records:
        return records
    
    # Collect all unique TPA and Network values from records that have them
    all_tpas: Set[str] = set()
    all_networks: Set[str] = set()
    all_dropdown_names: Set[str] = set()
    independent_dropdown_names: Set[str] = set()  # Dropdowns with both TPA and Network
    expanded_dropdown_names: Set[str] = set()  # Dropdowns that needed expansion
    
    for record in records:
        tpa = record.get("TPA", "")
        network = record.get("Network", "")
        dropdown_name = record.get("Dropdown_Name", "")
        
        if dropdown_name:
            all_dropdown_names.add(dropdown_name)
        
        if tpa and tpa.strip():
            all_tpas.add(tpa.strip())
        if network and network.strip():
            all_networks.add(network.strip())
        
        # Track which dropdowns are independent vs need expansion
        has_tpa = bool(tpa and tpa.strip())
        has_network = bool(network and network.strip())
        if has_tpa and has_network and dropdown_name:
            independent_dropdown_names.add(dropdown_name)
        elif dropdown_name:
            expanded_dropdown_names.add(dropdown_name)
    
    # If no TPA or Network values found, return original records
    if not all_tpas and not all_networks:
        print(f"   ⚠️ No TPA/Network values found in records, skipping expansion")
        return records
    
    # Ensure we have at least one value for each
    if not all_tpas:
        all_tpas.add("N/A")
    if not all_networks:
        all_networks.add("N/A")
    
    print(f"\n   {'='*50}")
    print(f"   📊 TPA/NETWORK EXPANSION SUMMARY")
    print(f"   {'='*50}")
    print(f"   📊 Found {len(all_tpas)} unique TPA values: {list(all_tpas)}")
    print(f"   📊 Found {len(all_networks)} unique Network values: {list(all_networks)}")
    print(f"   📊 Total unique dropdown fields: {len(all_dropdown_names)}")
    print(f"   ✅ Independent dropdowns (have TPA & Network): {len(independent_dropdown_names)}")
    if independent_dropdown_names:
        for name in sorted(independent_dropdown_names):
            print(f"      • {name}")
    print(f"   🔄 Dropdowns needing expansion: {len(expanded_dropdown_names)}")
    if expanded_dropdown_names:
        for name in sorted(expanded_dropdown_names):
            print(f"      • {name}")
    
    expanded_records = []
    records_expanded_count = 0
    original_with_values_count = 0
    
    for record in records:
        tpa = record.get("TPA", "")
        network = record.get("Network", "")
        
        has_tpa = bool(tpa and tpa.strip())
        has_network = bool(network and network.strip())
        
        if has_tpa and has_network:
            # Record has both TPA and Network, keep as is
            expanded_records.append(record)
            original_with_values_count += 1
        else:
            # Record missing TPA and/or Network - create combinations
            records_expanded_count += 1
            
            # Determine which values to iterate over
            tpas_to_use = [tpa] if has_tpa else list(all_tpas)
            networks_to_use = [network] if has_network else list(all_networks)
            
            # Create all combinations
            for combo_tpa, combo_network in product(tpas_to_use, networks_to_use):
                new_record = record.copy()
                new_record["TPA"] = combo_tpa
                new_record["Network"] = combo_network
                expanded_records.append(new_record)
    
    combinations_created = len(expanded_records) - original_with_values_count
    print(f"\n   📊 EXPANSION RESULTS:")
    print(f"   ✅ Independent records (kept as-is): {original_with_values_count}")
    print(f"   🔄 Records expanded: {records_expanded_count} → {combinations_created} combinations")
    print(f"   📈 Total records: {len(records)} → {len(expanded_records)}")
    print(f"   {'='*50}")
    
    return expanded_records
