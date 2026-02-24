-- ============================================================================
-- STAGING UPLOAD TABLES
-- Created for comparing extracted data before updating the original table
-- ============================================================================
-- Run this script to create the required tables for staged uploads with
-- comparison, backup, and audit trail functionality.
-- ============================================================================

-- 1. STAGING TABLE
-- Temporary storage for new extraction data before comparison
-- This table is cleared and repopulated on each extraction run
-- ============================================================================
CREATE TABLE IF NOT EXISTS Medical_CTN_Cascading_Dropdown_Staging (
    Staging_ID INT AUTO_INCREMENT PRIMARY KEY,
    Broker_ID INT,
    Company VARCHAR(100),
    TPA VARCHAR(100),
    Network VARCHAR(100),
    Region VARCHAR(100),
    Dropdown_Name TEXT,
    Selection_Value TEXT,
    Run_ID VARCHAR(50) COMMENT 'Unique identifier for the extraction run',
    Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for efficient querying (prefix length for TEXT columns)
    INDEX idx_staging_company (Company),
    INDEX idx_staging_runid (Run_ID),
    INDEX idx_staging_lookup (Company, TPA, Network, Region, Dropdown_Name(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Temporary staging table for new portal extractions before comparison';


-- 2. BACKUP TABLE
-- Snapshot of original data before applying changes
-- Backups are retained for 7 days then automatically cleaned up
-- ============================================================================
CREATE TABLE IF NOT EXISTS Medical_CTN_Cascading_Dropdown_Backup (
    Backup_ID INT AUTO_INCREMENT PRIMARY KEY,
    Run_ID VARCHAR(50) COMMENT 'Links to the extraction run that triggered backup',
    Original_CTN_ID INT COMMENT 'Original CTN_ID from the main table',
    Broker_ID INT,
    Company VARCHAR(100),
    TPA VARCHAR(100),
    Network VARCHAR(100),
    Region VARCHAR(100),
    Dropdown_Name TEXT,
    Selection_Value TEXT,
    Backup_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for efficient querying and cleanup
    INDEX idx_backup_runid (Run_ID),
    INDEX idx_backup_date (Backup_Date),
    INDEX idx_backup_company (Company),
    INDEX idx_backup_lookup (Company, TPA, Network, Region, Dropdown_Name(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Backup of original data before changes - retained for 7 days';


-- 3. AUDIT/CHANGE LOG TABLE
-- Tracks all changes (INSERT/UPDATE/DELETE) made to the original table
-- Provides full audit trail with old and new values
-- ============================================================================
CREATE TABLE IF NOT EXISTS Medical_CTN_Cascading_Dropdown_Audit (
    Audit_ID INT AUTO_INCREMENT PRIMARY KEY,
    Run_ID VARCHAR(50) COMMENT 'Links to the extraction run',
    Change_Type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    Company VARCHAR(100),
    TPA VARCHAR(100),
    Network VARCHAR(100),
    Region VARCHAR(100),
    Dropdown_Name TEXT,
    Old_Value TEXT COMMENT 'Previous value (for UPDATE/DELETE)',
    New_Value TEXT COMMENT 'New value (for INSERT/UPDATE)',
    Difference_Type VARCHAR(50) COMMENT 'Type of change: VALUE_CHANGE, WHITESPACE_CHANGE, CASE_CHANGE',
    Changed_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for efficient querying
    INDEX idx_audit_runid (Run_ID),
    INDEX idx_audit_date (Changed_At),
    INDEX idx_audit_company (Company),
    INDEX idx_audit_type (Change_Type),
    INDEX idx_audit_dropdown (Dropdown_Name(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Audit log of all changes made to cascading dropdown data';


-- ============================================================================
-- VERIFICATION QUERIES
-- Run these after creating tables to verify structure
-- ============================================================================

-- Check tables exist
-- SELECT TABLE_NAME, TABLE_COMMENT 
-- FROM information_schema.TABLES 
-- WHERE TABLE_SCHEMA = DATABASE() 
-- AND TABLE_NAME LIKE 'Medical_CTN_Cascading_Dropdown_%';

-- Check staging table structure
-- DESCRIBE Medical_CTN_Cascading_Dropdown_Staging;

-- Check backup table structure
-- DESCRIBE Medical_CTN_Cascading_Dropdown_Backup;

-- Check audit table structure
-- DESCRIBE Medical_CTN_Cascading_Dropdown_Audit;


-- ============================================================================
-- CLEANUP PROCEDURES (Optional - can be run manually or scheduled)
-- ============================================================================

-- Delete backups older than 7 days
-- DELETE FROM Medical_CTN_Cascading_Dropdown_Backup 
-- WHERE Backup_Date < DATE_SUB(NOW(), INTERVAL 7 DAY);

-- Delete audit logs older than 30 days (optional, adjust as needed)
-- DELETE FROM Medical_CTN_Cascading_Dropdown_Audit 
-- WHERE Changed_At < DATE_SUB(NOW(), INTERVAL 30 DAY);
