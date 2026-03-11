-- Al Sagr dropdown name mapping
SELECT MapID, Dropdown_Name,`AL SAGR`  FROM WebDB_Live.Medical_CTN_Portal_Field_Mapping;
 
ALTER TABLE WebDB_Live.Medical_CTN_Portal_Field_Mapping 
ADD COLUMN `AL SAGR` VARCHAR(500) NULL AFTER `Liva Globalcare`;
 
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR`= 'TPA' WHERE MapID = 1;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Visa Region' WHERE MapID = 2;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Plan' WHERE MapID = 3;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Aggregate Limit' WHERE MapID = 4;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Geographical Area' WHERE MapID = 5;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Nursing Home' WHERE MapID = 6;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Consult.Ded' WHERE MapID = 8;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Pharmacy Limit' WHERE MapID = 11;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Phar.Co-Ins' WHERE MapID = 12;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Maternity Limit' WHERE MapID = 15;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Dental' WHERE MapID = 20;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Optical' WHERE MapID = 22;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Alternative' WHERE MapID = 24;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Psychiatric' WHERE MapID = 26;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Repatriation' WHERE MapID = 27;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'OP Co-Insurance' WHERE MapID = 41;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'IP- Room & Board' WHERE MapID = 67;
UPDATE WebDB_Live.Medical_CTN_Portal_Field_Mapping SET `AL SAGR` = 'Network' WHERE MapID = 63;



-----------------------------------------------------------------------------------------------------------------
-- Broker and portal mapping table
CREATE TABLE WebDB_Live.Medical_CTN_Broker_Portal_Mapping (
    Mapping_ID INT AUTO_INCREMENT PRIMARY KEY,
    Broker_ID INT NOT NULL COMMENT 'Broker identifier (3, 6, 7, 8, etc.)',
    Broker_Name VARCHAR(100) NOT NULL COMMENT 'Human-readable broker name',
    Portal_Name VARCHAR(100) NOT NULL COMMENT 'Portal name (must match API_PORTAL_GROUPS keys)',
    Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    Updated_At DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_broker_portal (Broker_ID, Portal_Name),
    INDEX idx_broker_id (Broker_ID),
    INDEX idx_portal_name (Portal_Name)
) COMMENT='Defines which portals each broker can access';
 
SET SQL_SAFE_UPDATES = 0;
-- Broker 3 - Lifecare International (9 portals)
INSERT INTO WebDB_Live.Medical_CTN_Broker_Portal_Mapping (Broker_ID, Broker_Name, Portal_Name) VALUES
(3, 'Lifecare International', 'ADNIC'),
(3, 'Lifecare International', 'Takaful'),
(3, 'Lifecare International', 'QATAR'),
(3, 'Lifecare International', 'MaxHealth'),
(3, 'Lifecare International', 'Sukoon'),
(3, 'Lifecare International', 'Orient Aura'),
(3, 'Lifecare International', 'NLGI Aura'),
(3, 'Lifecare International', 'AL SAGR'),
(3, 'Lifecare International', 'QIC HealthX Exclusive'),
(2, 'Lifecare International', 'ADNIC'),
(2, 'Lifecare International', 'Takaful'),
(2, 'Lifecare International', 'Sukoon'),
(6, 'Lifecare International', 'Sukoon'),
(6, 'Lifecare International', 'NLGI Aura');
SET SQL_SAFE_UPDATES = 1;



-------------------------------------------------------------------------------------------------
-- Remove Broker_ID 

-- Remove Broker_ID from the Lifecare(original) table
ALTER TABLE WebDB_Live_Live.Medical_CTN_Cascading_Dropdown_Lifecare
DROP COLUMN Broker_ID;

-- Remove Broker_ID from the Staging table
ALTER TABLE WebDB_Live.Medical_CTN_Cascading_Dropdown_Staging
DROP COLUMN Broker_ID;
 
-- Remove Broker_ID from the Backup table
ALTER TABLE WebDB_Live.Medical_CTN_Cascading_Dropdown_Backup
DROP COLUMN Broker_ID;