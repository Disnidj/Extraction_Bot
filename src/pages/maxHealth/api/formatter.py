"""
MaxHealth Benefits Formatter
Converts JSON extraction results to formatted text file.

Output Format matches ADNIC style:
- Standalone fields first (no TPA/Network context)
- Then TPA-specific Network options
- Then for each TPA + Network combination, show Policy Holder Type
- Then for each TPA + Network + Policy Holder Type, show Plans

Each row maintains the "current state" (selected parent values) like ADNIC output:
- Plans include "Policy Holder Type": "<selected value>" to show parent context

Business Rules Applied:
- Location locked to Dubai
- Policy Holder Types filtered per TPA+Network combination
- Plans from DHA (Dubai Health Authority) only
"""

import json
import os
from datetime import datetime
from src.utils.logger import maxhealth_logger


class MaxHealthFormatter:
    """Formats MaxHealth extraction results to text format."""
    
    def __init__(self, results: dict = None):
        """
        Initialize formatter.
        
        Args:
            results: Extraction results dict (optional, can load from file)
        """
        self.results = results
        self.output_lines = []
    
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
        Convert JSON results to text format matching ADNIC style.
        
        Each row maintains the hierarchical state (selected parent values).
        For Plans, includes which Policy Holder Type was selected.
        
        Returns:
            list: List of formatted lines
        """
        if not self.results:
            raise ValueError("No results to format. Load or provide results first.")
        
        self.output_lines = []
        portal = self.results.get("portal", "MaxHealth")
        lookups = self.results.get("lookups", {})
        plans_by_combo = self.results.get("plans_by_combination", {})
        
        # Step 1: Standalone fields (no TPA/Network context)
        # TPA dropdown
        networks = lookups.get("networks", [])
        if networks:
            self._add_line(portal, "", "", "", "TPA", 
                          [n.get("title") for n in networks if n.get("title")])
        
        # Location (filtered to Dubai only)
        self._add_line(portal, "", "", "", "Location", ["Dubai"])
        
        # Quotation For (all options)
        client_statuses = lookups.get("clientStatuses", [])
        if client_statuses:
            self._add_line(portal, "", "", "", "Quotation For",
                          [cs.get("title") for cs in client_statuses if cs.get("title")])
        
        # Step 2: For each TPA, show available Networks
        # Group products by their network (TPA)
        tpa_to_networks = {}
        for combo_key, combo_data in plans_by_combo.items():
            tpa_name = combo_data.get("network_name", "")
            network_name = combo_data.get("product_name", "")
            if tpa_name not in tpa_to_networks:
                tpa_to_networks[tpa_name] = []
            if network_name not in tpa_to_networks[tpa_name]:
                tpa_to_networks[tpa_name].append(network_name)
        
        for tpa_name, network_list in tpa_to_networks.items():
            self._add_line(portal, tpa_name, "", "", "Network", network_list)
        
        # Step 3: For each TPA + Network, show Policy Holder Type
        for combo_key, combo_data in plans_by_combo.items():
            tpa_name = combo_data.get("network_name", "")
            network_name = combo_data.get("product_name", "")
            valid_target_groups = combo_data.get("valid_target_groups", [])
            plans = combo_data.get("plans", [])
            
            # Policy Holder Type for this combination
            if valid_target_groups:
                target_group_names = [tg.get("name") for tg in valid_target_groups if tg.get("name")]
                self._add_line(portal, tpa_name, "", network_name, "Policy Holder Type", target_group_names)
            
            # Step 4: For each Policy Holder Type, show Plans with parent context
            # This matches ADNIC format where each child row includes parent selection
            if plans and valid_target_groups:
                plan_values = [p.get("title") if isinstance(p, dict) else p for p in plans]
                
                for target_group in valid_target_groups:
                    tg_name = target_group.get("name", "")
                    if tg_name:
                        # Add Plan row with Policy Holder Type context
                        self._add_line(
                            portal, tpa_name, "", network_name, "Plan", plan_values,
                            extra_context={"Policy Holder Type": tg_name}
                        )
        
        return self.output_lines
    
    def _add_line(self, portal: str, tpa: str, region: str, network: str, 
                  field_name: str, values: list, extra_context: dict = None):
        """
        Add a formatted line to output.
        
        Args:
            portal: Portal name
            tpa: TPA name (empty string if not applicable)
            region: Region name (empty string if not applicable)
            network: Network name (empty string if not applicable)
            field_name: Name of the dropdown field
            values: List of option values
            extra_context: Additional context fields to include (parent selections)
        """
        if not values:
            return
        
        line_data = {
            "data": {
                "Portal": portal,
                "TPA": tpa,
                "Region": region,
                "Network": network,
                "field name": field_name,
                "values": [v for v in values if v]
            }
        }
        
        # Add any extra context (like parent selection values)
        if extra_context:
            line_data["data"].update(extra_context)
        
        self.output_lines.append(json.dumps(line_data, ensure_ascii=False))
    
    def save_to_file(self, output_dir: str = "extracted_data") -> str:
        """
        Save formatted output to text file.
        
        Args:
            output_dir: Base directory to save file
            
        Returns:
            str: Path to saved file
        """
        if not self.output_lines:
            raise ValueError("No formatted output. Run format_to_text first.")
        
        portal_dir = os.path.join(output_dir, "maxhealth")
        os.makedirs(portal_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"maxhealth_extracted_{timestamp}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            for line in self.output_lines:
                f.write(line + "\n")
        
        print(f"📄 Formatted output saved to {output_file}")
        maxhealth_logger.debug(f"Formatted output saved to {output_file}")
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
        print(f"\n📊 Formatted {len(self.output_lines)} dropdown fields")
