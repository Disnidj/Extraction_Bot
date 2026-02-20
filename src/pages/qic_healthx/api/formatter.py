"""
QIC HealthX Data Formatter
Converts API responses to database format.

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value

TPA: NAS (all plans use NAS network)
Network: Plan name without region suffix (e.g., "GN", "RN", "SRN")
Region: Dubai
"""

import json
import os
from typing import Dict, List
from datetime import datetime
from src.utils.logger import qic_healthx_logger
from .mapping import PORTAL_NAME, PORTAL_REGION, TPA_NAME


# Default Broker ID
DEFAULT_BROKER_ID = 3


class QICHealthXFormatter:
    """Formats QIC HealthX API data for database insertion"""
    
    def __init__(self, results: dict = None, broker_id: int = DEFAULT_BROKER_ID):
        """
        Initialize formatter.
        
        Args:
            results: Extraction results dict (optional)
            broker_id: Broker ID for database records
        """
        self.results = results
        self.broker_id = broker_id
        self.company = PORTAL_NAME
        self.output_lines = []
    
    def format_to_text(self) -> List[Dict]:
        """
        Convert JSON results to database-compatible format.
        
        Returns:
            List of formatted records
        """
        if not self.results:
            raise ValueError("No results to format")
        
        qic_healthx_logger.info("Starting QIC HealthX data formatting...")
        self.output_lines = []
        
        # Collect unique networks for dropdown records
        all_networks = set()
        
        # Process each plan's benefits
        plans = self.results.get("plans", {})
        qic_healthx_logger.info(f"Processing {len(plans)} plans")
        
        for plan_name, plan_data in plans.items():
            # Extract network from plan name (e.g., "GN Dubai" -> "GN")
            network = self._extract_network_from_plan(plan_name)
            all_networks.add(network)
            
            benefits = plan_data.get("benefits", {})
            
            for dropdown_name, values in benefits.items():
                self._add_rows(
                    tpa=TPA_NAME,
                    network=network,
                    region=PORTAL_REGION,
                    dropdown_name=dropdown_name,
                    values=values
                )
        
        # ════════════════════════════════════════════════════════════════
        # Add TPA dropdown record
        # ════════════════════════════════════════════════════════════════
        qic_healthx_logger.info("Adding TPA dropdown record")
        self._add_rows(
            tpa="",
            network="",
            region=PORTAL_REGION,
            dropdown_name="TPA",
            values=[TPA_NAME]
        )
        
        # ════════════════════════════════════════════════════════════════
        # Add Network dropdown records
        # ════════════════════════════════════════════════════════════════
        if all_networks:
            qic_healthx_logger.info(f"Adding Network dropdown records: {len(all_networks)} networks")
            self._add_rows(
                tpa="",
                network="",
                region=PORTAL_REGION,
                dropdown_name="Network",
                values=list(sorted(all_networks))
            )
        
        qic_healthx_logger.info(f"Formatting complete: {len(self.output_lines)} total records")
        return self.output_lines
    
    def _extract_network_from_plan(self, plan_name: str) -> str:
        """
        Return full plan name as network.
        
        Examples:
            "GN Dubai" -> "GN Dubai"
            "CN Dubai" -> "CN Dubai"
            "RN incl Medcare Group & SGH Dubai" -> "RN incl Medcare Group & SGH Dubai"
            "GN excluding MCG & KCH Dubai" -> "GN excluding MCG & KCH Dubai"
        
        Args:
            plan_name: Full plan name from API
            
        Returns:
            Full plan name as network (matches portal dropdown)
        """
        # Keep full plan name as network (matches portal NAS Network dropdown)
        return plan_name.strip()
    
    def _add_rows(self, tpa: str, network: str, region: str, 
                  dropdown_name: str, values: list):
        """
        Add rows to output - one row per selection value.
        
        Args:
            tpa: TPA name
            network: Network/Plan name
            region: Region name
            dropdown_name: Name of the dropdown field
            values: List of selection values
        """
        for value in values:
            if not value:
                continue
                
            row = {
                "Broker_ID": self.broker_id,
                "Company": self.company,
                "TPA": tpa,
                "Network": network,
                "Region": region,
                "Dropdown_Name": dropdown_name,
                "Selection_Value": value
            }
            self.output_lines.append(row)
    
    def save_to_json(self, output_dir: str, timestamp: str = None) -> str:
        """
        Save formatted data to JSON file.
        
        Args:
            output_dir: Base output directory
            timestamp: Optional timestamp string
            
        Returns:
            str: Path to saved file
        """
        if not self.output_lines:
            self.format_to_text()
        
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        dir_path = os.path.join(output_dir, timestamp, "qic_healthx")
        os.makedirs(dir_path, exist_ok=True)
        
        output_file = os.path.join(dir_path, f"qic_healthx_formatted_{timestamp}.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.output_lines, f, indent=2, ensure_ascii=False)
        
        qic_healthx_logger.info(f"Saved formatted data to: {output_file}")
        print(f"   📄 Formatted JSON saved: {output_file}")
        
        return output_file
    
    def save_to_txt(self, output_dir: str) -> str:
        """
        Save formatted data to JSON lines TXT file (one JSON object per line).
        Matches format used by ADNIC, Orient Aura, and other portals.
        
        Args:
            output_dir: Base output directory
            
        Returns:
            str: Path to saved file
        """
        if not self.output_lines:
            self.format_to_text()
        
        # Save to portal-specific subfolder (matches Orient Aura pattern)
        portal_dir = os.path.join(output_dir, "qic_healthx")
        os.makedirs(portal_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_file = os.path.join(portal_dir, f"qic_healthx_extracted_{timestamp}.txt")
        
        # Write JSON lines format (one JSON object per line)
        with open(output_file, "w", encoding="utf-8") as f:
            for row in self.output_lines:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        
        qic_healthx_logger.info(f"Saved formatted TXT to: {output_file}")
        print(f"   📄 Formatted TXT saved: {output_file}")
        
        return output_file
    
    def get_stats(self) -> dict:
        """
        Get formatting statistics.
        
        Returns:
            dict: Statistics about formatted data
        """
        if not self.output_lines:
            return {}
        
        dropdown_counts = {}
        network_counts = {}
        
        for row in self.output_lines:
            dropdown = row["Dropdown_Name"]
            network = row["Network"]
            
            dropdown_counts[dropdown] = dropdown_counts.get(dropdown, 0) + 1
            if network:
                network_counts[network] = network_counts.get(network, 0) + 1
        
        return {
            "total_records": len(self.output_lines),
            "unique_dropdowns": len(dropdown_counts),
            "unique_networks": len(network_counts),
            "dropdown_counts": dropdown_counts,
            "network_counts": network_counts
        }
    
    def print_summary(self):
        """Print formatting summary to console."""
        if not self.output_lines:
            print("   No records formatted")
            return
        
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("📝 FORMATTING SUMMARY")
        print("=" * 60)
        print(f"   Company: {self.company}")
        print(f"   TPA: {TPA_NAME}")
        print(f"   Region: {PORTAL_REGION}")
        print(f"   Total Records: {stats.get('total_records', 0)}")
        print(f"   Unique Dropdowns: {stats.get('unique_dropdowns', 0)}")
        print(f"   Unique Networks: {stats.get('unique_networks', 0)}")
        
        print("\n   Records by Network:")
        for network, count in sorted(stats.get("network_counts", {}).items()):
            print(f"      {network}: {count} records")
        
        print("\n   Records by Dropdown:")
        for dropdown, count in sorted(stats.get("dropdown_counts", {}).items()):
            print(f"      {dropdown}: {count} records")
        
        print("=" * 60)
