"""
Multi-broker aware database upload service.
Handles uploading extracted data for multiple brokers with shared portal deduplication.
"""

from typing import List, Dict, Optional
from pathlib import Path
from src.services.db_service.api_data.staging_upload import StagingUploader
from src.services.broker_service.portal_mapper import PortalMapper
from src.config.broker_config import get_broker_name
from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD


class MultiBrokerUploader:
    """Handles database uploads for multi-broker extraction runs."""
    
    def __init__(self, run_id: str, selected_broker_ids: List[int]):
        """
        Initialize multi-broker uploader.
        
        Args:
            run_id: Unique run identifier (timestamp)
            selected_broker_ids: List of broker IDs in this extraction run
        """
        self.run_id = run_id
        self.selected_broker_ids = selected_broker_ids
        self.uploader = StagingUploader()
        self.portal_mapper = PortalMapper()
        self.db = MySQLDatabase(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
        
        # Analyze portal distribution
        self.portal_analysis = self.portal_mapper.analyze_portal_distribution(selected_broker_ids)
    
    def upload_portal_data(self, portal_name: str, extracted_file_path: str) -> Dict:
        """
        Upload extracted data for a portal using BATCH multi-broker approach.
        All brokers' data is uploaded to staging at once, then compared and applied together.
        This is more efficient and atomic than sequential broker-by-broker uploads.
        
        Args:
            portal_name: Name of portal (e.g., 'ADNIC')
            extracted_file_path: Path to extracted data file
            
        Returns:
            Dict with upload statistics
        """
        # Determine which brokers use this portal
        brokers_using_portal = self._get_brokers_for_portal(portal_name)
        
        if not brokers_using_portal:
            print(f"⚠️  No brokers configured for portal {portal_name}")
            return {"status": "skipped", "reason": "no_brokers"}
        
        is_shared = len(brokers_using_portal) > 1
        
        print(f"\n{'='*70}")
        print(f"📤 Uploading {portal_name} data (BATCH MODE)")
        print(f"{'='*70}")
        print(f"Brokers: {', '.join([f'Broker {bid} ({get_broker_name(bid)})' for bid in brokers_using_portal])}")
        
        if is_shared:
            print(f"✅ Shared portal - uploading ALL brokers at once for maximum efficiency")
        else:
            print(f"Single broker portal")
        
        try:
            # BATCH UPLOAD: Parse file once, upload all brokers together
            print(f"\n   📋 Parsing extracted file...")
            all_records = self._parse_and_prepare_multi_broker_records(
                extracted_file_path, 
                portal_name,
                brokers_using_portal
            )
            
            print(f"   ✅ Prepared {len(all_records)} total records for {len(brokers_using_portal)} broker(s)")
            for broker_id in brokers_using_portal:
                broker_count = sum(1 for r in all_records if r.get('Broker_ID') == broker_id)
                print(f"      • Broker {broker_id}: {broker_count} records")
            
            # Apply mappings once
            print(f"\n   🔄 Applying dropdown mappings...")
            all_records = self._apply_mappings_to_records(all_records, portal_name)
            
            # Get unique dropdown names by company for staging upload
            dropdown_names_by_company = {portal_name: set()}
            for record in all_records:
                dropdown_name = record.get("Dropdown_Name", "")
                if dropdown_name:
                    dropdown_names_by_company[portal_name].add(dropdown_name)
            
            # SINGLE BATCH UPLOAD: Upload all brokers at once
            print(f"\n   📤 Batch uploading to staging table for all brokers...")
            success, report, message = self.uploader.process_upload(
                records=all_records,
                companies=[portal_name],
                dropdown_names_by_company=dropdown_names_by_company
            )
            
            if success:
                print(f"\n   ✅ Batch upload completed successfully!")
                return {
                    "status": "success",
                    "portal": portal_name,
                    "brokers": brokers_using_portal,
                    "is_shared": is_shared,
                    "report": report,
                    "total_changes": report.total_changes if report else 0
                }
            else:
                print(f"\n   ❌ Batch upload failed: {message}")
                return {
                    "status": "failed",
                    "portal": portal_name,
                    "brokers": brokers_using_portal,
                    "error": message
                }
                
        except Exception as e:
            print(f"\n   ❌ Batch upload error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "portal": portal_name,
                "brokers": brokers_using_portal,
                "error": str(e)
            }
    
    def _parse_and_prepare_multi_broker_records(
        self, 
        file_path: str, 
        portal_name: str, 
        broker_ids: List[int]
    ) -> List[Dict]:
        """
        Parse extracted file and prepare records for multiple brokers.
        Each broker gets identical data with different Broker_ID.
        
        Args:
            file_path: Path to extracted file
            portal_name: Portal/company name
            broker_ids: List of broker IDs to prepare data for
            
        Returns:
            List of all records for all brokers combined
        """
        import json
        from src.services.db_service.api_data.staging_config import standardize_company_name
        
        # Parse base records from file (Broker_ID = 0 placeholder)
        base_records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    base_records.append(record)
                except json.JSONDecodeError as e:
                    print(f"      ⚠️ Skipping invalid JSON at line {line_num}: {e}")
        
        if not base_records:
            raise ValueError("No valid records found in file")
        
        # Standardize company name
        standardized_company = standardize_company_name(portal_name)
        
        # Create copies for each broker
        all_records = []
        for broker_id in broker_ids:
            for base_record in base_records:
                record = base_record.copy()
                record['Broker_ID'] = broker_id  # Override placeholder
                record['Company'] = standardized_company
                all_records.append(record)
        
        return all_records
    
    def _apply_mappings_to_records(self, records: List[Dict], portal_name: str) -> List[Dict]:
        """
        Apply dropdown name mappings to records.
        
        Args:
            records: List of records
            portal_name: Portal name
            
        Returns:
            Records with mappings applied
        """
        from src.services.db_service.api_data.staging_mapping_service import (
            load_dropdown_mappings, 
            apply_dropdown_mapping
        )
        from src.services.db_service.api_data.staging_config import get_mapping_column_name
        
        # Connect to database for mapping lookup
        if not self.db.connect():
            raise ConnectionError("Failed to connect to database for mappings")
        
        try:
            # Get the correct column name for mapping table lookup
            mapping_column = get_mapping_column_name(portal_name)
            
            mappings = load_dropdown_mappings(self.db, mapping_column)
            if mappings:
                # Apply mappings (returns 5 values)
                records, mapped, unmapped, applied_mappings, unmapped_names = apply_dropdown_mapping(
                    records, mappings, only_mapped=False
                )
                print(f"      ✅ Mapped: {mapped}, Unmapped: {unmapped}")
            else:
                print(f"      ℹ️  No mappings found for {portal_name}")
            
            return records
            
        finally:
            self.db.disconnect()
    
    def _get_brokers_for_portal(self, portal_name: str) -> List[int]:
        """
        Get list of brokers that use this portal, ordered by selection.
        
        Args:
            portal_name: Portal name
            
        Returns:
            List of broker IDs (ordered by user's selection)
        """
        # Get all brokers that have this portal in database
        all_brokers = self.portal_mapper.get_brokers_using_portal(portal_name)
        
        # Filter to only selected brokers and preserve selection order
        ordered_brokers = [
            bid for bid in self.selected_broker_ids
            if bid in all_brokers
        ]
        
        return ordered_brokers
    
    def upload_all_portals_batch(self, portal_files: List[Dict]) -> Dict:
        """
        Upload ALL portals in a single batch operation for maximum efficiency.
        This processes all portals together: single backup, single comparison, single apply.
        
        Args:
            portal_files: List of dicts with portal info:
                [
                    {'portal': 'ADNIC', 'file': 'path/to/adnic.txt'},
                    {'portal': 'Sukoon', 'file': 'path/to/sukoon.txt'}
                ]
        
        Returns:
            Dict with combined upload results for all portals
        """
        if not portal_files:
            return {"status": "skipped", "reason": "no_portals"}
        
        print(f"\n{'='*70}")
        print(f"📤 BATCH UPLOAD - ALL PORTALS (Multi-Broker)")
        print(f"{'='*70}")
        print(f"Portals: {len(portal_files)}")
        print(f"Brokers: {', '.join([f'Broker {bid} ({get_broker_name(bid)})' for bid in self.selected_broker_ids])}")
        
        try:
            # Step 1: Parse and combine ALL portal data
            all_records = []
            all_dropdown_names = {}
            portal_broker_counts = {}
            
            for item in portal_files:
                portal_name = item['portal']
                file_path = item['file']
                
                print(f"\n   📋 Parsing {portal_name}...")
                
                # Get brokers for this portal
                brokers_using_portal = self._get_brokers_for_portal(portal_name)
                
                if not brokers_using_portal:
                    print(f"      ⚠️  No brokers configured for {portal_name}, skipping...")
                    continue
                
                # Parse and prepare records for all brokers
                records = self._parse_and_prepare_multi_broker_records(
                    file_path, 
                    portal_name,
                    brokers_using_portal
                )
                
                # Apply mappings
                records = self._apply_mappings_to_records(records, portal_name)
                
                # Add to combined list
                all_records.extend(records)
                
                # Collect dropdown names for this portal
                portal_dropdowns = set(r.get("Dropdown_Name") for r in records if r.get("Dropdown_Name"))
                all_dropdown_names[portal_name] = portal_dropdowns
                
                # Track broker counts for summary
                portal_broker_counts[portal_name] = {
                    'brokers': brokers_using_portal,
                    'records': len(records)
                }
                
                print(f"      ✅ {portal_name}: {len(records)} records for {len(brokers_using_portal)} broker(s)")
            
            if not all_records:
                print(f"\n   ⚠️  No records to upload")
                return {"status": "skipped", "reason": "no_records"}
            
            # Display summary
            print(f"\n   {'─'*70}")
            print(f"   📊 BATCH SUMMARY:")
            print(f"      • Total portals: {len(all_dropdown_names)}")
            print(f"      • Total records: {len(all_records)}")
            print(f"      • Total brokers: {len(self.selected_broker_ids)}")
            
            for portal_name, info in portal_broker_counts.items():
                broker_names = ', '.join([f"Broker {bid}" for bid in info['brokers']])
                print(f"      • {portal_name}: {info['records']} records ({broker_names})")
            print(f"   {'─'*70}")
            
            # Step 2: Single batch upload to staging for ALL portals
            print(f"\n   📤 Uploading ALL portals to staging in single batch operation...")
            print(f"      ✅ Single backup + Single comparison + Single apply = Maximum efficiency!")
            
            success, report, message = self.uploader.process_upload(
                records=all_records,
                companies=list(all_dropdown_names.keys()),
                dropdown_names_by_company=all_dropdown_names
            )
            
            if success:
                print(f"\n   ✅ Batch upload completed successfully for ALL {len(portal_files)} portals!")
                return {
                    "status": "success",
                    "portals": [item['portal'] for item in portal_files],
                    "total_records": len(all_records),
                    "total_changes": report.total_changes if report else 0,
                    "report": report,
                    "portal_details": portal_broker_counts
                }
            else:
                print(f"\n   ❌ Batch upload failed: {message}")
                return {
                    "status": "failed",
                    "portals": [item['portal'] for item in portal_files],
                    "error": message
                }
                
        except Exception as e:
            print(f"\n   ❌ Batch upload error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "portals": [item['portal'] for item in portal_files],
                "error": str(e)
            }
    
    def generate_upload_summary(self) -> str:
        """
        Generate summary of multi-broker upload.
        
        Returns:
            Formatted summary string
        """
        summary = f"\n{'='*70}\n"
        summary += "📊 MULTI-BROKER UPLOAD SUMMARY (BATCH MODE)\n"
        summary += f"{'='*70}\n"
        summary += f"Run ID: {self.run_id}\n"
        summary += f"Brokers: {len(self.selected_broker_ids)}\n"
        
        for broker_id in self.selected_broker_ids:
            summary += f"  • Broker {broker_id} - {get_broker_name(broker_id)}\n"
        
        summary += f"\nTotal Unique Portals: {self.portal_analysis['total_unique']}\n"
        
        if self.portal_analysis['shared']:
            summary += f"Shared Portals: {len(self.portal_analysis['shared'])} (uploaded in batch)\n"
            for portal, brokers in self.portal_analysis['shared'].items():
                broker_names = [f"Broker {bid}" for bid in brokers]
                summary += f"  • {portal} → {', '.join(broker_names)}\n"
        
        summary += f"{'='*70}\n"
        
        return summary
