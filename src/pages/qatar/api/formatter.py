"""
Qatar Benefits Formatter
Converts JSON extraction results to database-compatible format.

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value
"""

import json
import os
from datetime import datetime
from src.utils.logger import qatar_logger


# Default Broker ID - can be configured
DEFAULT_BROKER_ID = 3


class QatarFormatter:
    """Formats Qatar benefits JSON to database-compatible format."""
    
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
        self.company_name = "Qatar"
    
    def load_from_file(self, json_file_path: str):
        """
        Load extraction results from JSON file.
        
        Args:
            json_file_path: Path to JSON file
        """
        with open(json_file_path, "r", encoding="utf-8") as f:
            self.results = json.load(f)
        qatar_logger.debug(f"Loaded results from {json_file_path}")
    
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
        
        self.output_lines = []
        
        # Iterate through the hierarchy: emirates -> tpas -> plans -> benefits
        for emirate_name, emirate_data in self.results.get("emirates", {}).items():
            for tpa_name, tpa_data in emirate_data.get("tpas", {}).items():
                for plan_name, plan_data in tpa_data.get("plans", {}).items():
                    self._process_plan_benefits(
                        region=emirate_name,
                        tpa=tpa_name,
                        network=plan_name,
                        benefits=plan_data.get("benefits", {})
                    )
        
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
        {"Broker_ID": 3, "Company": "Qatar", "TPA": "...", "Network": "...",
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
        
        Args:
            output_dir: Base directory to save file
            
        Returns:
            str: Path to saved file
        """
        if not self.output_lines:
            raise ValueError("No formatted output. Run format_to_text first.")
        
        # Save to portal-specific subfolder
        portal_dir = os.path.join(output_dir, "qatar")
        os.makedirs(portal_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"qatar_extracted_{timestamp}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            for line in self.output_lines:
                f.write(line + "\n")
        
        print(f"📄 Formatted output saved to {output_file}")
        qatar_logger.debug(f"Formatted output saved to {output_file}")
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
        
        for dropdown, count in sorted(dropdown_counts.items()):
            print(f"   {dropdown}: {count} values")

