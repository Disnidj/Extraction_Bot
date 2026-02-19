"""  
Takaful Benefits Formatter
Converts JSON extraction results to database-compatible format.
Updated to follow Orient Aura/Qatar pattern with groups → emirates → tpas → plans.

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value

TPA/Network Expansion:
- Uses shared expansion service from src.services.formatter_service
- Records with empty TPA/Network are expanded to all TPA/Network combinations
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from src.services.formatter_service import expand_empty_tpa_network
from src.utils.logger import takaful_logger
from .mapping import PORTAL_REGION


# Default Broker ID - can be configured
DEFAULT_BROKER_ID = 3


class TakafulFormatter:
    """Formats Takaful benefits JSON to database-compatible format."""
    
    def __init__(self, results: dict = None, broker_id: int = DEFAULT_BROKER_ID):
        """
        Initialize formatter.
        
        Args:
            results: Extraction results dict (optional, can load from file)
            broker_id: Broker ID for database records
        """
        self.results = results
        self.broker_id = broker_id
        self.output_lines = []
        self.company_name = "Takaful"
    
    def load_from_file(self, json_file_path: str):
        """
        Load extraction results from JSON file.
        
        Args:
            json_file_path: Path to JSON file
        """
        with open(json_file_path, "r", encoding="utf-8") as f:
            self.results = json.load(f)
        takaful_logger.debug(f"Loaded results from {json_file_path}")
    
    def format_to_text(self) -> list:
        """
        Convert JSON results to database-compatible format.
        Each line is a JSON object with:
        - Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value
        
        Returns:
            list: List of formatted lines (one per Selection_Value)
        """
        if not self.results:
            raise ValueError("No results to format. Load or provide results first.")
        
        takaful_logger.info("Starting Takaful data formatting...")
        self.output_lines = []
        
        # Collect unique TPAs and Networks for dropdown records
        all_tpas = set()  # {tpa_name}
        tpa_networks = {}  # {tpa_name: set(network_names)}
        
        # Pre-Level: Process Industry Categories (Business Nature)
        industry_categories = self.results.get("industry_categories", [])
        if industry_categories:
            takaful_logger.info(f"Processing Industry Categories: {len(industry_categories)} values")
            self._add_rows(
                tpa="",  # No TPA context for pre-level
                network="",  # No Network context for pre-level
                region=PORTAL_REGION,  # Default Region for pre-level
                dropdown_name="Industry Categories",
                values=industry_categories
            )
            takaful_logger.debug(f"Added {len(industry_categories)} Industry Category records")
        
        # Iterate through the hierarchy: groups → emirates → tpas → plans → benefits
        takaful_logger.info("Processing hierarchy: Groups → Emirates → TPAs → Plans → Benefits")
        
        group_count = 0
        emirate_count = 0
        tpa_count = 0
        plan_count = 0
        
        groups = self.results.get("groups", {})
        
        for group_name, group_data in groups.items():
            group_count += 1
            takaful_logger.debug(f"Processing Group: {group_name}")
            
            for emirate_name, emirate_data in group_data.get("emirates", {}).items():
                emirate_count += 1
                takaful_logger.debug(f"  Processing Emirate: {emirate_name}")
                
                for tpa_name, tpa_data in emirate_data.get("tpas", {}).items():
                    tpa_count += 1
                    takaful_logger.debug(f"    Processing TPA: {tpa_name}")
                    
                    # Collect TPA for dropdown records
                    all_tpas.add(tpa_name)
                    if tpa_name not in tpa_networks:
                        tpa_networks[tpa_name] = set()
                    
                    for plan_name, plan_data in tpa_data.get("plans", {}).items():
                        plan_count += 1
                        benefit_count = len(plan_data.get("benefits", {}))
                        takaful_logger.debug(f"      Processing Plan: {plan_name} ({benefit_count} benefits)")
                        
                        # Collect Network (Plan) for dropdown records
                        tpa_networks[tpa_name].add(plan_name)
                        
                        self._process_plan_benefits(
                            region=emirate_name,
                            tpa=tpa_name,
                            network=plan_name,
                            benefits=plan_data.get("benefits", {})
                        )
        
        # ════════════════════════════════════════════════════════════════
        # Add TPA dropdown records (Dropdown_Name = "TPA")
        # ════════════════════════════════════════════════════════════════
        if all_tpas:
            takaful_logger.info(f"Adding TPA dropdown records: {len(all_tpas)} unique TPAs")
            self._add_rows(
                tpa="",
                network="",
                region=PORTAL_REGION,
                dropdown_name="TPA",
                values=list(all_tpas)
            )
        
        # ════════════════════════════════════════════════════════════════
        # Add Network dropdown records (Dropdown_Name = "Network")
        # Collect ALL unique networks and add with empty TPA/Network
        # so they get expanded to all TPA/Network combinations
        # ════════════════════════════════════════════════════════════════
        all_networks = set()
        for networks in tpa_networks.values():
            all_networks.update(networks)
        
        if all_networks:
            takaful_logger.info(f"Adding Network dropdown records: {len(all_networks)} unique networks")
            self._add_rows(
                tpa="",
                network="",
                region=PORTAL_REGION,
                dropdown_name="Network",
                values=list(all_networks)
            )
        
        takaful_logger.info(f"Formatting complete: {group_count} Groups, {emirate_count} Emirates, {tpa_count} TPAs, {plan_count} Plans")
        takaful_logger.info(f"Total records before expansion: {len(self.output_lines)}")
        
        return self.output_lines
    
    def _process_plan_benefits(self, region: str, tpa: str, 
                                network: str, benefits: dict):
        """
        Process all benefits for a single plan and add to output lines.
        
        Args:
            region: Region/Emirate name
            tpa: TPA name
            network: Plan/Network name
            benefits: Benefits dict with benefit_id -> list of options
        """
        # Group benefits by field name to handle duplicates
        processed_fields = {}
        
        for benefit_id, options_list in benefits.items():
            if not options_list:
                continue
            
            # Get field name from first option
            first_option = options_list[0]
            field_name = first_option.get("benefits_name", "")
            
            if not field_name:
                continue
            
            # Extract all values (options) for this field
            values = []
            for option in options_list:
                option_value = option.get("benefits_options", "")
                if option_value and option_value not in values:
                    values.append(option_value)
            
            if not values:
                continue
            
            # Create unique key for this field
            field_key = field_name
            
            # If we've seen this field before for this plan, merge values
            if field_key in processed_fields:
                for v in values:
                    if v not in processed_fields[field_key]:
                        processed_fields[field_key].append(v)
            else:
                processed_fields[field_key] = values
        
        # Output each unique field - one row per value (database format)
        for field_name, values in processed_fields.items():
            self._add_rows(tpa, network, region, field_name, values)
    
    def _add_rows(self, tpa: str, network: str, region: str,
                  dropdown_name: str, values: list):
        """
        Add formatted rows to output (one row per value).
        
        Database format:
        {"Broker_ID": 3, "Company": "Takaful", "TPA": "...", "Network": "...",
         "Region": "...", "Dropdown_Name": "...", "Selection_Value": "..."}
        
        Args:
            tpa: TPA name
            network: Network name
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
                "Broker_ID": self.broker_id,
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
        
        takaful_logger.info(f"Saving formatted data: {len(self.output_lines)} records before expansion")
        
        # Parse JSON lines back to dicts for expansion
        parsed_records = [json.loads(line) for line in self.output_lines]
        
        takaful_logger.debug("Expanding empty TPA/Network combinations...")
        # Expand records with empty TPA/Network using shared service
        expanded_records = expand_empty_tpa_network(parsed_records)
        
        takaful_logger.info(f"After expansion: {len(expanded_records)} total records")
        
        # Save to portal-specific subfolder
        portal_dir = os.path.join(output_dir, "takaful")
        os.makedirs(portal_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"takaful_extracted_{timestamp}.txt")
        
        takaful_logger.debug(f"Output file: {output_file}")
        
        with open(output_file, "w", encoding="utf-8") as f:
            for record in expanded_records:
                # Use ensure_ascii=True to avoid Unicode encoding issues
                f.write(json.dumps(record, ensure_ascii=True) + "\n")
        
        takaful_logger.info(f"Successfully saved {len(expanded_records)} records to {output_file}")
        print(f"Saved {len(expanded_records)} database rows to: {output_file}")
        
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
        print(f"\n📊 FORMATTING SUMMARY")
        print(f"   Total database rows: {len(self.output_lines)}")
        
        # Count by dropdown name
        dropdown_counts = {}
        for line in self.output_lines:
            try:
                data = json.loads(line)
                dropdown = data.get("Dropdown_Name", "Unknown")
                dropdown_counts[dropdown] = dropdown_counts.get(dropdown, 0) + 1
            except:
                pass
        
        for dropdown, count in sorted(dropdown_counts.items()):
            print(f"   {dropdown}: {count} values")


def format_json_file(json_file_path: str, output_dir: str = "extracted_data") -> str:
    """
    Standalone function to format a JSON file to text.
    
    Args:
        json_file_path: Path to JSON file
        output_dir: Directory to save output
        
    Returns:
        str: Path to saved file
    """
    formatter = TakafulFormatter()
    formatter.load_from_file(json_file_path)
    formatter.format_to_text()
    formatter.print_summary()
    return formatter.save_to_file(output_dir)


# Allow running this file directly to format existing JSON
if __name__ == "__main__":
    import glob
    
    # Find the most recent JSON file
    json_files = glob.glob("extracted_data/takaful_benefits_*.json")
    if json_files:
        latest_file = max(json_files, key=os.path.getmtime)
        print(f"\n📂 Formatting: {latest_file}")
        output_file = format_json_file(latest_file)
        print(f"\n✅ Done! Output: {output_file}")
    else:
        print("❌ No takaful_benefits_*.json files found in extracted_data/")
