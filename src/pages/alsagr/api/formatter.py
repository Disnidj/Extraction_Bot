"""
Al Sagr Formatter
Converts extraction results to database-compatible format.

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Company, TPA, Network, Region, Dropdown_Name, Selection_Value

Key Mappings:
- Portal's "Plan" (plan names) → DB's "Network" column & "Network" dropdown
- Portal's "Network" (RN, GN) → DB's "Plan_Selection" dropdown (Dropdown_Name, not column)
"""

import os
import json
from typing import Dict, List
from datetime import datetime
from src.services.formatter_service import expand_empty_tpa_network
from src.utils.logger import alsagr_logger
from .mapping import PORTAL_NAME, PORTAL_REGION, FIELD_MAPPING, COMPANY_NAME

# Create reverse mapping: Portal_Field_Name (display) -> Dropdown_Name
# e.g., "Plan" -> "Network", "Network" -> "Plan_Selection"
DISPLAY_NAME_TO_DROPDOWN = {v[1]: v[0] for k, v in FIELD_MAPPING.items()}


class AlSagrFormatter:
    """
    Formats Al Sagr extraction results and writes to file.
    
    Output format matches database schema:
    {"Company": "AL SAGR...", "TPA": "...", "Network": "...", 
     "Region": "...", "Dropdown_Name": "...", "Selection_Value": "..."}
    
    Files are saved to: {output_dir}/alsagr/alsagr_extracted_YYYYMMDD_HHMMSS.txt
    """
    
    def __init__(self, output_path: str = None, output_dir: str = "extracted_data"):
        """
        Initialize formatter with output path.
        
        Args:
            output_path: Path to output file. If None, generates portal-specific path.
            output_dir: Base output directory for extracted files.
        """
        self.portal_name = "alsagr"
        self.company_name = COMPANY_NAME
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
        {"data": {"Portal": "...", "field name": "...", "values": [...]}}
        
        To database format (one row per value):
        {"Company": "AL SAGR...", "TPA": "...", "Network": "...",
         "Region": "...", "Dropdown_Name": "...", "Selection_Value": "..."}
        
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
            network = data.get("Network", "")  # Plan name → DB's Network column
            region = data.get("Region", "") or PORTAL_REGION
            
            # Check for various field name formats
            field_name = data.get("field name", data.get("field_name", data.get("Dropdown_Name", "")))
            
            # Map display name to database Dropdown_Name
            # e.g., "Plan" -> "Network", "Network" -> "Plan_Selection"
            dropdown_name = DISPLAY_NAME_TO_DROPDOWN.get(field_name, field_name)
            
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
                    "Selection_Value": str(value)
                }
                rows.append(json.dumps(row, ensure_ascii=False))
        
        # Handle new database format (already flat)
        elif "Selection_Value" in record:
            # Ensure company is set
            record.setdefault("Company", self.company_name)
            
            # Remove Plan_Selection if present (not in DB schema)
            record.pop("Plan_Selection", None)
            
            if not record.get("Region"):
                record["Region"] = PORTAL_REGION
            
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
        alsagr_logger.info(f"Formatting {len(records)} extraction records...")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        all_rows = []
        for record in records:
            all_rows.extend(self.format_record(record))
        
        alsagr_logger.debug(f"Formatted into {len(all_rows)} initial database records")
        
        # Parse rows back to dicts for expansion
        parsed_records = [json.loads(row) for row in all_rows]
        
        # Expand records with empty TPA/Network using shared service
        # This ensures dropdown records work for all TPA/Network combinations
        alsagr_logger.debug("Expanding empty TPA/Network combinations...")
        expanded_records = expand_empty_tpa_network(parsed_records)
        
        alsagr_logger.debug(f"After expansion: {len(expanded_records)} database records")
        
        # Write to file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for record in expanded_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        self.records_written = len(expanded_records)
        alsagr_logger.info(f"Successfully saved {self.records_written} records to {self.output_path}")
        print(f"\n📁 Saved {self.records_written} database rows to: {self.output_path}")
        
        return self.output_path
    
    def format_and_save(self, results: Dict, output_dir: str = None) -> str:
        """
        Format results dict and save to file.
        
        Alternative entry point that takes the full results dict
        from extractor.extract_all_benefits().
        
        Args:
            results: Full results dict from extractor
            output_dir: Optional override for output directory
            
        Returns:
            Path to output file
        """
        if output_dir:
            self.output_dir = output_dir
            self.output_path = self._generate_output_path()
        
        records = results.get("records", [])
        return self.write_records(records)
    
    def print_summary(self):
        """Print formatting summary."""
        print("\n📊 FORMATTER SUMMARY")
        print(f"   Records written: {self.records_written}")
        print(f"   Output file: {self.output_path}")
    
    def write_json(self, records: List[Dict], json_path: str = None) -> str:
        """
        Write records as formatted JSON file (optional backup).
        
        Args:
            records: List of record dicts
            json_path: Path for JSON file (auto-generated if None)
            
        Returns:
            Path to JSON file
        """
        if not json_path:
            # Generate JSON path from txt path
            json_path = self.output_path.replace(".txt", ".json")
        
        # Format records first
        all_rows = []
        for record in records:
            all_rows.extend(self.format_record(record))
        
        # Parse and write as formatted JSON
        parsed_records = [json.loads(row) for row in all_rows]
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_records, f, indent=2, ensure_ascii=False)
        
        alsagr_logger.info(f"JSON backup saved to {json_path}")
        return json_path
    
    def get_stats(self) -> Dict:
        """
        Get formatting statistics.
        
        Returns:
            Dict with stats about formatting operation
        """
        return {
            "portal": self.portal_name,
            "company": self.company_name,
            "records_written": self.records_written,
            "output_path": self.output_path,
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
    formatter = AlSagrFormatter(output_path)
    return formatter.write_records(records)