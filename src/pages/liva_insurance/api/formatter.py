"""
Liva Insurance Formatter

Converts extraction results to database-compatible format.
Writes records to: extracted_data/liva_insurance/liva_insurance_extracted_YYYYMMDD_HHMMSS.txt

Output Format matches database schema:
- One row per Selection_Value (flat structure)
- Fields: Company, TPA, Network, Region, Dropdown_Name, Selection_Value

TPA/Network Expansion:
- Uses shared expansion service from src.services.formatter_service
- Records with empty TPA/Network are expanded to all TPA/Network combinations
"""

import json
import os
from typing import Dict, List
from datetime import datetime
from src.services.formatter_service import expand_empty_tpa_network
from src.utils.logger import liva_insurance_logger

PORTAL_NAME = "liva_insurance"


class LivaInsuranceFormatter:
    """
    Formats Liva Insurance extraction results and writes to file.
    """

    def __init__(self, output_path: str = None, output_dir: str = "extracted_data"):
        self.portal_name = PORTAL_NAME
        self.company_name = "Liva Insurance"
        self.output_path = output_path
        self.output_dir = output_dir
        self.records_written = 0

        if not self.output_path:
            self.output_path = self._generate_output_path()

    def _generate_output_path(self) -> str:
        """Generate portal-specific output path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(self.output_dir, self.portal_name)
        os.makedirs(folder, exist_ok=True)
        filename = f"{self.portal_name}_extracted_{timestamp}.txt"
        return os.path.join(folder, filename)

    def format_record(self, record: Dict) -> List[str]:
        """
        Format a single record as database rows (one per value).

        Converts old format:
        {"data": {"Portal": "...", "field name": "...", "values": [...]}}

        To database format (one row per value):
        {"Company": "Liva Insurance", ..., "Selection_Value": "..."}
        """
        rows = []

        if "data" in record:
            data = record["data"]
            tpa = data.get("TPA", "")
            network = data.get("Network", "")
            region = data.get("Region", "")
            dropdown_name = data.get("field name", data.get("field_name", data.get("Dropdown_Name", "")))
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

        elif "Selection_Value" in record:
            record.setdefault("Company", self.company_name)
            rows.append(json.dumps(record, ensure_ascii=False))

        return rows

    def write_records(self, records: List[Dict]) -> str:
        """
        Write all records to file in database format.
        Expands records with empty TPA/Network to all combinations.
        """
        liva_insurance_logger.info(f"Formatting {len(records)} extraction records...")

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        all_rows = []
        for record in records:
            all_rows.extend(self.format_record(record))

        liva_insurance_logger.debug(f"Formatted into {len(all_rows)} initial database records")

        # Parse rows back to dicts for expansion
        parsed_records = [json.loads(row) for row in all_rows]

        # Expand records with empty TPA/Network
        liva_insurance_logger.debug("Expanding empty TPA/Network combinations...")
        expanded_records = expand_empty_tpa_network(parsed_records)

        liva_insurance_logger.debug(f"After expansion: {len(expanded_records)} database records")

        with open(self.output_path, 'w', encoding='utf-8') as f:
            for record in expanded_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        self.records_written = len(expanded_records)
        liva_insurance_logger.info(f"Saved {self.records_written} records to {self.output_path}")
        print(f"\n💾 Saved {self.records_written} database rows to: {self.output_path}")

        return self.output_path

    def get_stats(self) -> Dict:
        """Get formatter statistics."""
        return {
            "records_written": self.records_written,
            "output_path": self.output_path
        }


def format_and_save(records: List[Dict], output_path: str = None) -> str:
    """Convenience function to format and save records."""
    formatter = LivaInsuranceFormatter(output_path)
    return formatter.write_records(records)
