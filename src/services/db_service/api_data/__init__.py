# API Data Service Module
# Handles staging upload, comparison, and database operations for API extraction data

from .staging_models import ChangeRecord, ChangeReport
from .staging_config import (
    ORIGINAL_TABLE, STAGING_TABLE, BACKUP_TABLE, AUDIT_TABLE,
    BACKUP_RETENTION_DAYS, BATCH_SIZE, ONLY_UPLOAD_MAPPED,
    SKIP_DROPDOWN_NAMES, COMPANY_NAME_MAPPING, standardize_company_name
)
from .staging_comparison_utils import (
    highlight_difference, format_value_for_display,
    get_comparison_key, is_whitespace_only_change, is_case_only_change
)
from .staging_mapping_service import (
    load_dropdown_mappings, apply_dropdown_mapping,
    filter_skip_dropdowns, get_unique_dropdown_names, build_mapping_summary
)
from .staging_upload import StagingUploader
from .upload_extracted import upload_to_database

__all__ = [
    'ChangeRecord',
    'ChangeReport',
    'StagingUploader',
    'upload_to_database',
    'ORIGINAL_TABLE',
    'STAGING_TABLE', 
    'BACKUP_TABLE',
    'AUDIT_TABLE',
    'BACKUP_RETENTION_DAYS',
    'BATCH_SIZE',
    'ONLY_UPLOAD_MAPPED',
    'SKIP_DROPDOWN_NAMES',
    'COMPANY_NAME_MAPPING',
    'standardize_company_name',
    'highlight_difference',
    'format_value_for_display',
    'get_comparison_key',
    'is_whitespace_only_change',
    'is_case_only_change',
    'load_dropdown_mappings',
    'apply_dropdown_mapping',
    'filter_skip_dropdowns',
    'get_unique_dropdown_names',
    'build_mapping_summary',
]
