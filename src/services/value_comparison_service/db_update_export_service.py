import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from src.utils.logger import logger
from src.models.data_models import DataComparisonResult
from src.utils.load_yaml import DB_UPDATE_DIR
from src.config.constants import BROKER_PORTALS
from src.services.value_comparison_service.condition_validator import ConditionValidator
from src.services.value_comparison_service.mapping_service import MappingService
from src.services.value_comparison_service.business_nature_service import BusinessNatureService
from src.services.value_comparison_service.broker_commission_service import BrokerCommissionService
from src.services.value_comparison_service.iq_comparison_service import IQComparisonService

class DBUpdateExportService:
    """Handles database update focused export operations with broker-specific sheets only"""
    
    def __init__(self, broker_id: int, mapping_service: MappingService, iq_comparison_service: IQComparisonService = None):
        self.broker_id = broker_id
        self.mapping_service = mapping_service
        self.condition_validator = ConditionValidator(mapping_service=self.mapping_service)
        self.business_nature_service = BusinessNatureService(mapping_service=self.mapping_service)
        self.broker_commission_service = BrokerCommissionService(mapping_service=self.mapping_service)
        self.iq_comparison_service = iq_comparison_service  # NEW: Store IQ service reference

    def save_db_update_results(self, result: DataComparisonResult, tpa_comparison_df: pd.DataFrame = None, network_comparison_df: pd.DataFrame = None, iq_comparison_df: pd.DataFrame = None) -> Optional[str]:
        """Save DB update focused results to Excel file with broker-specific sheets only"""
        if result.comparison_df.empty:
            logger.warning("No comparison results to save for DB update")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Handle combined mode (all brokers)
        if self.broker_id == 0:
            filename = f"db_update_all_brokers_{timestamp}.xlsx"
        else:
            filename = f"db_update_broker_{self.broker_id}_{timestamp}.xlsx"
            
        save_path = Path(DB_UPDATE_DIR) / filename

        try:
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                # Create filtered comparison_df (excluding special care records)
                filtered_comparison_df = self._get_filtered_comparison_df(result)
                
                # NEW: Add IQ comparison data to filtered comparison if provided
                # if iq_comparison_df is not None and not iq_comparison_df.empty:
                #     enhanced_comparison_df = self._add_iq_comparison_to_main_comparison(filtered_comparison_df, iq_comparison_df)
                # else:
                #     enhanced_comparison_df = filtered_comparison_df
                
                enhanced_comparison_df = filtered_comparison_df
                
                # Create Value_Mismatch sheet (with special care records excluded + Business Nature + IQ)
                self._create_value_mismatch_sheet(writer, enhanced_comparison_df)
                
                # Create broker-specific sheets ONLY (with special care records excluded + IQ)
                self._create_broker_specific_sheets(writer, enhanced_comparison_df)  # Use enhanced_comparison_df

                # Add Business Nature Add/Delete sheets
                self.business_nature_service.create_business_nature_add_delete_sheets(writer, result)

                # Add Broker Commission Add/Delete sheets
                self.broker_commission_service.create_broker_commission_add_delete_sheets(writer, result)

                # Add Special Care sheet (separate from other sheets, excluding Sukoon)
                self._add_special_care_sheet(writer, result)

                # Add TPA Dropdown Comparison as a sheet if provided
                if tpa_comparison_df is not None and not tpa_comparison_df.empty:
                    tpa_comparison_df.to_excel(writer, sheet_name='TPA_Dropdown_Comparison', index=False)
                
                # Add Network Dropdown Comparison as a sheet if provided
                if network_comparison_df is not None and not network_comparison_df.empty:
                    network_comparison_df.to_excel(writer, sheet_name='Network_Dropdown_Comparison', index=False)
                
                # Add IQ Comparison sheet and Add/Delete sheets
                if self.iq_comparison_service and self.iq_comparison_service.df_iq_data is not None:
                    db_columns = self.iq_comparison_service.df_iq_data.columns.tolist()
                    if iq_comparison_df is not None and not iq_comparison_df.empty:
                        iq_comparison_df.to_excel(writer, sheet_name='IQ_Comparison', index=False)
                        self._create_iq_add_delete_sheets(writer, iq_comparison_df, db_columns)
                    else:
                        # If there's no comparison data, still create the empty sheets with correct headers
                        self._create_empty_iq_add_sheet(writer, db_columns)
                        self._create_empty_iq_delete_sheet(writer, db_columns)
            
            
            logger.info(f"Broker-specific DB Update results saved to: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Error saving DB update Excel file: {e}")
            return None

    def _add_iq_comparison_to_main_comparison(self, main_comparison_df: pd.DataFrame, iq_comparison_df: pd.DataFrame) -> pd.DataFrame:
        """Convert IQ comparison data to main comparison format and merge"""
        try:
            logger.info("Adding IQ comparison data to main comparison...")
            
            if iq_comparison_df.empty:
                logger.info("No IQ comparison data to add")
                return main_comparison_df
            
            # IQ comparison already follows standard format, just need to ensure columns match
            iq_converted_df = iq_comparison_df.copy()
            
            # Ensure all columns from main comparison exist in IQ data
            for col in main_comparison_df.columns:
                if col not in iq_converted_df.columns:
                    iq_converted_df[col] = ''
            
            # Reorder columns to match main comparison
            iq_converted_df = iq_converted_df[main_comparison_df.columns]
            
            # Combine with main comparison
            enhanced_df = pd.concat([main_comparison_df, iq_converted_df], ignore_index=True)
            logger.info(f"Added {len(iq_comparison_df)} IQ comparison records to main comparison")
            return enhanced_df
            
        except Exception as e:
            logger.error(f"Error adding IQ comparison to main comparison: {e}")
            return main_comparison_df
    
    def _get_filtered_comparison_df(self, result: DataComparisonResult) -> pd.DataFrame:
        """
        Get comparison dataframe with special care records, Business Nature records, and Broker Commission records excluded
        (for broker-specific sheets only)
        """
        # Create a copy to avoid modifying the original
        filtered_df = result.comparison_df.copy()
        original_count = len(filtered_df)
        
        # 1. Exclude Business Nature records from broker-specific sheets
        logger.info("Filtering out Business Nature records from broker-specific sheets...")
        business_nature_filter = filtered_df['Dropdown_Name'].str.contains(
            'Business.*Nature|Nature.*Business', case=False, na=False, regex=True
        )
        business_nature_count = business_nature_filter.sum()
        filtered_df = filtered_df[~business_nature_filter].copy()
        logger.info(f"Excluded {business_nature_count} Business Nature records from broker-specific sheets")
        
        # 2. Exclude Broker Commission records from broker-specific sheets
        logger.info("Filtering out Broker Commission records from broker-specific sheets...")
        broker_commission_filter = filtered_df['Dropdown_Name'].str.contains(
            'Broker.*Commission|Commission.*Broker', case=False, na=False, regex=True
        )
        broker_commission_count = broker_commission_filter.sum()
        filtered_df = filtered_df[~broker_commission_filter].copy()
        logger.info(f"Excluded {broker_commission_count} Broker Commission records from broker-specific sheets")
        
        # 3. Exclude special care records if they exist
        if hasattr(result, 'special_care_df') and not result.special_care_df.empty:
            logger.info(f"Filtering out special care records from comparison data...")
            
            # Create filter to exclude special care records
            special_care_filter = self._create_special_care_filter(
                filtered_df, 
                result.special_care_df
            )
            
            # Apply filter to exclude special care records
            special_care_count = special_care_filter.sum()
            filtered_df = filtered_df[~special_care_filter].copy()
            logger.info(f"Excluded {special_care_count} special care records from broker-specific sheets")
        else:
            logger.info("No special care records to exclude")
        
        total_removed = original_count - len(filtered_df)
        logger.info(f"Total excluded from broker-specific sheets: {total_removed} records")
        logger.info(f"Filtered comparison now has {len(filtered_df)} records for broker-specific Add/Delete operations")
        
        return filtered_df
    
    def _create_special_care_filter(self, comparison_df: pd.DataFrame, special_care_df: pd.DataFrame) -> pd.Series:
        """
        Create a boolean filter to identify special care records in the main comparison DataFrame
        """
        logger.info("Creating special care exclusion filter")
        
        # Initialize filter as all False
        special_care_filter = pd.Series([False] * len(comparison_df), index=comparison_df.index)
        
        if special_care_df.empty:
            return special_care_filter
        
        # Get unique combinations of company and fields from special care
        special_care_keys = set()
        for _, sc_row in special_care_df.iterrows():
            company = sc_row['Company']
            trigger_field = sc_row.get('Trigger_Field_Original', '')
            dependent_field = sc_row.get('Dependent_Field_Original', '')
            
            # Add context for more precise matching
            context_key = self._build_context_key(sc_row)
            
            # Add both trigger and dependent fields to exclusion list
            if trigger_field:
                special_care_keys.add((company, trigger_field, context_key))
            if dependent_field:
                special_care_keys.add((company, dependent_field, context_key))
        
        # Apply filter to comparison dataframe
        for _, comp_row in comparison_df.iterrows():
            company = comp_row['Company']
            dropdown_name = comp_row['Dropdown_Name']
            context_key = self._build_context_key(comp_row)
            
            # Check if this record matches any special care combination
            if (company, dropdown_name, context_key) in special_care_keys:
                special_care_filter.loc[comp_row.name] = True
        
        special_care_count = special_care_filter.sum()
        logger.info(f"Special care filter identified {special_care_count} records to exclude from Add/Delete sheets")
        
        return special_care_filter
    
    def _build_context_key(self, row: pd.Series) -> str:
        """Build a context key for more precise matching of special care records"""
        context_parts = []
        
        # Add context fields in a consistent order
        for field in ['TPA', 'Network', 'Region']:
            if field in row and pd.notna(row[field]) and str(row[field]).strip():
                context_parts.append(f"{field}:{str(row[field]).strip()}")
        
        return "|".join(context_parts) if context_parts else ""
    
    def _create_value_mismatch_sheet(self, writer: pd.ExcelWriter, comparison_df: pd.DataFrame):
        """Create Value Mismatch sheet (with special care records excluded) - includes Value Mismatch and Only in Extracted"""
        value_mismatches = comparison_df[
            comparison_df['Mismatch_Type'].isin(['Value Mismatch', 'Only in Extracted'])
        ]
        
        if value_mismatches.empty:
            empty_df = pd.DataFrame({'Message': ['No value mismatches found (excluding special care)']})
            empty_df.to_excel(writer, sheet_name='Value_Mismatch', index=False)
            return
        
        # Use the enhanced format with original field names
        export_cols = [
            'Company', 'TPA', 'Network', 'Region',
            'Original_Extracted_Field_Name',  # Use original extracted field name
            'DB_Field_Display_Name',          # Use DB field display name
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
        
        enhanced_export = value_mismatches[available_cols].copy()
        
        # Update column names to match expected format
        updated_column_mappings = [
            'Company', 'TPA', 'Network', 'Region',
            'Extracted_Field_Name',      # Renamed from Original_Extracted_Field_Name
            'DB_Field_Name',             # Renamed from DB_Field_Display_Name
            'Mismatch_Type',
            'All_Values_Extracted', 'All_Values_Database',
            'Only_in_Extracted', 'Only_in_Database', 'Common_Values'
        ]
        
        enhanced_export.columns = updated_column_mappings[:len(enhanced_export.columns)]
        
        # Add DB action columns - now handle all mismatch types
        enhanced_export['Values_to_INSERT_in_DB'] = enhanced_export.apply(
            lambda row: (
                row['All_Values_Extracted'] if row['Mismatch_Type'] == 'Only in Extracted' 
                else row['Only_in_Extracted'] if row['Mismatch_Type'] == 'Value Mismatch'
                else ''
            ), axis=1
        )
        enhanced_export['Values_to_DELETE_from_DB'] = enhanced_export.apply(
            lambda row: (
                row['Only_in_Database'] if row['Mismatch_Type'] == 'Value Mismatch'
                else ''
            ), axis=1
        )
        
        enhanced_export.to_excel(writer, sheet_name='Value_Mismatch', index=False)
    
    def _create_broker_specific_sheets(self, writer: pd.ExcelWriter, comparison_df: pd.DataFrame):
        """Create separate sheets for each broker and action type (excluding special care)"""
        
        # Get active brokers (those with portals defined)
        active_brokers = {broker: portals for broker, portals in BROKER_PORTALS.items() if portals}
        
        for broker_name, broker_portals in active_brokers.items():
            
            # Filter data for this broker's portals
            broker_data = comparison_df[comparison_df['Company'].isin(broker_portals)]
            
            if broker_data.empty:
                # Still create empty sheets for brokers with no data
                self._create_empty_broker_sheets(writer, broker_name)
                continue
            
            # Create Add Values sheet for this broker
            self._create_broker_add_values_sheet(writer, broker_data, broker_name)
            
            # Create Delete Values sheet for this broker
            self._create_broker_delete_values_sheet(writer, broker_data, broker_name)

    def _create_broker_add_values_sheet(self, writer: pd.ExcelWriter, broker_data: pd.DataFrame, broker_name: str):
        """Create Add Values sheet for specific broker with simplified columns (excluding special care)"""
        sheet_name = f"Add_Values-{broker_name}"
        
        # Include Value Mismatch and Only in Extracted for add operations
        value_mismatches = broker_data[
            broker_data['Mismatch_Type'].isin(['Value Mismatch', 'Only in Extracted'])
        ]
        
        if value_mismatches.empty:
            empty_df = pd.DataFrame({
                'Message': [f'No values to add for {broker_name} (excluding special care)'],
                'Broker': [broker_name if not str(broker_name).startswith("Broker ") else str(broker_name).replace("Broker ", "")],
                'Portals_Count': [len(BROKER_PORTALS.get(broker_name, []))]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
            return
        
        add_values_data = []
        
        for _, row in value_mismatches.iterrows():
            # For "Only in Extracted", add all Selection_Value_Extracted values
            if row['Mismatch_Type'] == 'Only in Extracted':
                values_to_add = row.get('Selection_Value_Extracted', [])
            else:
                # For "Value Mismatch", add only Values_Only_Extracted
                values_to_add = row.get('Values_Only_Extracted', [])
            
            if values_to_add and len(values_to_add) > 0:
                # Get the DB field display name for the dropdown name
                db_field_name = row.get('DB_Field_Display_Name', row.get('Dropdown_Name', ''))
                
                for value in values_to_add:
                    add_values_data.append({
                        'Broker': broker_name if not str(broker_name).startswith("Broker ") else str(broker_name).replace("Broker ", ""),
                        'Company': row.get('Company', ''),
                        'TPA': row.get('TPA', ''),
                        'Network': row.get('Network', ''),
                        'Region': row.get('Region', ''),
                        'Dropdown_Name': db_field_name,
                        'Selection_Value': value
                    })
        
        if add_values_data:
            add_values_df = pd.DataFrame(add_values_data)
            
            # Simplified required columns
            required_cols = ['Broker', 'Company', 'TPA', 'Network', 'Region', 'Dropdown_Name', 'Selection_Value']
            for col in required_cols:
                if col not in add_values_df.columns:
                    add_values_df[col] = ''
            
            add_values_df = add_values_df[required_cols]
            add_values_df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Create empty sheet if no add values after filtering
            empty_df = pd.DataFrame({
                'Message': [f'No values to add for {broker_name} (excluding special care)'],
                'Broker': [broker_name if not str(broker_name).startswith("Broker ") else str(broker_name).replace("Broker ", "")],
                'Portals_Count': [len(BROKER_PORTALS.get(broker_name, []))]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def _create_broker_delete_values_sheet(self, writer: pd.ExcelWriter, broker_data: pd.DataFrame, broker_name: str):
        """Create Delete Values sheet for specific broker with simplified columns (excluding special care)"""
        sheet_name = f"Delete_Values-{broker_name}"
        
        value_mismatches = broker_data[broker_data['Mismatch_Type'] == 'Value Mismatch']
        
        if value_mismatches.empty:
            empty_df = pd.DataFrame({
                'Message': [f'No values to delete for {broker_name} (excluding special care)'],
                'Broker': [broker_name if not str(broker_name).startswith("Broker ") else str(broker_name).replace("Broker ", "")],
                'Portals_Count': [len(BROKER_PORTALS.get(broker_name, []))]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
            return
        
        delete_values_data = []
        
        for _, row in value_mismatches.iterrows():
            values_to_delete = row.get('Values_Only_Database', [])
            
            if values_to_delete and len(values_to_delete) > 0:
                # Get the DB field display name for the dropdown name
                db_field_name = row.get('DB_Field_Display_Name', row.get('Dropdown_Name', ''))
                
                for value in values_to_delete:
                    delete_values_data.append({
                        'Broker': broker_name if not str(broker_name).startswith("Broker ") else str(broker_name).replace("Broker ", ""),
                        'Company': row.get('Company', ''),
                        'TPA': row.get('TPA', ''),
                        'Network': row.get('Network', ''),
                        'Region': row.get('Region', ''),
                        'Dropdown_Name': db_field_name,
                        'Selection_Value': value
                    })
        
        if delete_values_data:
            delete_values_df = pd.DataFrame(delete_values_data)
            
            # Simplified required columns
            required_cols = ['Broker', 'Company', 'TPA', 'Network', 'Region', 'Dropdown_Name', 'Selection_Value']
            for col in required_cols:
                if col not in delete_values_df.columns:
                    delete_values_df[col] = ''
            
            delete_values_df = delete_values_df[required_cols]
            delete_values_df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Create empty sheet if no delete values after filtering
            empty_df = pd.DataFrame({
                'Message': [f'No values to delete for {broker_name} (excluding special care)'],
                'Broker': [broker_name if not str(broker_name).startswith("Broker ") else str(broker_name).replace("Broker ", "")],
                'Portals_Count': [len(BROKER_PORTALS.get(broker_name, []))]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
   
    def _add_special_care_sheet(self, writer: pd.ExcelWriter, result: DataComparisonResult):
        """Add Special Care sheet using the proper ConditionValidator logic"""
        logger.info("Adding Special Care sheet using ConditionValidator")
        
        # Check if we already have special care results in the comparison result
        if hasattr(result, 'special_care_df') and not result.special_care_df.empty:
            logger.info(f"Using pre-computed special care results with {len(result.special_care_df)} records")
            # Add a note about special care exclusion
            special_care_with_note = result.special_care_df.copy()
            
            special_care_with_note.to_excel(writer, sheet_name='Special_Care', index=False)
            return
        
        # If no pre-computed results, check if we have the necessary data to create them
        if not hasattr(result, 'df_extracted') or not hasattr(result, 'df_database'):
            logger.warning("No extracted/database data available for special care validation")
            empty_df = pd.DataFrame({'Message': ['No data available for special care validation']})
            empty_df.to_excel(writer, sheet_name='Special_Care', index=False)
            return
        
        # Use the ConditionValidator to create the special care sheet
        try:
            special_care_df = self.condition_validator.create_special_care_sheet(
                result.df_extracted, 
                result.df_database
            )
            
            if not special_care_df.empty:
                logger.info(f"Created Special Care sheet with {len(special_care_df)} records")
                
                special_care_df.to_excel(writer, sheet_name='Special_Care', index=False)
            else:
                logger.info("No special care records found")
                empty_df = pd.DataFrame({'Message': ['No special care records found']})
                empty_df.to_excel(writer, sheet_name='Special_Care', index=False)
                
        except Exception as e:
            logger.error(f"Error creating Special Care sheet: {e}")
            error_df = pd.DataFrame({'Error': [f'Error creating special care sheet: {str(e)}']})
            error_df.to_excel(writer, sheet_name='Special_Care', index=False)
    
    def _create_empty_broker_sheets(self, writer: pd.ExcelWriter, broker_name: str):
        """Create empty sheets for brokers with no data"""
        # Empty Add Values sheet
        add_sheet_name = f"Add_Values-{broker_name}"
        empty_add_df = pd.DataFrame({
            'Message': [f'No values to add for {broker_name} (excluding special care)'],
            'Broker': [broker_name if not str(broker_name).startswith("Broker ") else str(broker_name).replace("Broker ", "")],
            'Portals_Count': [len(BROKER_PORTALS.get(broker_name, []))]
        })
        empty_add_df.to_excel(writer, sheet_name=add_sheet_name, index=False)
        
        # Empty Delete Values sheet
        delete_sheet_name = f"Delete_Values-{broker_name}"
        empty_delete_df = pd.DataFrame({
            'Message': [f'No values to delete for {broker_name} (excluding special care)'],
            'Broker': [broker_name if not str(broker_name).startswith("Broker ") else str(broker_name).replace("Broker ", "")],
            'Portals_Count': [len(BROKER_PORTALS.get(broker_name, []))]
        })
        empty_delete_df.to_excel(writer, sheet_name=delete_sheet_name, index=False)


    def _create_iq_add_delete_sheets(self, writer: pd.ExcelWriter, iq_comparison_df: pd.DataFrame, db_columns: List[str]):
        """Create separate Add IQ Values and Delete IQ Values sheets"""
        try:
            logger.info("Creating IQ Add/Delete sheets...")
            
            if not iq_comparison_df.empty and self.iq_comparison_service:
                add_iq_data = self.iq_comparison_service.prepare_iq_add_data(iq_comparison_df)
                delete_iq_data = self.iq_comparison_service.prepare_iq_delete_data(iq_comparison_df)

                if not add_iq_data.empty:
                    add_iq_data.to_excel(writer, sheet_name='Add_IQ_Values', index=False)
                    logger.info(f"Created Add_IQ_Values sheet with {len(add_iq_data)} records")
                else:
                    self._create_empty_iq_add_sheet(writer, db_columns)

                if not delete_iq_data.empty:
                    delete_iq_data.to_excel(writer, sheet_name='Delete_IQ_Values', index=False)
                    logger.info(f"Created Delete_IQ_Values sheet with {len(delete_iq_data)} records")
                else:
                    self._create_empty_iq_delete_sheet(writer, db_columns)
            else:
                self._create_empty_iq_add_sheet(writer, db_columns)
                self._create_empty_iq_delete_sheet(writer, db_columns)
            
            logger.info("IQ Add/Delete sheets created successfully")
            
        except Exception as e:
            logger.error(f"Error creating IQ Add/Delete sheets: {e}", exc_info=True)
            if self.iq_comparison_service and self.iq_comparison_service.df_iq_data is not None:
                db_columns = self.iq_comparison_service.df_iq_data.columns.tolist()
            else:
                db_columns = [] # Fallback
            self._create_empty_iq_add_sheet(writer, db_columns)
            self._create_empty_iq_delete_sheet(writer, db_columns)

    def _create_empty_iq_add_sheet(self, writer: pd.ExcelWriter, columns: List[str]):
        """Create empty Add IQ Values sheet with the correct wide-format headers"""
        empty_add_df = pd.DataFrame(columns=columns)
        empty_add_df.to_excel(writer, sheet_name='Add_IQ_Values', index=False)

    def _create_empty_iq_delete_sheet(self, writer: pd.ExcelWriter, columns: List[str]):
        """Create empty Delete IQ Values sheet with the correct wide-format headers"""
        empty_delete_df = pd.DataFrame(columns=columns)
        empty_delete_df.to_excel(writer, sheet_name='Delete_IQ_Values', index=False)
