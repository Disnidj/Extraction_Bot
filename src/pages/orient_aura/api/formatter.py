"""  
Orient Aura Benefits Formatter
Converts JSON extraction results to database-compatible format.

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
from src.utils.logger import orient_aura_logger
from .mapping import PORTAL_REGION


# Default Broker ID - placeholder (will be overwritten during upload)
DEFAULT_BROKER_ID = 0


class OrientAuraFormatter:
    """Formats Orient Aura benefits JSON to database-compatible format."""
    
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
        self.company_name = "Orient Aura"
    
    def load_from_file(self, json_file_path: str):
        """
        Load extraction results from JSON file.
        
        Args:
            json_file_path: Path to JSON file
        """
        with open(json_file_path, "r", encoding="utf-8") as f:
            self.results = json.load(f)
        orient_aura_logger.debug(f"Loaded results from {json_file_path}")
    
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
        
        orient_aura_logger.info("Starting Orient Aura data formatting...")
        self.output_lines = []
        
        # Collect unique TPAs and Networks for dropdown records
        all_tpas = set()  # {combined_tpa_name}
        tpa_networks = {}  # {combined_tpa_name: set(network_names)}
        
        # Pre-Level: Process Industry Categories (Business Nature)
        industry_categories = self.results.get("industry_categories", [])
        if industry_categories:
            orient_aura_logger.info(f"Processing Industry Categories: {len(industry_categories)} values")
            self._add_rows(
                tpa="",  # No TPA context for pre-level
                network="",  # No Network context for pre-level
                region=PORTAL_REGION,  # Default Region for pre-level
                dropdown_name="Industry Categories",
                values=industry_categories
            )
            orient_aura_logger.debug(f"Added {len(industry_categories)} Industry Category records")
        
        # Iterate through the hierarchy: groups → emirates → tpas → plans → benefits
        orient_aura_logger.info("Processing hierarchy: Groups → Emirates → TPAs → Plans → Benefits")
        
        group_count = 0
        emirate_count = 0
        tpa_count = 0
        plan_count = 0
        
        for group_name, group_data in self.results.get("groups", {}).items():
            group_count += 1
            orient_aura_logger.debug(f"Processing Group: {group_name}")
            
            for emirate_name, emirate_data in group_data.get("emirates", {}).items():
                emirate_count += 1
                orient_aura_logger.debug(f"  Processing Emirate: {emirate_name}")
                
                for tpa_name, tpa_data in emirate_data.get("tpas", {}).items():
                    tpa_count += 1
                    # Combine Group Name with TPA Name (e.g., "Nextcare Sme - Nextcare")
                    combined_tpa = f"{group_name} - {tpa_name}" if tpa_name else ""
                    orient_aura_logger.debug(f"    Processing TPA: {combined_tpa}")
                    
                    # Collect TPA for dropdown records
                    all_tpas.add(combined_tpa)
                    if combined_tpa not in tpa_networks:
                        tpa_networks[combined_tpa] = set()
                    
                    for plan_name, plan_data in tpa_data.get("plans", {}).items():
                        plan_count += 1
                        benefit_count = len(plan_data.get("benefits", {}))
                        orient_aura_logger.debug(f"      Processing Plan: {plan_name} ({benefit_count} benefits)")
                        
                        # Collect Network (Plan) for dropdown records
                        tpa_networks[combined_tpa].add(plan_name)
                        
                        self._process_plan_benefits(
                            tpa_name=combined_tpa,  # Combined format: "Nextcare Sme - Nextcare"
                            plan_name=plan_name,
                            benefits=plan_data.get("benefits", {}),
                            region=emirate_name
                        )
        
        # ════════════════════════════════════════════════════════════════
        # Add TPA dropdown records (Dropdown_Name = "TPA")
        # ════════════════════════════════════════════════════════════════
        if all_tpas:
            orient_aura_logger.info(f"Adding TPA dropdown records: {len(all_tpas)} unique TPAs")
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
            orient_aura_logger.info(f"Adding Network dropdown records: {len(all_networks)} unique networks")
            self._add_rows(
                tpa="",
                network="",
                region=PORTAL_REGION,
                dropdown_name="Network",
                values=list(all_networks)
            )
        
        orient_aura_logger.info(f"Formatting complete: {len(self.output_lines)} total records")
        orient_aura_logger.info(f"  Groups: {group_count}, Emirates: {emirate_count}, TPAs: {tpa_count}, Plans: {plan_count}")
        
        return self.output_lines
    
    def _process_plan_benefits(self, tpa_name: str, plan_name: str, benefits: dict, region: str):
        """
        Process benefits for a single plan.
        
        Args:
            tpa_name: TPA name (e.g., "Nextcare")
            plan_name: Plan/Network name (e.g., "Plan1 GN+")
            benefits: Benefits dict keyed by benefit header ID
            region: Region/Emirate name (e.g., "Dubai")
        """
        for benefit_header_id, benefit_options in benefits.items():
            if not isinstance(benefit_options, list):
                continue
            
            # Extract benefit name from first option
            if not benefit_options:
                continue
            
            benefit_name = benefit_options[0].get("benefits_name", "Unknown")
            
            # Collect all unique option values
            option_values = []
            for option in benefit_options:
                value = option.get("benefits_options", "").strip()
                if value and value not in option_values:
                    option_values.append(value)
            
            if option_values:
                self._add_rows(
                    tpa=tpa_name,
                    network=plan_name,
                    region=region,
                    dropdown_name=benefit_name,
                    values=option_values
                )
    
    def _add_rows(self, tpa: str, network: str, region: str, dropdown_name: str, values: list):
        """
        Add rows to output for a single dropdown field.
        Creates one row per value.
        
        Args:
            tpa: TPA name (empty string for TPA-independent fields)
            network: Network/Plan name (empty string for network-independent fields)
            region: Region name
            dropdown_name: Name of the dropdown field
            values: List of dropdown values
        """
        for value in values:
            row = {
                "Broker_ID": self.broker_id,
                "Company": self.company_name,
                "TPA": tpa,
                "Network": network,
                "Region": region,
                "Dropdown_Name": dropdown_name,
                "Selection_Value": value
            }
            self.output_lines.append(row)
    
    def format_and_save(self, output_dir: str = "extracted_data") -> str:
        """
        Format results and save to text file.
        
        Args:
            output_dir: Base directory to save file
            
        Returns:
            str: Path to saved file
        """
        # Format the data
        formatted_lines = self.format_to_text()
        
        # Save to portal-specific subfolder
        portal_dir = os.path.join(output_dir, "orient_aura")
        os.makedirs(portal_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"orient_aura_extracted_{timestamp}.txt")
        
        # Apply TPA/Network expansion for records with empty TPA/Network
        # This expands pre-level fields to all TPA/Network combinations
        expanded_lines = expand_empty_tpa_network(formatted_lines)
        
        # Write to file (one JSON object per line)
        with open(output_file, "w", encoding="utf-8") as f:
            for line in expanded_lines:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
        
        print(f"\n💾 Formatted text file saved to {output_file}")
        orient_aura_logger.info(f"Formatted output saved to {output_file}")
        orient_aura_logger.info(f"Total records after expansion: {len(expanded_lines)}")
        
        return output_file
    
    def print_summary(self):
        """Print formatting summary."""
        if not self.output_lines:
            print("   No records formatted")
            return
        
        print("\n" + "=" * 60)
        print("📝 FORMATTING SUMMARY")
        print("=" * 60)
        
        # Count unique dropdowns
        unique_dropdowns = set(line["Dropdown_Name"] for line in self.output_lines)
        
        # Count by TPA
        tpa_counts = {}
        for line in self.output_lines:
            tpa = line["TPA"] or "(No TPA)"
            tpa_counts[tpa] = tpa_counts.get(tpa, 0) + 1
        
        print(f"   Total records: {len(self.output_lines)}")
        print(f"   Unique dropdowns: {len(unique_dropdowns)}")
        print(f"   TPAs found: {len([k for k in tpa_counts.keys() if k != '(No TPA)'])}")
        
        print("\n   Records by TPA:")
        for tpa, count in sorted(tpa_counts.items()):
            print(f"      {tpa}: {count} records")
        
        print("=" * 60)
