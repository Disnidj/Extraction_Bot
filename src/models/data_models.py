from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import pandas as pd

@dataclass
class ComparisonSummary:
    """Summary of comparison results"""
    total_records: int = 0
    perfect_matches: int = 0
    value_mismatches: int = 0
    only_in_database: int = 0
    only_in_extracted: int = 0
    companies_affected: int = 0
    total_missing_values: int = 0
    total_extra_values: int = 0
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary"""
        return {
            'Perfect Match': self.perfect_matches,
            'Value Mismatch': self.value_mismatches,
            'Only in Database': self.only_in_database,
            'Only in Extracted': self.only_in_extracted
        }

@dataclass
class DataComparisonResult:
    """Result of data comparison"""
    comparison_df: pd.DataFrame
    summary: ComparisonSummary
    database_companies: List[str] = field(default_factory=list)
    extracted_companies: List[str] = field(default_factory=list)
    mappings_applied: Dict[str, str] = field(default_factory=dict)

@dataclass
class ProcessingStats:
    """Statistics from data processing"""
    original_records: int = 0
    original_portals: int = 0
    filtered_records: int = 0
    filtered_portals: int = 0
    final_companies: List[str] = field(default_factory=list)
    mappings_applied: int = 0