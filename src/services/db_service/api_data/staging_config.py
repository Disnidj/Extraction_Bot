"""
Staging Upload Configuration

Table names and constants for the staging upload service.
"""

# =============================================================================
# TABLE NAMES
# =============================================================================

# Original table with cascading dropdown data
ORIGINAL_TABLE = "Medical_CTN_Cascading_Dropdown_Lifecare"

# Staging table for new extraction data (before comparison)
STAGING_TABLE = "Medical_CTN_Cascading_Dropdown_Staging"

# Backup table for data before changes (7-day retention)
BACKUP_TABLE = "Medical_CTN_Cascading_Dropdown_Backup"

# Audit table for change history
AUDIT_TABLE = "Medical_CTN_Cascading_Dropdown_Audit"

# Mapping table for dropdown name translations
MAPPING_TABLE = "Medical_CTN_Portal_Field_Mapping"


# =============================================================================
# RETENTION SETTINGS
# =============================================================================

# Number of days to keep backups
BACKUP_RETENTION_DAYS = 7

# Number of days to keep audit logs (optional cleanup)
AUDIT_RETENTION_DAYS = 30


# =============================================================================
# FULL TABLE BACKUP SETTINGS
# =============================================================================

# Enable full table backup before changes (creates .sql dump file)
# This is in ADDITION to the selective backup to BACKUP_TABLE
ENABLE_FULL_TABLE_BACKUP = True

# Backup format: 'sql' for SQL dump, 'csv' for CSV export, 'both' for both
FULL_BACKUP_FORMAT = 'sql'  # Options: 'sql', 'csv', 'both'

# Directory to store full table backup files (relative to project root)
FULL_BACKUP_DIR = 'database/backups'

# Number of days to keep full backup files (auto-cleanup old files)
FULL_BACKUP_RETENTION_DAYS = 30


# =============================================================================
# BATCH SETTINGS
# =============================================================================

# Batch size for database INSERT operations
BATCH_SIZE = 100

# Maximum records to process in single transaction
MAX_TRANSACTION_SIZE = 10000


# =============================================================================
# UPLOAD SETTINGS
# =============================================================================

# When True: Only upload records that have dropdown mappings (recommended)
# When False: Upload all records (mapped ones renamed, unmapped keep original names)
ONLY_UPLOAD_MAPPED = True

# Dropdown names to skip (hierarchy fields that shouldn't be uploaded)
SKIP_DROPDOWN_NAMES = {"", "TPA", "Network"}


# =============================================================================
# COMPANY NAME MAPPING
# =============================================================================

# Maps formatter/portal names to standard database company names
COMPANY_NAME_MAPPING = {
    "Sukoon": "SUKOON INSURANCE",
    "Qatar": "QATAR INSURANCE CO",
    "Takaful": "TAKAFUL EMARAT",
    "ADNIC": "ADNIC",
    "MaxHealth": "MaxHealth",
    "Orient Aura": "Orient Aura",
    "NLGI Aura": "Liva Globalcare",
    # Add other portals as needed
}


def standardize_company_name(company: str) -> str:
    """
    Standardize company name to match database naming convention.
    
    Args:
        company: Company name from extracted file
        
    Returns:
        Standardized company name for database
    """
    return COMPANY_NAME_MAPPING.get(company, company)
