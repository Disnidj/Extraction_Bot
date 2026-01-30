"""
ADNIC Formatter

Converts extraction results to text format.
Writes records to portal-specific folder: extracted_data/adnic/adnic_extracted_YYYYMMDD_HHMMSS.txt
"""

import json
import os
from typing import Dict, List
from datetime import datetime

# Portal name for this formatter
PORTAL_NAME = "adnic"


class ADNICFormatter:
    """
    Formats ADNIC extraction results and writes to file.
    
    Output format matches the standard extraction format:
    {"data": {"Portal": "...", "TPA": "...", "Network": "...", "field name": "...", "values": [...]}}
    
    Files are saved to: {output_dir}/adnic/adnic_extracted_YYYYMMDD_HHMMSS.txt
    """
    
    def __init__(self, output_path: str = None, output_dir: str = "extracted_data"):
        """
        Initialize formatter with output path.
        
        Args:
            output_path: Path to output file. If None, generates portal-specific path.
            output_dir: Base output directory for extracted files.
        """
        self.portal_name = PORTAL_NAME
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
    
    def format_record(self, record: Dict) -> str:
        """
        Format a single record as JSON string.
        
        Args:
            record: Record dict to format
            
        Returns:
            JSON string representation
        """
        return json.dumps(record, ensure_ascii=False)
    
    def write_records(self, records: List[Dict]) -> str:
        """
        Write all records to file.
        
        Args:
            records: List of record dicts
            
        Returns:
            Path to output file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(self.format_record(record) + "\n")
        
        self.records_written = len(records)
        print(f"\n💾 Saved {self.records_written} records to: {self.output_path}")
        
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
            json_path = f"extracted_data/adnic_benefits_{timestamp}.json"
        
        # Structure the data hierarchically
        structured = {
            "portal": "ADNIC",
            "extracted_at": datetime.now().isoformat(),
            "total_records": len(records),
            "records": records
        }
        
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


def format_and_save(records: List[Dict], output_path: str) -> str:
    """
    Convenience function to format and save records.
    
    Args:
        records: List of extraction records
        output_path: Path to output file
        
    Returns:
        Path to output file
    """
    formatter = ADNICFormatter(output_path)
    return formatter.write_records(records)
