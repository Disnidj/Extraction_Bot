"""
Qatar Benefits Formatter
Converts JSON extraction results to formatted text file.
Each line contains one dropdown field with its values.
"""

import json
import os
from datetime import datetime
from src.utils.logger import qatar_logger


class QatarFormatter:
    """Formats Qatar benefits JSON to text format."""
    
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
        qatar_logger.debug(f"Loaded results from {json_file_path}")
    
    def format_to_text(self) -> list:
        """
        Convert JSON results to text format.
        Each line is a JSON object with:
        - Portal, Region, TPA, Network (plan), field_name, values
        
        Returns:
            list: List of formatted lines
        """
        if not self.results:
            raise ValueError("No results to format. Load or provide results first.")
        
        self.output_lines = []
        portal = self.results.get("portal", "QATAR INSURANCE CO")
        
        # Iterate through the hierarchy: emirates -> tpas -> plans -> benefits
        for emirate_name, emirate_data in self.results.get("emirates", {}).items():
            for tpa_name, tpa_data in emirate_data.get("tpas", {}).items():
                for plan_name, plan_data in tpa_data.get("plans", {}).items():
                    self._process_plan_benefits(
                        portal=portal,
                        region=emirate_name,
                        tpa=tpa_name,
                        network=plan_name,
                        benefits=plan_data.get("benefits", {})
                    )
        
        return self.output_lines
    
    def _process_plan_benefits(self, portal: str, region: str, tpa: str, 
                                network: str, benefits: dict):
        """
        Process all benefits for a single plan and add to output lines.
        
        Args:
            portal: Portal name
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
        
        # Output each unique field as a line
        # Order: Portal, Region, TPA, Network (Plan), field_name, values
        for field_name, values in processed_fields.items():
            line_data = {
                "data": {
                    "Portal": portal,
                    "Region": region,
                    "TPA": tpa,
                    "Network": network,
                    "field_name": field_name,
                    "values": values
                }
            }
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
        print(f"\n📊 Formatted {len(self.output_lines)} dropdown fields")
