"""
ADNIC Formatter

Converts extraction results to database-compatible format.
Writes records to portal-specific folder: extracted_data/adnic/adnic_extracted_YYYYMMDD_HHMMSS.txt

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value

TPA/Network Expansion:
- For records with empty TPA and/or Network, creates combinations with all existing TPA/Network values
- This ensures cascading dropdowns work regardless of TPA/Network selection in the web app
"""

import json
import os
from typing import Dict, List, Set
from datetime import datetime
from itertools import product

# Portal name for this formatter
PORTAL_NAME = "adnic"

# Default Broker ID - can be configured
DEFAULT_BROKER_ID = 3


class ADNICFormatter:
    """
    Formats ADNIC extraction results and writes to file.
    
    Output format matches database schema:
    {"Broker_ID": 3, "Company": "ADNIC", "TPA": "...", "Network": "...", 
     "Region": "...", "Dropdown_Name": "...", "Selection_Value": "..."}
    
    Files are saved to: {output_dir}/adnic/adnic_extracted_YYYYMMDD_HHMMSS.txt
    """
    
    def __init__(self, output_path: str = None, output_dir: str = "extracted_data",
                 broker_id: int = DEFAULT_BROKER_ID):
        """
        Initialize formatter with output path.
        
        Args:
            output_path: Path to output file. If None, generates portal-specific path.
            output_dir: Base output directory for extracted files.
            broker_id: Broker ID for database records.
        """
        self.portal_name = PORTAL_NAME
        self.company_name = "ADNIC"
        self.output_path = output_path
        self.output_dir = output_dir
        self.broker_id = broker_id
        self.records_written = 0
        
        # If no path provided, create portal-specific path
        if not self.output_path:
            self.output_path = self._generate_output_path()
    
    def _generate_output_path(self) -> str:
        """
        Generate portal-specific output path.
        
        Creates folder structure: {output_dir}/{portal_name}/
        File naming: {portal_name}_extracted_YYYYMMDD_HHMMSS.txt
        
        Returns:
            Full path to output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create portal-specific folder
        folder = os.path.join(self.output_dir, self.portal_name)
        os.makedirs(folder, exist_ok=True)
        
        # Generate filename
        filename = f"{self.portal_name}_extracted_{timestamp}.txt"
        
        return os.path.join(folder, filename)
    
    def format_record(self, record: Dict) -> List[str]:
        """
        Format a single record as database rows (one per value).
        
        Converts old format:
        {"data": {"Portal": "...", "field_name": "...", "values": [...]}}
        
        To database format (one row per value):
        {"Broker_ID": 3, "Company": "ADNIC", ..., "Selection_Value": "..."}
        
        Args:
            record: Record dict to format (can be old or new format)
            
        Returns:
            List of JSON strings (one per value)
        """
        rows = []
        
        # Handle old format with "data" wrapper
        if "data" in record:
            data = record["data"]
            tpa = data.get("TPA", "")
            network = data.get("Network", "")
            region = data.get("Region", "")
            # Check for various field name formats: "field name", "field_name", "Dropdown_Name"
            dropdown_name = data.get("field name", data.get("field_name", data.get("Dropdown_Name", "")))
            values = data.get("values", [])
            
            for value in values:
                if not value:
                    continue
                row = {
                    "Broker_ID": self.broker_id,
                    "Company": self.company_name,
                    "TPA": tpa,
                    "Network": network,
                    "Region": region,
                    "Dropdown_Name": dropdown_name,
                    "Selection_Value": value
                }
                rows.append(json.dumps(row, ensure_ascii=False))
        
        # Handle new database format (already flat)
        elif "Selection_Value" in record:
            # Ensure broker_id and company are set
            record.setdefault("Broker_ID", self.broker_id)
            record.setdefault("Company", self.company_name)
            rows.append(json.dumps(record, ensure_ascii=False))
        
        return rows
    
    def write_records(self, records: List[Dict]) -> str:
        """
        Write all records to file in database format.
        Expands records with empty TPA/Network to all combinations.
        
        Args:
            records: List of record dicts (old or new format)
            
        Returns:
            Path to output file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        all_rows = []
        for record in records:
            all_rows.extend(self.format_record(record))
        
        # Parse rows back to dicts for expansion
        parsed_records = [json.loads(row) for row in all_rows]
        
        # Expand records with empty TPA/Network
        expanded_records = self._expand_empty_tpa_network(parsed_records)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for record in expanded_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        self.records_written = len(expanded_records)
        print(f"\n💾 Saved {self.records_written} database rows to: {self.output_path}")
        
        return self.output_path
    
    def _expand_empty_tpa_network(self, records: List[Dict]) -> List[Dict]:
        """
        Expand records with empty TPA/Network to all TPA/Network combinations.
        
        For records where TPA and/or Network is empty:
        - Collects all unique TPA values from records that have TPA
        - Collects all unique Network values from records that have Network
        - Creates combinations for records with missing TPA/Network
        
        Args:
            records: List of record dictionaries
            
        Returns:
            Expanded list of records with TPA/Network combinations
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

    def write_json(self, records: List[Dict], json_path: str = None) -> str:
        """
        Write records as formatted JSON file (optional).
        
        Args:
            records: List of record dicts
            json_path: Path for JSON file
            
        Returns:
            Path to JSON file
        """
        if not json_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = f"extracted_data/adnic_benefits_{timestamp}.json"
        
        # Structure the data hierarchically
        structured = {
            "portal": "ADNIC",
            "extracted_at": datetime.now().isoformat(),
            "total_records": len(records),
            "records": records
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(structured, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved JSON to: {json_path}")
        return json_path
    
    def get_stats(self) -> Dict:
        """Get formatter statistics."""
        return {
            "records_written": self.records_written,
            "output_path": self.output_path
        }


def format_and_save(records: List[Dict], output_path: str = None) -> str:
    """
    Convenience function to format and save records.
    
    Args:
        records: List of extraction records
        output_path: Path to output file
        
    Returns:
        Path to output file
    """
    formatter = ADNICFormatter(output_path)
    return formatter.write_records(records)
