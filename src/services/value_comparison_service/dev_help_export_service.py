import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from src.utils.logger import logger
from src.utils.load_yaml import DB_UPDATE_DIR
from src.models.data_models import DataComparisonResult
from src.config.constants import EXPORT_COLUMN_MAPPINGS
class ExportService:
    """Handles data export operations with original extracted field names"""
    
    def __init__(self, broker_id: int):
        self.broker_id = broker_id
    
    def save_comparison_results(self, result: DataComparisonResult) -> Optional[str]:
        """Save comparison results to Excel file with original extracted field names"""
        if result.comparison_df.empty:
            logger.warning("No comparison results to save")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # ✅ Handle combined mode (all brokers)
        if self.broker_id == 0:
            filename = f"value_mismatches_all_brokers_{timestamp}.xlsx"
            logger.info("📊 Creating COMBINED RPA file for ALL brokers")
        else:
            filename = f"value_mismatches_broker_{self.broker_id}_{timestamp}.xlsx"
            
        save_path = Path(DB_UPDATE_DIR) / filename

        try:
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                # All results sheet
                self._create_all_results_sheet(writer, result.comparison_df)
                
                # Individual mismatch type sheets
                self._create_mismatch_type_sheets(writer, result.comparison_df)
                
                # RPA summary sheet
                self._create_rpa_summary_sheet(writer, result)
                
                # Statistics logging
                self._log_export_statistics(result)
            
            logger.info(f"Results saved to: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Error saving Excel file: {e}")
            return None
    
    def _create_all_results_sheet(self, writer: pd.ExcelWriter, comparison_df: pd.DataFrame):
        """Create the main results sheet with original extracted field names"""
        export_cols = [
            'Company', 'TPA', 'Network', 'Region',
            'Original_Extracted_Field_Name', 
            'DB_Field_Display_Name',         
            'Mismatch_Type',
            'Values_String_Extracted', 'Values_String_Database', 
            'Values_Only_Extracted_Str', 'Values_Only_Database_Str', 'Values_Common_Str'
        ]
        
        # Check which columns exist in the dataframe
        available_cols = [col for col in export_cols if col in comparison_df.columns]
        
        if 'Original_Extracted_Field_Name' not in comparison_df.columns:
            logger.warning("Original_Extracted_Field_Name column not found, using Dropdown_Name")
            available_cols = [col if col != 'Original_Extracted_Field_Name' else 'Dropdown_Name' for col in available_cols]
        
        if 'DB_Field_Display_Name' not in comparison_df.columns:
            logger.warning("DB_Field_Display_Name column not found, using Dropdown_Name")
            available_cols = [col if col != 'DB_Field_Display_Name' else 'Dropdown_Name' for col in available_cols]
        
        export_df = comparison_df[available_cols].copy()
        
        updated_column_mappings = [
            'Company', 'TPA', 'Network', 'Region',
            'Extracted_Field_Name',      
            'DB_Field_Name',             
            'Mismatch_Type',
            'All_Values_Extracted', 'All_Values_Database',
            'Only_in_Extracted', 'Only_in_Database', 'Common_Values'
        ]
        
        export_df.columns = updated_column_mappings[:len(export_df.columns)]
        export_df.to_excel(writer, sheet_name='All_Results', index=False)
        logger.info(f"Created All_Results sheet with {len(export_df)} records")
    
    def _create_mismatch_type_sheets(self, writer: pd.ExcelWriter, comparison_df: pd.DataFrame):
        """Create individual sheets for each mismatch type with original field names"""
        mismatch_types = ['Only in Database', 'Only in Extracted', 'Value Mismatch', 'Perfect Match']
        
        for mismatch_type in mismatch_types:
            type_data = comparison_df[comparison_df['Mismatch_Type'] == mismatch_type]
            sheet_name = mismatch_type.replace(' ', '_')
            
            if not type_data.empty:
                if mismatch_type in ['Value Mismatch', 'Only in Database', 'Only in Extracted']:
                    # Enhanced sheet for actionable mismatch types
                    self._create_value_mismatch_sheet(writer, type_data, sheet_name)
                else:
                    # Standard sheet for other types
                    self._create_standard_mismatch_sheet(writer, type_data, sheet_name)
            else:
                self._create_empty_sheet(writer, sheet_name, mismatch_type)
    
    def _create_value_mismatch_sheet(self, writer: pd.ExcelWriter, type_data: pd.DataFrame, sheet_name: str):
        """Create enhanced Value Mismatch sheet with original field names - now includes all actionable mismatch types"""
        logger.info(f"Creating ENHANCED {sheet_name} sheet with {len(type_data)} records")
        
        # Note: type_data is already filtered to only include Value Mismatch records
        # But we should also handle Only in Database and Only in Extracted in the main sheet creation
        
        
        export_cols = [
            'Company', 'TPA', 'Network', 'Region',
            'Original_Extracted_Field_Name',  
            'DB_Field_Display_Name',          
            'Mismatch_Type',
            'Values_String_Extracted', 'Values_String_Database', 
            'Values_Only_Extracted_Str', 'Values_Only_Database_Str', 'Values_Common_Str'
        ]
        
        # Check which columns exist
        available_cols = [col for col in export_cols if col in type_data.columns]
        
        if 'Original_Extracted_Field_Name' not in type_data.columns:
            logger.warning("Original_Extracted_Field_Name column not found, using Dropdown_Name")
            available_cols = [col if col != 'Original_Extracted_Field_Name' else 'Dropdown_Name' for col in available_cols]
        
        if 'DB_Field_Display_Name' not in type_data.columns:
            logger.warning("DB_Field_Display_Name column not found, using Dropdown_Name")
            available_cols = [col if col != 'DB_Field_Display_Name' else 'Dropdown_Name' for col in available_cols]
        
        enhanced_export = type_data[available_cols].copy()
        
        enhanced_column_mappings = [
            'Company', 'TPA', 'Network', 'Region',
            'Extracted_Field_Name',           
            'DB_Field_Name',                  
            'Mismatch_Type',
            'All_Values_in_Extraction',
            'All_Values_in_Database',
            'Values_MISSING_from_Database',  
            'Values_EXTRA_in_Database',     
            'Values_MATCHING_Both_Sources'
        ]
        
        enhanced_export.columns = enhanced_column_mappings[:len(enhanced_export.columns)]
        
        # Add DB action columns based on mismatch type
        if 'Values_MISSING_from_Database' in enhanced_export.columns:
            enhanced_export['Values_to_INSERT_in_DB'] = enhanced_export.apply(
                lambda row: (
                    row['All_Values_in_Extraction'] if row['Mismatch_Type'] == 'Only in Extracted'
                    else row['Values_MISSING_from_Database'] if row['Mismatch_Type'] == 'Value Mismatch'
                    else ''
                ), axis=1
            )
        if 'Values_EXTRA_in_Database' in enhanced_export.columns:
            enhanced_export['Values_to_REVIEW_in_DB'] = enhanced_export.apply(
                lambda row: (
                    row['All_Values_in_Database'] if row['Mismatch_Type'] == 'Only in Database'
                    else row['Values_EXTRA_in_Database'] if row['Mismatch_Type'] == 'Value Mismatch'
                    else ''
                ), axis=1
            )
        
        enhanced_export.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.info(f"Created enhanced {sheet_name} sheet with {len(enhanced_export)} records")
    
    def _create_standard_mismatch_sheet(self, writer: pd.ExcelWriter, type_data: pd.DataFrame, sheet_name: str):
        """Create standard mismatch sheet with original field names"""
        
        # Updated to include original extracted field names and DB field display names
        export_cols = [
            'Company', 'TPA', 'Network', 'Region',
            'Original_Extracted_Field_Name',  
            'DB_Field_Display_Name',          
            'Mismatch_Type',
            'Values_String_Extracted', 'Values_String_Database', 
            'Values_Only_Extracted_Str', 'Values_Only_Database_Str', 'Values_Common_Str'
        ]
        
        # Check which columns exist
        available_cols = [col for col in export_cols if col in type_data.columns]
        
        if 'Original_Extracted_Field_Name' not in type_data.columns:
            available_cols = [col if col != 'Original_Extracted_Field_Name' else 'Dropdown_Name' for col in available_cols]
        
        if 'DB_Field_Display_Name' not in type_data.columns:
            available_cols = [col if col != 'DB_Field_Display_Name' else 'Dropdown_Name' for col in available_cols]
        
        type_export = type_data[available_cols].copy()
        
        # Standard column mappings
        standard_column_mappings = [
            'Company', 'TPA', 'Network', 'Region',
            'Extracted_Field_Name',      
            'DB_Field_Name',             
            'Mismatch_Type',
            'All_Values_Extracted', 'All_Values_Database',
            'Only_in_Extracted', 'Only_in_Database', 'Common_Values'
        ]
        
        type_export.columns = standard_column_mappings[:len(type_export.columns)]
        type_export.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.info(f"Created sheet '{sheet_name}' with {len(type_data)} records")
    
    def _create_empty_sheet(self, writer: pd.ExcelWriter, sheet_name: str, mismatch_type: str):
        """Create empty sheet with message"""
        empty_df = pd.DataFrame({'Message': [f'No {mismatch_type.lower()} records found']})
        empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.info(f"Created empty sheet '{sheet_name}' - no records of this type")
    
    def _create_rpa_summary_sheet(self, writer: pd.ExcelWriter, result: DataComparisonResult):
        """Create RPA Summary sheet"""
        value_mismatches = result.comparison_df[result.comparison_df['Mismatch_Type'] == 'Value Mismatch']
        
        if value_mismatches.empty:
            summary_df = pd.DataFrame({'Message': ['No value mismatches found for RPA processing']})
            summary_df.to_excel(writer, sheet_name='RPA_Summary', index=False)
            return
        
        summary_data = self._build_rpa_summary_data(result)
        summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
        summary_df.to_excel(writer, sheet_name='RPA_Summary', index=False)
        
        logger.info("Created RPA_Summary sheet with processing statistics")
    
    def _build_rpa_summary_data(self, result: DataComparisonResult) -> list:
        """Build RPA summary data"""
        summary_data = []
        value_mismatches = result.comparison_df[result.comparison_df['Mismatch_Type'] == 'Value Mismatch']
        
        # Overall statistics
        summary_data.extend([
            ['OVERALL STATISTICS', ''],
            ['Total Value Mismatches', len(value_mismatches)],
            ['Companies Affected', result.summary.companies_affected],
            ['Total Values Missing from DB', result.summary.total_missing_values],
            ['Total Extra Values in DB', result.summary.total_extra_values],
            ['', '']
        ])
        
        # Company breakdown
        summary_data.append(['COMPANY BREAKDOWN', 'Mismatch Count'])
        if not value_mismatches.empty:
            company_counts = value_mismatches['Company'].value_counts()
            for company, count in company_counts.items():
                summary_data.append([company, count])
        
        # Dropdown field breakdown (show both extracted and DB field names)
        summary_data.extend([
            ['', ''],
            ['FIELD BREAKDOWN', 'Mismatch Count']
        ])
        
        if not value_mismatches.empty:
            # Show breakdown by original extracted field names if available
            if 'Original_Extracted_Field_Name' in value_mismatches.columns:
                field_counts = value_mismatches['Original_Extracted_Field_Name'].value_counts()
                for field, count in field_counts.items():
                    summary_data.append([f"Extracted Field: {field}", count])
            else:
                field_counts = value_mismatches['Dropdown_Name'].value_counts()
                for field, count in field_counts.items():
                    summary_data.append([f"Field: {field}", count])
        
        # Action breakdown
        summary_data.extend([
            ['', ''],
            ['RPA ACTIONS REQUIRED', 'Count']
        ])
        
        if not value_mismatches.empty:
            action_counts = self._calculate_action_counts(value_mismatches)
            for action, count in action_counts.items():
                summary_data.append([action, count])
        
        return summary_data
    
    def _calculate_action_counts(self, value_mismatches: pd.DataFrame) -> Dict[str, int]:
        """Calculate action counts for RPA summary"""
        insert_only = len(value_mismatches[
            (value_mismatches['Values_Only_Extracted'].apply(len) > 0) & 
            (value_mismatches['Values_Only_Database'].apply(len) == 0)
        ])
        
        review_only = len(value_mismatches[
            (value_mismatches['Values_Only_Extracted'].apply(len) == 0) & 
            (value_mismatches['Values_Only_Database'].apply(len) > 0)
        ])
        
        both_actions = len(value_mismatches[
            (value_mismatches['Values_Only_Extracted'].apply(len) > 0) & 
            (value_mismatches['Values_Only_Database'].apply(len) > 0)
        ])
        
        return {
            'INSERT_MISSING_VALUES': insert_only,
            'REVIEW_EXTRA_VALUES': review_only,
            'INSERT_AND_REVIEW': both_actions
        }
    
    def _log_export_statistics(self, result: DataComparisonResult):
        """Log export statistics with field name information"""
        mismatches = result.comparison_df[result.comparison_df['Mismatch_Type'] != 'Perfect Match']
        perfect_matches = result.comparison_df[result.comparison_df['Mismatch_Type'] == 'Perfect Match']
        value_mismatches = result.comparison_df[result.comparison_df['Mismatch_Type'] == 'Value Mismatch']
        
        logger.info(f"📊 FINAL EXPORT SUMMARY:")
        logger.info(f"  All_Results: {len(result.comparison_df)} records")
        logger.info(f"  Value_Mismatch (ENHANCED): {len(value_mismatches)} records")
        logger.info(f"  Perfect_Match: {len(perfect_matches)} records")
        logger.info(f"  Total mismatches: {len(mismatches)} records")
        
        # Log field name usage
        if 'Original_Extracted_Field_Name' in result.comparison_df.columns:
            unique_extracted_fields = result.comparison_df['Original_Extracted_Field_Name'].nunique()
            logger.info(f"  Unique extracted field names: {unique_extracted_fields}")
        
        if 'DB_Field_Display_Name' in result.comparison_df.columns:
            unique_db_fields = result.comparison_df['DB_Field_Display_Name'].nunique()
            logger.info(f"  Unique DB field names: {unique_db_fields}")