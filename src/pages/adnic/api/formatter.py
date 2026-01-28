"""
ADNIC Formatter

Converts extraction results to text format.
Writes records to the extracted_data file.
"""

import json
from typing import Dict, List
from datetime import datetime


class ADNICFormatter:
    """
    Formats ADNIC extraction results and writes to file.
    
    Output format matches the standard extraction format:
    {"data": {"Portal": "...", "TPA": "...", "Network": "...", "field name": "...", "values": [...]}}
    """
    
    def __init__(self, output_path: str = None):
        """
        Initialize formatter with output path.
        
        Args:
            output_path: Path to output file. If None, generates default path.
        """
        self.output_path = output_path
        self.records_written = 0
    
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
        if not self.output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_path = f"extracted_data/adnic_extracted_{timestamp}.txt"
        
        with open(self.output_path, 'a', encoding='utf-8') as f:
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
