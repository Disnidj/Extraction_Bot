"""  
MaxHealth Benefits Formatter
Converts JSON extraction results to database-compatible format.

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Company, TPA, Network, Region, Dropdown_Name, Selection_Value

Database Schema Reference:
{
    "CTN_ID": auto-generated,
    "Company": "MaxHealth",
    "TPA": "NAS",
    "Network": "MAXMED - NAS",
    "Region": "Dubai",
    "Dropdown_Name": "Plan",
    "Selection_Value": "MAXMED BRONZE GROUP_NAS"
}

Business Rules Applied:
- Location locked to Dubai
- Policy Holder Types filtered per TPA+Network combination
- Plans from DHA (Dubai Health Authority) only

TPA/Network Expansion:
- Uses shared expansion service from src.services.formatter_service
- Records with empty TPA/Network are expanded to all TPA/Network combinations
"""

import json
import os
from datetime import datetime
from src.services.formatter_service import expand_empty_tpa_network
from src.utils.logger import maxhealth_logger


class MaxHealthFormatter:
    """Formats MaxHealth extraction results to database-compatible format."""
    
    def __init__(self, results: dict = None):
        """
        Initialize formatter.
        
        Args:
            results: Extraction results dict (optional, can load from file)
        """
        self.results = results
        self.output_lines = []
        self.company_name = "MaxHealth"
    
    def load_from_file(self, json_file_path: str):
        """
        Load extraction results from JSON file.
        
        Args:
            json_file_path: Path to JSON file
        """
        with open(json_file_path, "r", encoding="utf-8") as f:
            self.results = json.load(f)
        maxhealth_logger.debug(f"Loaded results from {json_file_path}")
    
    def format_to_text(self) -> list:
        """
        Convert JSON results to database-compatible format.
        
        Each row has full context: TPA, Network, Region all populated.
        Output per TPA+Network+Region combination:
        - Location, Quotation For, Policy Holder Type, Plan
        
        Returns:
            list: List of formatted lines (one per Selection_Value)
        """
        if not self.results:
            raise ValueError("No results to format. Load or provide results first.")
        
        maxhealth_logger.info("Starting MaxHealth data formatting...")
        self.output_lines = []
        lookups = self.results.get("lookups", {})
        plans_by_combo = self.results.get("plans_by_combination", {})
        
        maxhealth_logger.debug(f"Processing {len(plans_by_combo)} TPA+Network combinations")
        
        # Region is always Dubai (filtered during extraction)
        region = "Dubai"
        maxhealth_logger.debug(f"Region: {region} (locked)")
        
        # Get Quotation For values (same for all combinations)
        client_statuses = lookups.get("clientStatuses", [])
        quotation_values = [cs.get("title") for cs in client_statuses if cs.get("title")] if client_statuses else []
        
        maxhealth_logger.debug(f"Quotation For values: {len(quotation_values)} options")
        
        # ===========================================
        # Collect all unique TPAs and Networks for dropdown records
        # These will have empty TPA/Network columns so they get expanded
        # ===========================================
        all_tpas = set()
        all_networks = set()
        
        for combo_data in plans_by_combo.values():
            tpa_name = combo_data.get("network_name", "")
            network_name = combo_data.get("product_name", "")
            if tpa_name:
                all_tpas.add(tpa_name)
            if network_name:
                all_networks.add(network_name)
        
        # Add TPA dropdown with empty TPA/Network so it gets expanded
        if all_tpas:
            self._add_rows("", "", region, "TPA", list(all_tpas))
            maxhealth_logger.debug(f"Added TPA dropdown: {len(all_tpas)} unique TPAs")
        
        # Add Network dropdown with empty TPA/Network so it gets expanded
        if all_networks:
            self._add_rows("", "", region, "Network", list(all_networks))
            maxhealth_logger.debug(f"Added Network dropdown: {len(all_networks)} unique Networks")
        
        # ===========================================
        # Output per TPA+Network+Region (all context filled)
        # ===========================================
        combo_count = 0
        for combo_key, combo_data in plans_by_combo.items():
            combo_count += 1
            tpa_name = combo_data.get("network_name", "")
            network_name = combo_data.get("product_name", "")
            valid_target_groups = combo_data.get("valid_target_groups", [])
            
            maxhealth_logger.debug(f"Processing combo {combo_count}: TPA={tpa_name}, Network={network_name}")
            maxhealth_logger.debug(f"  Valid target groups: {len(valid_target_groups)} options")
            plans = combo_data.get("plans", [])
            
            # Quotation For
            if quotation_values:
                self._add_rows(tpa_name, network_name, region, "Quotation For", quotation_values)
            
            # Policy Holder Type for this combination
            if valid_target_groups:
                target_group_names = [tg.get("name") for tg in valid_target_groups if tg.get("name")]
                self._add_rows(tpa_name, network_name, region, "Policy Holder Type", target_group_names)
            
            # Plans for this combination
            if plans:
                plan_values = [p.get("title") if isinstance(p, dict) else p for p in plans]
                self._add_rows(tpa_name, network_name, region, "Plan", plan_values)
        
        return self.output_lines
    
    def _add_rows(self, tpa: str, network: str, region: str, 
                  dropdown_name: str, values: list):
        """
        Add formatted rows to output (one row per value).
        
        Database format:
        {"Company": "MaxHealth", "TPA": "NAS", "Network": "MAXMED", 
         "Region": "Dubai", "Dropdown_Name": "Plan", "Selection_Value": "Bronze"}
        
        Args:
            tpa: TPA name (empty string if not applicable)
            network: Network name (empty string if not applicable)
            region: Region name
            dropdown_name: Name of the dropdown field
            values: List of option values
        """
        if not values:
            return
        
        for value in values:
            if not value:
                continue
                
            row = {
                "Company": self.company_name,
                "TPA": tpa,
                "Network": network,
                "Region": region,
                "Dropdown_Name": dropdown_name,
                "Selection_Value": value
            }
            
            self.output_lines.append(json.dumps(row, ensure_ascii=False))
    
    def save_to_file(self, output_dir: str = "extracted_data") -> str:
        """
        Save formatted output to text file.
        Expands records with empty TPA/Network to all combinations.
        
        Args:
            output_dir: Base directory to save file
            
        Returns:
            str: Path to saved file
        """
        if not self.output_lines:
            raise ValueError("No formatted output. Run format_to_text first.")
        
        # Parse JSON lines back to dicts for expansion
        parsed_records = [json.loads(line) for line in self.output_lines]
        
        # Expand records with empty TPA/Network using shared service
        expanded_records = expand_empty_tpa_network(parsed_records)
        
        portal_dir = os.path.join(output_dir, "maxhealth")
        os.makedirs(portal_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"maxhealth_extracted_{timestamp}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            for record in expanded_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        print(f"\n💾 Saved {len(expanded_records)} database rows to: {output_file}")
        maxhealth_logger.debug(f"Saved {len(expanded_records)} rows to {output_file}")
        return output_file
    
    def format_and_save(self, output_dir: str = "extracted_data") -> str:
        """
        Format results and save to file in one step.
        
        Args:
            output_dir: Directory to save file
            
        Returns:
            str: Path to saved file
        """
        self.format_to_text()
        return self.save_to_file(output_dir)
    
    def print_summary(self):
        """Print formatting summary."""
        print(f"\n📊 Formatted {len(self.output_lines)} database rows")
        
        # Count by dropdown name
        dropdown_counts = {}
        for line in self.output_lines:
            try:
                data = json.loads(line)
                dropdown = data.get("Dropdown_Name", "Unknown")
                dropdown_counts[dropdown] = dropdown_counts.get(dropdown, 0) + 1
            except:
                pass
        
        if dropdown_counts:
            print("   Breakdown by Dropdown:")
            for dropdown, count in dropdown_counts.items():
                print(f"     • {dropdown}: {count} rows")
