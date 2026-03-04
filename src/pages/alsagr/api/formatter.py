"""
Al Sagr Formatter
Converts extraction results to database-compatible format.

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Broker_ID, Company, TPA, Network, Region, Dropdown_Name, Selection_Value

Output file: extracted_data/alsagr/alsagr_extracted_YYYYMMDD_HHMMSS.txt
"""

import json
import os
from typing import Dict, List
from datetime import datetime
from src.utils.logger import alsagr_logger
from .mapping import PORTAL_NAME, PORTAL_REGION, FIELD_MAPPING

# Default Broker ID - placeholder (will be overwritten during upload)
DEFAULT_BROKER_ID = 0

# Create reverse mapping: Portal_Field_Name (display) -> Dropdown_Name
# e.g., "Visa Region" -> "Region", "Aggregate Limit" -> "Annual"
DISPLAY_NAME_TO_DROPDOWN = {v[1]: v[0] for k, v in FIELD_MAPPING.items()}


class AlSagrFormatter:
    """
    Formats Al Sagr extraction results and writes to file.
    
    Output format matches database schema:
    {"Broker_ID": 3, "Company": "Al Sagr", "TPA": "", "Network": "...", 
     "Region": "...", "Dropdown_Name": "...", "Selection_Value": "..."}
    
    Files are saved to: {output_dir}/alsagr/alsagr_extracted_YYYYMMDD_HHMMSS.txt
    """
    
    def __init__(self, output_path: str = None, output_dir: str = "extracted_data", 
                 broker_id: int = DEFAULT_BROKER_ID):
        """
        Initialize formatter with output path.
        
        Args:
            output_path: Path to output file. If None, generates portal-specific path.
            output_dir: Base output directory for extracted files.
            broker_id: Broker ID for database records.
        """
        self.portal_name = "alsagr"
        self.company_name = PORTAL_NAME
        self.output_path = output_path
        self.output_dir = output_dir
        self.broker_id = broker_id
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
        {"Broker_ID": 3, "Company": "Al Sagr", ..., "Selection_Value": "..."}
        
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
            region = data.get("Region", "") or PORTAL_REGION
            
            # Check for various field name formats
            field_name = data.get("field name", data.get("field_name", data.get("Dropdown_Name", "")))
            
            # Map display name to database Dropdown_Name
            # e.g., "Visa Region" -> "Region", "Aggregate Limit" -> "Annual"
            dropdown_name = DISPLAY_NAME_TO_DROPDOWN.get(field_name, field_name)
            
            values = data.get("values", [])
            
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
                    "Selection_Value": str(value)
                }
                rows.append(json.dumps(row, ensure_ascii=False))
        
        # Handle new database format (already flat)
        elif "Selection_Value" in record:
            record.setdefault("Broker_ID", self.broker_id)
            record.setdefault("Company", self.company_name)
            
            if not record.get("Region"):
                record["Region"] = PORTAL_REGION
            
            rows.append(json.dumps(record, ensure_ascii=False))
        
        return rows
    
    def write_records(self, records: List[Dict]) -> str:
        """
        Write all records to file in database format.
        
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
        
        alsagr_logger.debug(f"Formatted into {len(all_rows)} database records")
        
        # Write to file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for row in all_rows:
                f.write(row + "\n")
        
        self.records_written = len(all_rows)
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
