"""
NLGI Aura Data Formatter
Converts API responses to database format (matches Orient Aura/Qatar pattern exactly)

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Company, TPA, Network, Region, Dropdown_Name, Selection_Value
- Network = Plan name (NOT TPA name!)

TPA/Network Expansion:
- Uses shared expansion service from src.services.formatter_service
- Records with empty TPA/Network are expanded to all TPA/Network combinations
"""

import json
import os
from typing import Dict, List
from datetime import datetime
from src.services.formatter_service import expand_empty_tpa_network
from src.utils.logger import nlgi_aura_logger
from .mapping import NLGI_MAPPING, PORTAL_REGION

# Get group name for TPA prefix
GROUP_NAME = NLGI_MAPPING["group"]["group_name"]


class NLGIAuraFormatter:
    """Formats NLGI Aura API data for database insertion"""
    
    def __init__(self, results: dict = None):
        """
        Initialize formatter.
        
        Args:
            results: Extraction results dict (optional)
        """
        self.results = results
        self.company = "NLGI Aura"
        self.output_lines = []
    
    def format_to_text(self) -> List[Dict]:
        """
        Convert JSON results to database-compatible format.
        Matches Orient Aura/Qatar hierarchical pattern.
        
        Returns:
            List of formatted records
        """
        if not self.results:
            raise ValueError("No results to format")
        
        nlgi_aura_logger.info("Starting NLGI Aura data formatting...")
        self.output_lines = []
        
        # Collect unique TPAs and Networks for dropdown records
        all_tpas = set()  # {combined_tpa_name}
        tpa_networks = {}  # {combined_tpa_name: set(network_names)}
        
        # Pre-Level: Process Industry Categories (Business Nature)
        industries = self.results.get("industry_categories", [])
        if industries:
            nlgi_aura_logger.info(f"Processing Industry Categories: {len(industries)} values")
            self._add_rows(
                tpa="",  # No TPA for pre-level
                network="",  # No Network for pre-level
                region=PORTAL_REGION,
                dropdown_name="Industry Categories",
                values=industries
            )
            nlgi_aura_logger.debug(f"Added {len(industries)} Industry Category records")
        
        # Process hierarchical data: Groups → Emirates → TPAs → Plans → Benefits
        groups = self.results.get("groups", {})
        nlgi_aura_logger.info(f"Processing {len(groups)} groups")
        
        for group_name, group_data in groups.items():
            emirates = group_data.get("emirates", {})
            
            for emirate_name, emirate_data in emirates.items():
                tpas = emirate_data.get("tpas", {})
                
                for tpa_name, tpa_data in tpas.items():
                    # Combine Group Name with TPA Name (e.g., "GlobalCare SME - NAS")
                    combined_tpa = f"{group_name} - {tpa_name}"
                    
                    # Collect TPA for dropdown records
                    all_tpas.add(combined_tpa)
                    if combined_tpa not in tpa_networks:
                        tpa_networks[combined_tpa] = set()
                    
                    plans = tpa_data.get("plans", {})
                    
                    for plan_name, plan_data in plans.items():
                        benefits = plan_data.get("benefits", {})
                        
                        # Collect Network (Plan) for dropdown records
                        tpa_networks[combined_tpa].add(plan_name)
                        
                        self._process_plan_benefits(
                            tpa_name=combined_tpa,  # Combined format
                            plan_name=plan_name,  # Network = Plan name!
                            benefits=benefits,
                            region=emirate_name
                        )
        
        # ════════════════════════════════════════════════════════════════
        # Add TPA dropdown records (Dropdown_Name = "TPA")
        # ════════════════════════════════════════════════════════════════
        if all_tpas:
            nlgi_aura_logger.info(f"Adding TPA dropdown records: {len(all_tpas)} unique TPAs")
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
            nlgi_aura_logger.info(f"Adding Network dropdown records: {len(all_networks)} unique networks")
            self._add_rows(
                tpa="",
                network="",
                region=PORTAL_REGION,
                dropdown_name="Network",
                values=list(all_networks)
            )
        
        nlgi_aura_logger.info(f"Formatting complete: {len(self.output_lines)} total records")
        return self.output_lines
    
    def _process_plan_benefits(self, tpa_name: str, plan_name: str, benefits: Dict, region: str):
        """
        Process benefits for a single plan.
        Matches Orient Aura/Qatar pattern exactly.
        
        Args:
            tpa_name: Combined TPA name (e.g., "GlobalCare SME - NAS")
            plan_name: Plan/Network name (e.g., "Plan A - WW") - THIS IS THE NETWORK!
            benefits: Benefits dict keyed by benefit header ID
            region: Region/Emirate name (e.g., "Dubai")
        """
        for benefit_header_id, benefit_options in benefits.items():
            if not isinstance(benefit_options, list):
                continue
            
            if not benefit_options:
                continue
            
            # Extract benefit name from first option
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
                    network=plan_name,  # Use plan_name for Network field!
                    region=region,
                    dropdown_name=benefit_name,
                    values=option_values
                )
    
    def _add_rows(self, tpa: str, network: str, region: str, dropdown_name: str, values: List):
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
                "Company": self.company,
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
        portal_dir = os.path.join(output_dir, "nlgi_aura")
        os.makedirs(portal_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"nlgi_aura_extracted_{timestamp}.txt")
        
        # Apply TPA/Network expansion for records with empty TPA/Network
        # This expands pre-level fields (Industry Categories) to all TPA/Network combinations
        expanded_lines = expand_empty_tpa_network(formatted_lines)
        
        # Write to file (one JSON object per line)
        with open(output_file, "w", encoding="utf-8") as f:
            for line in expanded_lines:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
        
        print(f"\n💾 Formatted text file saved to {output_file}")
        nlgi_aura_logger.info(f"Formatted output saved to {output_file}")
        nlgi_aura_logger.info(f"Total records after expansion: {len(expanded_lines)}")
        
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
