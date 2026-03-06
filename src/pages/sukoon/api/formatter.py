"""  
Sukoon Formatter

Converts extraction results to database-compatible format.
Writes records to portal-specific folder: extracted_data/sukoon/sukoon_extracted_YYYYMMDD_HHMMSS.txt

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Company, TPA, Network, Region, Dropdown_Name, Selection_Value

TPA/Network Expansion:
- Uses shared expansion service from src.services.formatter_service
- Records with empty TPA/Network are expanded to all TPA/Network combinations
- Ensures cascading dropdowns work regardless of TPA/Network selection
"""

import json
import os
from typing import Dict, List
from datetime import datetime
from src.services.formatter_service import expand_empty_tpa_network
from src.utils.logger import sukoon_logger
from .mapping import PORTAL_REGION

# Portal name for this formatter
PORTAL_NAME = "sukoon"

# Sukoon-specific dropdown name mapping
# Maps extraction field names to portal-specific names that match the mapping table
SUKOON_DROPDOWN_NAMES = {
    "TPA": "Indemnity Limit",
    "Network": "Applicable Network",
}


class SukoonFormatter:
    """
    Formats Sukoon extraction results and writes to file.
    
    Output format matches database schema:
    {"Company": "Sukoon", "TPA": "...", "Network": "...", 
     "Region": "...", "Dropdown_Name": "...", "Selection_Value": "..."}
    
    Files are saved to: {output_dir}/sukoon/sukoon_extracted_YYYYMMDD_HHMMSS.txt
    """
    
    def __init__(self, output_path: str = None, output_dir: str = "extracted_data"):
        """
        Initialize formatter with output path.
        
        Args:
            output_path: Path to output file. If None, generates portal-specific path.
            output_dir: Base output directory for extracted files.
        """
        self.portal_name = PORTAL_NAME
        self.company_name = "Sukoon"
        self.output_path = output_path
        self.output_dir = output_dir
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
        {"Company": "Sukoon", ..., "Selection_Value": "..."}
        
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
            region = data.get("Region", "") or PORTAL_REGION  # Default to PORTAL_REGION if empty
            # Check for various field name formats: "field name", "field_name", "Dropdown_Name"
            dropdown_name = data.get("field name", data.get("field_name", data.get("Dropdown_Name", "")))
            
            # Apply Sukoon-specific dropdown name mapping
            dropdown_name = SUKOON_DROPDOWN_NAMES.get(dropdown_name, dropdown_name)
            
            values = data.get("values", [])
            
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
                rows.append(json.dumps(row, ensure_ascii=False))
        
        # Handle new database format (already flat)
        elif "Selection_Value" in record:
            # Ensure company is set
            record.setdefault("Company", self.company_name)
            
            # Default Region to PORTAL_REGION if empty
            if not record.get("Region"):
                record["Region"] = PORTAL_REGION
            
            # Apply Sukoon-specific dropdown name mapping
            if "Dropdown_Name" in record:
                record["Dropdown_Name"] = SUKOON_DROPDOWN_NAMES.get(record["Dropdown_Name"], record["Dropdown_Name"])
            
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
        sukoon_logger.info(f"Formatting {len(records)} extraction records...")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        all_rows = []
        for record in records:
            all_rows.extend(self.format_record(record))
        
        sukoon_logger.debug(f"Formatted into {len(all_rows)} initial database records")
        
        # Parse rows back to dicts for expansion
        parsed_records = [json.loads(row) for row in all_rows]
        
        # Expand records with empty TPA/Network using shared service
        sukoon_logger.debug("Expanding empty TPA/Network combinations...")
        expanded_records = expand_empty_tpa_network(parsed_records)
        
        sukoon_logger.info(f"After expansion: {len(expanded_records)} total records")
        sukoon_logger.debug(f"Output file: {self.output_path}")
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for record in expanded_records:
                # Use ensure_ascii=True to avoid Unicode encoding issues
                f.write(json.dumps(record, ensure_ascii=True) + "\n")
        
        self.records_written = len(expanded_records)
        sukoon_logger.info(f"Successfully saved {self.records_written} records to {self.output_path}")
        print(f"Saved {self.records_written} database rows to: {self.output_path}")
        
        return self.output_path
    
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
            folder = os.path.join(self.output_dir, self.portal_name)
            os.makedirs(folder, exist_ok=True)
            json_path = os.path.join(folder, f"{self.portal_name}_benefits_{timestamp}.json")
        
        # Structure the data hierarchically
        structured = {
            "portal": "SUKOON INSURANCE",
            "extracted_at": datetime.now().isoformat(),
            "total_records": len(records),
            "records": records
        }
        
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
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
        output_path: Path to output file (optional)
        
    Returns:
        Path to output file
    """
    formatter = SukoonFormatter(output_path)
    return formatter.write_records(records)
