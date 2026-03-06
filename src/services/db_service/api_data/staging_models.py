"""
Data Models for Staging Upload Service

Contains dataclasses for tracking and reporting database changes.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ChangeRecord:
    """
    Represents a single change (INSERT/UPDATE/DELETE) detected during comparison.
    
    Attributes:
        change_type: Type of change ('INSERT', 'UPDATE', 'DELETE')
        company: Company/portal name
        tpa: TPA value
        network: Network value
        region: Region value
        dropdown_name: Dropdown field name
        old_value: Previous value (for UPDATE/DELETE)
        new_value: New value (for INSERT/UPDATE)
        difference_type: Type of difference detected (VALUE_CHANGE, WHITESPACE_CHANGE, CASE_CHANGE)
    """
    change_type: str  # 'INSERT', 'UPDATE', 'DELETE'
    company: str
    tpa: str
    network: str
    region: str
    dropdown_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    difference_type: Optional[str] = None  # VALUE_CHANGE, WHITESPACE_CHANGE, CASE_CHANGE
    
    def get_difference_description(self) -> str:
        """Get human-readable description of the difference."""
        if self.difference_type == "WHITESPACE_CHANGE":
            return "Whitespace difference (leading/trailing spaces)"
        elif self.difference_type == "INTERNAL_WHITESPACE":
            return "Internal whitespace difference"
        elif self.difference_type == "CASE_CHANGE":
            return "Case difference only"
        elif self.difference_type == "VALUE_CHANGE":
            return "Value changed"
        return ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'change_type': self.change_type,
            'company': self.company,
            'tpa': self.tpa,
            'network': self.network,
            'region': self.region,
            'dropdown_name': self.dropdown_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'difference_type': self.difference_type,
            'difference_description': self.get_difference_description()
        }


@dataclass
class ChangeReport:
    """
    Summary of all changes detected during staging comparison.
    
    Provides methods to:
    - Get total change counts
    - Group changes by company/portal
    - Export to dictionary for reporting
    
    Attributes:
        run_id: Unique identifier for the extraction run
        companies_processed: List of company names processed
        new_records: List of new records to insert
        modified_records: List of records to update
        deleted_records: List of records to delete
        unchanged_count: Number of records with no changes
        staging_count: Total records in staging table
        original_count: Total records in original table (for comparison scope)
        backup_count: Number of records backed up to BACKUP_TABLE
        full_backup_file: Path to full table backup file (SQL or CSV)
        old_backups_removed: Number of old backup records removed (>28 days)
        staging_cleared: Number of old staging records cleared before upload
        audit_records_logged: Number of change records logged to audit table
    """
    run_id: str
    companies_processed: List[str] = field(default_factory=list)
    new_records: List[ChangeRecord] = field(default_factory=list)
    modified_records: List[ChangeRecord] = field(default_factory=list)
    deleted_records: List[ChangeRecord] = field(default_factory=list)
    unchanged_count: int = 0
    staging_count: int = 0
    original_count: int = 0
    backup_count: int = 0
    full_backup_file: Optional[str] = None  # Path to full table backup file
    backup_table: Optional[str] = None  # Name of backup table
    staging_table: Optional[str] = None  # Name of staging table
    original_table: Optional[str] = None  # Name of original table
    audit_table: Optional[str] = None  # Name of audit table
    old_backups_removed: int = 0  # Old backup records removed (>28 days)
    staging_cleared: int = 0  # Old staging records cleared before upload
    audit_records_logged: int = 0  # Change records logged to audit table
    protected_groups: int = 0  # Groups skipped from deletion (safety for API errors)
    protected_values: int = 0  # Values protected from deletion (safety for API errors)
    
    @property
    def total_changes(self) -> int:
        """Total number of changes (new + modified + deleted)."""
        return len(self.new_records) + len(self.modified_records) + len(self.deleted_records)
    
    @property
    def has_changes(self) -> bool:
        """Whether any changes were detected."""
        return self.total_changes > 0
    
    @property
    def new_count(self) -> int:
        """Number of new records."""
        return len(self.new_records)
    
    @property
    def modified_count(self) -> int:
        """Number of modified records."""
        return len(self.modified_records)
    
    @property
    def deleted_count(self) -> int:
        """Number of deleted records."""
        return len(self.deleted_records)
    
    def get_changes_by_company(self) -> Dict[str, Dict]:
        """
        Group all changes by company/portal.
        
        Returns:
            Dict mapping company name to dict with 'new', 'modified', 'deleted' lists
        """
        changes_by_company = {}
        
        for rec in self.new_records:
            changes_by_company.setdefault(rec.company, {'new': [], 'modified': [], 'deleted': []})
            changes_by_company[rec.company]['new'].append(rec)
        
        for rec in self.modified_records:
            changes_by_company.setdefault(rec.company, {'new': [], 'modified': [], 'deleted': []})
            changes_by_company[rec.company]['modified'].append(rec)
        
        for rec in self.deleted_records:
            changes_by_company.setdefault(rec.company, {'new': [], 'modified': [], 'deleted': []})
            changes_by_company[rec.company]['deleted'].append(rec)
        
        return changes_by_company
    
    def get_summary_by_company(self) -> Dict[str, Dict]:
        """
        Get count summary by company (for reports).
        
        Returns:
            Dict mapping company name to counts
        """
        return {
            company: {
                'new': len(data['new']),
                'modified': len(data['modified']),
                'deleted': len(data['deleted']),
                'total': len(data['new']) + len(data['modified']) + len(data['deleted'])
            }
            for company, data in self.get_changes_by_company().items()
        }
    
    def get_changes_by_dropdown(self) -> Dict[str, Dict[str, Dict]]:
        """
        Group all changes by company and dropdown name.
        
        Returns:
            Dict[company] -> Dict[dropdown_name] -> {
                'new_values': [list of new values],
                'deleted_values': [list of deleted values],
                'modified': [list of (old_value, new_value) tuples]
            }
        """
        result = {}
        
        for rec in self.new_records:
            result.setdefault(rec.company, {})
            result[rec.company].setdefault(rec.dropdown_name, {'new_values': [], 'deleted_values': [], 'modified': []})
            result[rec.company][rec.dropdown_name]['new_values'].append(rec.new_value)
        
        for rec in self.deleted_records:
            result.setdefault(rec.company, {})
            result[rec.company].setdefault(rec.dropdown_name, {'new_values': [], 'deleted_values': [], 'modified': []})
            result[rec.company][rec.dropdown_name]['deleted_values'].append(rec.old_value)
        
        for rec in self.modified_records:
            result.setdefault(rec.company, {})
            result[rec.company].setdefault(rec.dropdown_name, {'new_values': [], 'deleted_values': [], 'modified': []})
            result[rec.company][rec.dropdown_name]['modified'].append({
                'old': rec.old_value,
                'new': rec.new_value,
                'type': rec.difference_type
            })
        
        return result
    
    def get_dropdown_change_summary(self, show_all: bool = False) -> Dict[str, Dict[str, Dict]]:
        """
        Get a summary of dropdown changes for reports.
        
        Args:
            show_all: If True, returns ALL values. If False, returns only samples (first 3).
        
        Returns:
            Dict[company] -> Dict[dropdown_name] -> {
                'new_count': int,
                'deleted_count': int,
                'modified_count': int,
                'sample_new': new values (all or first 3),
                'sample_deleted': deleted values (all or first 3),
                'sample_modified': modified values (all or first 2),
                'all_new': ALL new values (always included),
                'all_deleted': ALL deleted values (always included),
                'all_modified': ALL modified values (always included)
            }
        """
        changes = self.get_changes_by_dropdown()
        summary = {}
        
        for company, dropdowns in changes.items():
            summary[company] = {}
            for dropdown_name, data in dropdowns.items():
                # Get unique values and sort them
                new_values = sorted(set(data['new_values']))
                deleted_values = sorted(set(data['deleted_values']))
                modified_list = data['modified']
                
                summary[company][dropdown_name] = {
                    'new_count': len(data['new_values']),
                    'deleted_count': len(data['deleted_values']),
                    'modified_count': len(data['modified']),
                    'sample_new': new_values if show_all else new_values[:3],
                    'sample_deleted': deleted_values if show_all else deleted_values[:3],
                    'sample_modified': modified_list if show_all else modified_list[:2],
                    # Always include all values for detailed view
                    'all_new': new_values,
                    'all_deleted': deleted_values,
                    'all_modified': modified_list
                }
        
        return summary
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'run_id': self.run_id,
            'companies_processed': self.companies_processed,
            'staging_count': self.staging_count,
            'backup_count': self.backup_count,
            'total_changes': self.total_changes,
            'new_count': self.new_count,
            'modified_count': self.modified_count,
            'deleted_count': self.deleted_count,
            'unchanged_count': self.unchanged_count,
            'has_changes': self.has_changes,
            'changes_by_company': self.get_summary_by_company()
        }
