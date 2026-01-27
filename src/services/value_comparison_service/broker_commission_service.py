"""
Broker Commission Comparison Service

This service handles all Broker Commission specific comparison logic and Excel sheet generation.
It provides specialized comparison algorithms for Broker Commission data that differ from
standard dropdown field comparisons.

Key Features:
- Specialized Broker Commission comparison logic excluding TPA/Network
- JSON array parsing for extracted values (handles JSON arrays from portal extraction)
- Broker Commission specific Add/Delete sheet generation  
- Integration with main comparison dataframes
- Broker information mapping for Broker Commission records
- HTML entity decoding and value normalization
- Only processes companies with extracted data (no database-only deletions)
- Prevents deletion suggestions when no Broker Commission data is extracted
"""

import pandas as pd
import numpy as np
import html
import traceback
from typing import List, Optional, Dict, Any
from src.utils.logger import logger
from src.models.data_models import DataComparisonResult
from src.config.constants import BROKER_PORTALS
# Apply the mapping service to align field names
from src.services.value_comparison_service.mapping_service import MappingService
from src.services.value_comparison_service.value_comparison_db import DataComparisonDBService

class BrokerCommissionService:
    """Handles Broker Commission specific comparison and export operations"""
    
    def __init__(self, mapping_service=None):
        """
        Initialize Broker Commission Service
        
        Args:
            mapping_service: Optional mapping service for field name alignment
        """
        self.mapping_service = mapping_service
    
    def compare_broker_commission_data(self, broker_commission_extracted: pd.DataFrame, 
                                     broker_commission_database: pd.DataFrame) -> pd.DataFrame:
        """
        Specialized comparison for Broker Commission data using simplified comparison logic
        
        This method differs from standard field comparison by:
        - Excluding TPA and Network from comparison logic (but keeping in output schema)
        - Only processing companies that have extracted data (no database-only deletions)
        - Using left join to prevent database-only companies from appearing
        - HTML entity decoding for proper value comparison
        
        Args:
            broker_commission_extracted: DataFrame with extracted Broker Commission data
            broker_commission_database: DataFrame with database Broker Commission data
            
        Returns:
            DataFrame with Broker Commission comparison results including mismatch types
        """
        try:
            # Ensure required columns exist in both datasets
            required_columns = ['Company', 'TPA', 'Network', 'Region', 'Dropdown_Name', 'Selection_Value', 'Field']
            
            # Process extracted data
            extracted_data = broker_commission_extracted.copy()
            for col in required_columns:
                if col not in extracted_data.columns:
                    if col == 'Region':
                        extracted_data[col] = 'Dubai'  # Default region
                    else:
                        extracted_data[col] = ''
            
            # Process database data
            database_data = broker_commission_database.copy()
            for col in required_columns:
                if col not in database_data.columns:
                    if col == 'Region':
                        database_data[col] = 'Dubai'  # Default region
                    else:
                        database_data[col] = ''
            # Remove TPA and Network from both datasets for comparison
            # But keep them in the final result for consistency with expected schema
            extracted_data_for_comparison = extracted_data.drop(columns=['TPA', 'Network'], errors='ignore')
            database_data_for_comparison = database_data.drop(columns=['TPA', 'Network'], errors='ignore')
            
            # Apply normalization to both datasets (use the comparison datasets without TPA/Network)
            extracted_data_for_comparison['Selection_Value_List'] = extracted_data_for_comparison['Selection_Value'].apply(self._normalize_selection_value)
            database_data_for_comparison['Selection_Value_List'] = database_data_for_comparison['Selection_Value'].apply(self._normalize_selection_value)
            
            # Group by merge columns for comparison (using standard field names)
            # Field name mapping is handled by the mapping service, no need for hardcoded normalization
            merge_columns = ['Company', 'Region', 'Dropdown_Name']
            # Group extracted data - combine all lists for each group
            extracted_grouped = extracted_data_for_comparison.groupby(merge_columns)['Selection_Value_List'].apply(self._combine_lists).reset_index()
            extracted_grouped.rename(columns={'Selection_Value_List': 'Selection_Value_Extracted'}, inplace=True)
            # Group database data  
            database_grouped = database_data_for_comparison.groupby(merge_columns)['Selection_Value_List'].apply(self._combine_lists).reset_index()
            database_grouped.rename(columns={'Selection_Value_List': 'Selection_Value_Database'}, inplace=True)
            # FOR BROKER COMMISSION: Only merge on companies that have extracted data
            # This prevents database-only companies from appearing in delete operations
            # Use 'left' join to only include companies present in extracted data
            comparison = pd.merge(
                extracted_grouped, 
                database_grouped, 
                on=merge_columns, 
                how='left'
            )
            # Handle missing values - convert NaN to empty lists
            comparison['Selection_Value_Extracted'] = comparison['Selection_Value_Extracted'].apply(self._ensure_list)
            comparison['Selection_Value_Database'] = comparison['Selection_Value_Database'].apply(self._ensure_list)
            # Calculate differences
            comparison['Values_Only_Extracted'] = comparison.apply(
                lambda row: sorted(set(row['Selection_Value_Extracted']) - set(row['Selection_Value_Database'])), 
                axis=1
            )
            comparison['Values_Only_Database'] = comparison.apply(
                lambda row: sorted(set(row['Selection_Value_Database']) - set(row['Selection_Value_Extracted'])), 
                axis=1
            )
            comparison['Values_Common'] = comparison.apply(
                lambda row: sorted(set(row['Selection_Value_Extracted']) & set(row['Selection_Value_Database'])), 
                axis=1
            )
            
            # Determine mismatch type
            comparison['Mismatch_Type'] = comparison.apply(self._get_mismatch_type, axis=1)
            
            # Add string versions for display/export purposes only when needed
            comparison['Selection_Value_Extracted_Str'] = comparison['Selection_Value_Extracted'].apply(lambda x: ', '.join(x) if x else '')
            comparison['Selection_Value_Database_Str'] = comparison['Selection_Value_Database'].apply(lambda x: ', '.join(x) if x else '')
            comparison['Values_Only_Extracted_Str'] = comparison['Values_Only_Extracted'].apply(lambda x: ', '.join(x) if x else '')
            comparison['Values_Only_Database_Str'] = comparison['Values_Only_Database'].apply(lambda x: ', '.join(x) if x else '')
            comparison['Values_Common_Str'] = comparison['Values_Common'].apply(lambda x: ', '.join(x) if x else '')
            
            # Filter to only mismatched records - ensure proper comparison
            try:
                mismatched = comparison[comparison['Mismatch_Type'] != 'Match'].copy()
            except ValueError as e:
                logger.error(f"Error filtering Mismatch_Type: {e}")
                # If filtering fails, manually filter
                mismatched_indices = []
                for idx, row in comparison.iterrows():
                    mismatch_type = row['Mismatch_Type']
                    if isinstance(mismatch_type, str) and mismatch_type != 'Match':
                        mismatched_indices.append(idx)
                mismatched = comparison.loc[mismatched_indices].copy() if mismatched_indices else pd.DataFrame()
            
            # Add TPA and Network columns back to the result with default values for consistency
            # This ensures the output schema matches what's expected downstream
            mismatched['TPA'] = 'N/A'  # Default value since we excluded from comparison
            mismatched['Network'] = 'N/A'  # Default value since we excluded from comparison
            
            # Add DB_Field_Display_Name for consistency with regular broker sheets
            # Use the original Dropdown_Name as provided by the mapping service
            mismatched['DB_Field_Display_Name'] = mismatched['Dropdown_Name']
            
            return mismatched
            
        except Exception as e:
            logger.error(f"Error during Broker Commission comparison: {e}\n{traceback.format_exc()}")
            return pd.DataFrame()
    
    def _normalize_selection_value(self, value):
        """Convert various value formats to list of strings (no HTML entity decoding, no strip)"""
        try:
            # Handle arrays/lists first to avoid pd.isna() array ambiguity
            if isinstance(value, (list, tuple, np.ndarray)):
                cleaned_values = []
                for v in value:
                    val_str = str(v)
                    if val_str and val_str.lower() != 'nan':
                        cleaned_values.append(val_str)
                return cleaned_values
            elif pd.isna(value):
                return []
            else:
                val_str = str(value)
                if val_str and val_str.lower() != 'nan':
                    return [val_str]
                return []
        except Exception as e:
            return []
    
    def _combine_lists(self, series):
        """Group extracted data - combine all lists for each group"""
        all_values = []
        for value_list in series:
            all_values.extend(value_list)
        return sorted(set(all_values))  # Remove duplicates and sort
    
    def _ensure_list(self, value):
        """Ensure value is a list, handling NaN and arrays properly"""
        try:
            if isinstance(value, (list, tuple)):
                return list(value)
            elif isinstance(value, np.ndarray):
                return value.tolist()
            elif pd.isna(value):
                return []
            else:
                return []
        except Exception as e:
            return []
    
    def _get_mismatch_type(self, row):
        """Determine mismatch type for Broker Commission comparison"""
        try:
            has_extracted_only = len(row['Values_Only_Extracted']) > 0
            has_database_only = len(row['Values_Only_Database']) > 0
            
            if has_extracted_only and has_database_only:
                return 'Both Actions Required'
            elif has_extracted_only:
                return 'Insert Only'
            elif has_database_only:
                return 'Review Only'
            else:
                return 'Match'
        except Exception as e:
            logger.error(f"Error in get_mismatch_type for row: {e}")
            return 'Error'
    
    def add_broker_info_to_broker_commission(self, broker_commission_df: pd.DataFrame) -> pd.DataFrame:
        """Add broker information to Broker Commission comparison data"""
        # Add broker information based on company mapping
        broker_commission_df['Broker_ID'] = broker_commission_df['Company'].apply(self._get_broker_id_for_company)
        broker_commission_df['Broker_Name'] = broker_commission_df['Company'].apply(self._get_broker_name_for_company)
        
        return broker_commission_df
    
    def _get_broker_name_for_company(self, company: str) -> str:
        """Get broker name for a given company"""
        for broker_name, portals in BROKER_PORTALS.items():
            if company in portals:
                return broker_name
        return "Unknown"
    
    def _get_broker_id_for_company(self, company: str) -> int:
        """Get broker ID for a given company"""
        for broker_id, (broker_name, portals) in enumerate(BROKER_PORTALS.items(), 1):
            if company in portals:
                return broker_id
        return 0  # Unknown broker
    
    def create_broker_commission_add_values_sheet(self, writer, broker_commission_data: pd.DataFrame):
        """Create Add Values sheet for Broker Commission with simplified columns"""
        sheet_name = "Add_Values-Broker_Commission"
        # Include Insert Only and Both Actions Required for add operations (map from Broker Commission types)
        value_mismatches = broker_commission_data[
            broker_commission_data['Mismatch_Type'].isin(['Insert Only', 'Both Actions Required'])
        ]
        if value_mismatches.empty:
            empty_df = pd.DataFrame({
                'Message': ['No Broker Commission values to add'],
                'Record_Count': [0]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
            return
        add_values_data = []
        for _, row in value_mismatches.iterrows():
            values_to_add = row.get('Values_Only_Extracted', [])
            if values_to_add and len(values_to_add) > 0:
                if isinstance(values_to_add, list):
                    values_list = values_to_add
                elif isinstance(values_to_add, str):
                    values_list = [v for v in values_to_add.split(',') if v]
                else:
                    values_list = [str(values_to_add)]
                db_field_name = row.get('DB_Field_Display_Name', row.get('Dropdown_Name', ''))
                for value in values_list:
                    add_values_data.append({
                        'Company': row.get('Company', ''),
                        'TPA': row.get('TPA', ''),
                        'Network': row.get('Network', ''),
                        'Region': row.get('Region', ''),
                        'Dropdown_Name': db_field_name,
                        'Selection_Value': value
                    })
        if add_values_data:
            add_values_df = pd.DataFrame(add_values_data)
            required_cols = ['Company', 'TPA', 'Network', 'Region', 'Dropdown_Name', 'Selection_Value']
            for col in required_cols:
                if col not in add_values_df.columns:
                    add_values_df[col] = ''
            add_values_df = add_values_df[required_cols]
            add_values_df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            empty_df = pd.DataFrame({
                'Message': ['No Broker Commission values to add after filtering'],
                'Record_Count': [0]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def create_broker_commission_delete_values_sheet(self, writer, broker_commission_data: pd.DataFrame):
        """Create Delete Values sheet for Broker Commission with simplified columns"""
        sheet_name = "Delete_Values-Broker_Commission"
        # Include Review Only and Both Actions Required for delete operations (map from Broker Commission types)
        value_mismatches = broker_commission_data[
            broker_commission_data['Mismatch_Type'].isin(['Review Only', 'Both Actions Required'])
        ]
        if value_mismatches.empty:
            empty_df = pd.DataFrame({
                'Message': ['No Broker Commission values to delete'],
                'Record_Count': [0]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
            return
        delete_values_data = []
        for _, row in value_mismatches.iterrows():
            values_to_delete = row.get('Values_Only_Database', [])
            if values_to_delete and len(values_to_delete) > 0:
                if isinstance(values_to_delete, list):
                    values_list = values_to_delete
                elif isinstance(values_to_delete, str):
                    values_list = [v for v in values_to_delete.split(',') if v]
                else:
                    values_list = [str(values_to_delete)]
                db_field_name = row.get('DB_Field_Display_Name', row.get('Dropdown_Name', ''))
                for value in values_list:
                    delete_values_data.append({
                        'Company': row.get('Company', ''),
                        'TPA': row.get('TPA', ''),
                        'Network': row.get('Network', ''),
                        'Region': row.get('Region', ''),
                        'Dropdown_Name': db_field_name,
                        'Selection_Value': value
                    })
        if delete_values_data:
            delete_values_df = pd.DataFrame(delete_values_data)
            required_cols = ['Company', 'TPA', 'Network', 'Region', 'Dropdown_Name', 'Selection_Value']
            for col in required_cols:
                if col not in delete_values_df.columns:
                    delete_values_df[col] = ''
            delete_values_df = delete_values_df[required_cols]
            delete_values_df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            empty_df = pd.DataFrame({
                'Message': ['No Broker Commission values to delete after filtering'],
                'Record_Count': [0]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def create_empty_broker_commission_sheets(self, writer, error_msg: str = None):
        """Create empty Broker Commission Add/Delete sheets"""
        message = error_msg if error_msg else 'No Broker Commission data available'
        
        # Empty Add Values sheet
        empty_add_df = pd.DataFrame({
            'Message': [f'{message} - Add Values'],
            'Broker': ['Broker Commission'],
            'Record_Count': [0]
        })
        empty_add_df.to_excel(writer, sheet_name='Add_Values-Broker_Commission', index=False)
        
        # Empty Delete Values sheet
        empty_delete_df = pd.DataFrame({
            'Message': [f'{message} - Delete Values'],
            'Broker': ['Broker Commission'],
            'Record_Count': [0]
        })
        empty_delete_df.to_excel(writer, sheet_name='Delete_Values-Broker_Commission', index=False)
    
    def create_broker_commission_add_delete_sheets(self, writer, result: DataComparisonResult):
        """Create separate Add Values and Delete Values sheets for Broker Commission"""
        # Check if we have the raw dataframes needed for Broker Commission comparison
        if not hasattr(result, 'df_extracted') or not hasattr(result, 'df_database'):
            self.create_empty_broker_commission_sheets(writer, "No raw data available")
            return

        try:
            # Filter raw dataframes for Broker Commission records
            broker_commission_extracted = result.df_extracted[
                result.df_extracted['Dropdown_Name'].str.contains('Broker.*Commission|Commission.*Broker', case=False, na=False, regex=True)
            ].copy()
            
            broker_commission_database = result.df_database[
                result.df_database['Dropdown_Name'].str.contains('Broker.*Commission|Broker_Commission|Commission.*Broker', case=False, na=False, regex=True)
            ].copy()
            
            if broker_commission_extracted.empty and broker_commission_database.empty:
                self.create_empty_broker_commission_sheets(writer, "No Broker Commission records found")
                return
            
        # Apply mapping service to Broker Commission extracted data to align field names

            # Get the mapping service instance
            db_service = DataComparisonDBService()
            mapping_service = MappingService()
            
            # Load mappings from database
            with db_service:
                (df_database,
                    df_tpa_dropdowns,
                    df_network_dropdowns,
                    df_iq_data_plans,  # NEW: Include IQ data (even though not used)
                    direct_mappings, 
                    global_request_mappings, 
                    company_specific_mappings, 
                    dropdown_mappings,
                    company_specific_direct_mappings) = db_service.fetch_all_data_with_mappings()
            
            mapping_service.load_mappings(
                direct_mappings, 
                global_request_mappings, 
                company_specific_mappings, 
                dropdown_mappings,
                company_specific_direct_mappings
            )
            
            # Apply mappings to broker commission extracted data
            broker_commission_extracted_mapped, _ = mapping_service.apply_mappings_for_comparison(broker_commission_extracted)
            
            # Use the mapped data for comparison
            broker_commission_extracted = broker_commission_extracted_mapped
            
            # Perform proper Broker Commission comparison (excluding TPA/Network)
            broker_commission_comparison = self.compare_broker_commission_data(
                broker_commission_extracted, 
                broker_commission_database
            )
            
            if broker_commission_comparison.empty:
                self.create_empty_broker_commission_sheets(writer, "No Broker Commission comparison results")
                return
            
            # Add broker information to Broker Commission data
            broker_commission_comparison = self.add_broker_info_to_broker_commission(broker_commission_comparison)
            
            # Create Add Values sheet for Broker Commission
            self.create_broker_commission_add_values_sheet(writer, broker_commission_comparison)
            
            # Create Delete Values sheet for Broker Commission
            self.create_broker_commission_delete_values_sheet(writer, broker_commission_comparison)
            
            
        except Exception as e:
            logger.error(f"Error creating Broker Commission Add/Delete sheets: {e}")
            self.create_empty_broker_commission_sheets(writer, f"Error: {str(e)}")
    
    def format_broker_commission_for_main_comparison(self, broker_commission_df: pd.DataFrame) -> pd.DataFrame:
        """
        Format Broker Commission comparison results to match the main comparison dataframe structure
        """
        if broker_commission_df.empty:
            return pd.DataFrame()
        
        try:
            # Create a copy and map Broker Commission mismatch types to main comparison types
            formatted_df = broker_commission_df.copy()
            
            # Map Broker Commission mismatch types to main comparison types
            mismatch_type_mapping = {
                'Insert Only': 'Only in Extracted',
                'Review Only': 'Only in Database', 
                'Both Actions Required': 'Value Mismatch'
            }
            
            formatted_df['Mismatch_Type'] = formatted_df['Mismatch_Type'].map(mismatch_type_mapping).fillna(formatted_df['Mismatch_Type'])
            
            # Ensure required columns exist and are in the right format
            required_columns = [
                'Company', 'TPA', 'Network', 'Region', 'Dropdown_Name', 'Mismatch_Type',
                'Selection_Value_Extracted', 'Selection_Value_Database',
                'Values_Only_Extracted', 'Values_Only_Database', 'Values_Common'
            ]
            
            for col in required_columns:
                if col not in formatted_df.columns:
                    if col in ['TPA', 'Network']:
                        formatted_df[col] = 'N/A'  # Broker Commission doesn't use TPA/Network
                    else:
                        formatted_df[col] = ''
            
            # Add original field name for Broker Commission (for display in Value_Mismatch)
            formatted_df['Original_Extracted_Field_Name'] = 'Broker Commission'
            formatted_df['DB_Field_Display_Name'] = 'Broker Commission'
            
            # Use the string versions for display in Value_Mismatch sheet
            # The list data should already be intact, just use string versions for export
            formatted_df['Values_String_Extracted'] = formatted_df.get('Selection_Value_Extracted_Str', formatted_df.get('Selection_Value_Extracted', ''))
            formatted_df['Values_String_Database'] = formatted_df.get('Selection_Value_Database_Str', formatted_df.get('Selection_Value_Database', ''))
            formatted_df['Values_Only_Extracted_Str'] = formatted_df.get('Values_Only_Extracted_Str', formatted_df.get('Values_Only_Extracted', ''))
            formatted_df['Values_Only_Database_Str'] = formatted_df.get('Values_Only_Database_Str', formatted_df.get('Values_Only_Database', ''))
            formatted_df['Values_Common_Str'] = formatted_df.get('Values_Common_Str', formatted_df.get('Values_Common', ''))
            
            return formatted_df
            
        except Exception as e:
            logger.error(f"Error formatting Broker Commission results: {e}")
            return pd.DataFrame()
    
    def add_broker_commission_to_comparison(self, comparison_df: pd.DataFrame, result: DataComparisonResult) -> pd.DataFrame:
        """
        Add Broker Commission comparison results to the main comparison dataframe for inclusion in Value_Mismatch sheet
        """
        try:
            # Check if we have the raw dataframes needed for Broker Commission comparison
            if not hasattr(result, 'df_extracted') or not hasattr(result, 'df_database'):
                return comparison_df
            
            # Filter raw dataframes for Broker Commission records
            broker_commission_extracted = result.df_extracted[
                result.df_extracted['Dropdown_Name'].str.contains('Broker.*Commission|Commission.*Broker', case=False, na=False, regex=True)
            ].copy()
            
            broker_commission_database = result.df_database[
                result.df_database['Dropdown_Name'].str.contains('Broker.*Commission|Broker_Commission|Commission.*Broker', case=False, na=False, regex=True)
            ].copy()
            
            if broker_commission_extracted.empty and broker_commission_database.empty:
                return comparison_df
            
            # Get Broker Commission comparison results
            broker_commission_comparison = self.compare_broker_commission_data(
                broker_commission_extracted, 
                broker_commission_database
            )
            
            if broker_commission_comparison.empty:
                return comparison_df
            
            # Transform Broker Commission results to match main comparison format
            broker_commission_formatted = self.format_broker_commission_for_main_comparison(broker_commission_comparison)
            
            if not broker_commission_formatted.empty:
                # Combine with main comparison
                combined_comparison = pd.concat([comparison_df, broker_commission_formatted], ignore_index=True)
                return combined_comparison
            else:
                return comparison_df
                
        except Exception as e:
            logger.error(f"Error adding Broker Commission to main comparison: {e}")
            return comparison_df
