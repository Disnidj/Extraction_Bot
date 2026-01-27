"""
Business Nature Comparison Service

This service handles all Business Nature specific comparison logic and Excel sheet generation.
It provides specialized comparison algorithms for Business Nature data that differ from
standard dropdown field comparisons.

Key Features:
- Specialized Business Nature comparison logic excluding TPA/Network
- Business Nature specific Add/Delete sheet generation
- Integration with main comparison dataframes
- Broker information mapping for Business Nature records
- HTML entity decoding and value normalization
"""

import pandas as pd
import numpy as np
import html
import traceback
from typing import List, Optional, Dict, Any
from src.utils.logger import logger
from src.models.data_models import DataComparisonResult
from src.config.constants import BROKER_PORTALS


class BusinessNatureService:
    """Handles Business Nature specific comparison and export operations"""
    
    def __init__(self, mapping_service=None):
        """
        Initialize Business Nature Service
        
        Args:
            mapping_service: Optional mapping service for field name alignment
        """
        self.mapping_service = mapping_service
    
    def compare_business_nature_data(self, business_nature_extracted: pd.DataFrame, 
                                   business_nature_database: pd.DataFrame) -> pd.DataFrame:
        """
        Specialized comparison for Business Nature data using simplified comparison logic
        
        This method differs from standard field comparison by:
        - Excluding TPA and Network from comparison logic (but keeping in output schema)
        - Only processing companies that have extracted data (no database-only deletions)
        - Using left join to prevent database-only companies from appearing
        - HTML entity decoding for proper value comparison
        
        Args:
            business_nature_extracted: DataFrame with extracted Business Nature data
            business_nature_database: DataFrame with database Business Nature data
            
        Returns:
            DataFrame with Business Nature comparison results including mismatch types
        """
        try:
            required_columns = ['Company', 'TPA', 'Network', 'Region', 'Dropdown_Name', 'Selection_Value', 'Field']
            # Process extracted data
            extracted_data = business_nature_extracted.copy()
            for col in required_columns:
                if col not in extracted_data.columns:
                    if col == 'Region':
                        extracted_data[col] = 'Dubai'  # Default region
                    else:
                        extracted_data[col] = ''
            # Process database data
            database_data = business_nature_database.copy()
            for col in required_columns:
                if col not in database_data.columns:
                    if col == 'Region':
                        database_data[col] = 'Dubai'  # Default region
                    else:
                        database_data[col] = ''
            # Remove TPA and Network from both datasets for comparison
            extracted_data_for_comparison = extracted_data.drop(columns=['TPA', 'Network'], errors='ignore')
            database_data_for_comparison = database_data.drop(columns=['TPA', 'Network'], errors='ignore')

            # Apply normalization to both datasets (use the comparison datasets without TPA/Network)
            extracted_data_for_comparison['Selection_Value_List'] = extracted_data_for_comparison['Selection_Value'].apply(self._normalize_selection_value)
            database_data_for_comparison['Selection_Value_List'] = database_data_for_comparison['Selection_Value'].apply(self._normalize_selection_value)

            # Group by merge columns for comparison (using standard field names)
            merge_columns = ['Company', 'Region', 'Dropdown_Name']

            # Group extracted data - combine all lists for each group
            extracted_grouped = extracted_data_for_comparison.groupby(merge_columns)['Selection_Value_List'].apply(self._combine_lists).reset_index()
            extracted_grouped.rename(columns={'Selection_Value_List': 'Selection_Value_Extracted'}, inplace=True)

            # Group database data  
            database_grouped = database_data_for_comparison.groupby(merge_columns)['Selection_Value_List'].apply(self._combine_lists).reset_index()
            database_grouped.rename(columns={'Selection_Value_List': 'Selection_Value_Database'}, inplace=True)


            # FOR BUSINESS NATURE: Only merge on companies that have extracted data
            comparison = pd.merge(
                extracted_grouped, 
                database_grouped, 
                on=merge_columns, 
                how='left'
            )

            # Handle missing values - convert NaN to empty lists
            comparison['Selection_Value_Extracted'] = comparison['Selection_Value_Extracted'].apply(self._ensure_list)
            comparison['Selection_Value_Database'] = comparison['Selection_Value_Database'].apply(self._ensure_list)
            def compare_row(row):
                extracted = row['Selection_Value_Extracted']
                database = row['Selection_Value_Database']
                only_extracted = sorted(set(extracted) - set(database))
                only_database = sorted(set(database) - set(extracted))
                common = sorted(set(extracted) & set(database))
                return only_extracted, only_database, common

            diffs = comparison.apply(compare_row, axis=1, result_type='expand')
            comparison['Values_Only_Extracted'] = diffs[0]
            comparison['Values_Only_Database'] = diffs[1]
            comparison['Values_Common'] = diffs[2]

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
                mismatched_indices = []
                for idx, row in comparison.iterrows():
                    mismatch_type = row['Mismatch_Type']
                    if isinstance(mismatch_type, str) and mismatch_type != 'Match':
                        mismatched_indices.append(idx)
                mismatched = comparison.loc[mismatched_indices].copy() if mismatched_indices else pd.DataFrame()

            # Add TPA and Network columns back to the result with default values for consistency
            mismatched['TPA'] = 'N/A'  # Default value since we excluded from comparison

            mismatched['Network'] = 'N/A'  # Default value since we excluded from comparison
            # Add DB_Field_Display_Name for consistency with regular broker sheets
            
            mismatched['DB_Field_Display_Name'] = mismatched['Dropdown_Name']
            return mismatched
        except Exception as e:
            logger.error(f"Error during Business Nature comparison: {e}\n{traceback.format_exc()}")
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
            logger.warning(f"Error normalizing selection value {value}: {e}")
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
            logger.warning(f"Error ensuring list for value {value}: {e}")
            return []
    
    def _get_mismatch_type(self, row):
        """Determine mismatch type for Business Nature comparison"""
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
            logger.error(f"Row Values_Only_Extracted type: {type(row['Values_Only_Extracted'])}, value: {row['Values_Only_Extracted']}")
            logger.error(f"Row Values_Only_Database type: {type(row['Values_Only_Database'])}, value: {row['Values_Only_Database']}")
            return 'Error'
    
    def add_broker_info_to_business_nature(self, business_nature_df: pd.DataFrame) -> pd.DataFrame:
        """Add broker information to Business Nature comparison data"""
        logger.info("Adding broker information to Business Nature data...")
        
        # Add broker information based on company mapping
        business_nature_df['Broker_ID'] = business_nature_df['Company'].apply(self._get_broker_id_for_company)
        business_nature_df['Broker_Name'] = business_nature_df['Company'].apply(self._get_broker_name_for_company)
        
        return business_nature_df
    
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
    
    def create_business_nature_add_values_sheet(self, writer, business_nature_data: pd.DataFrame):
        """Create Add Values sheet for Business Nature with simplified columns"""
        sheet_name = "Add_Values-Business_Nature"

        # Only add values that are in Values_Only_Extracted (not in both extracted and db)
        value_mismatches = business_nature_data[
            business_nature_data['Mismatch_Type'].isin(['Insert Only', 'Both Actions Required'])
        ]

        if value_mismatches.empty:
            empty_df = pd.DataFrame({
                'Message': ['No Business Nature values to add'],
                'Record_Count': [0]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
            return
        add_values_data = []
        for _, row in value_mismatches.iterrows():
            # Always use Values_Only_Extracted for add sheet
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
            logger.info(f"Created Business Nature Add Values sheet with {len(add_values_df)} records")
        else:
            empty_df = pd.DataFrame({
                'Message': ['No Business Nature values to add after filtering'],
                'Record_Count': [0]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def create_business_nature_delete_values_sheet(self, writer, business_nature_data: pd.DataFrame):
        """Create Delete Values sheet for Business Nature with simplified columns"""
        sheet_name = "Delete_Values-Business_Nature"
        
        # Include Review Only and Both Actions Required for delete operations (map from Business Nature types)
        value_mismatches = business_nature_data[
            business_nature_data['Mismatch_Type'].isin(['Review Only', 'Both Actions Required'])
        ]
        
        if value_mismatches.empty:
            empty_df = pd.DataFrame({
                'Message': ['No Business Nature values to delete'],
                'Record_Count': [0]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
            return
        delete_values_data = []
        for _, row in value_mismatches.iterrows():
            if row['Mismatch_Type'] == 'Review Only':
                values_to_delete = row.get('Selection_Value_Database', [])
            else:
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
            logger.info(f"Created Business Nature Delete Values sheet with {len(delete_values_df)} records")
        else:
            empty_df = pd.DataFrame({
                'Message': ['No Business Nature values to delete after filtering'],
                'Record_Count': [0]
            })
            empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def create_empty_business_nature_sheets(self, writer, error_msg: str = None):
        """Create empty Business Nature Add/Delete sheets"""
        message = error_msg if error_msg else 'No Business Nature data available'
        
        # Empty Add Values sheet
        empty_add_df = pd.DataFrame({
            'Message': [f'{message} - Add Values'],
            'Broker': ['Business Nature'],
            'Record_Count': [0]
        })
        empty_add_df.to_excel(writer, sheet_name='Add_Values-Business_Nature', index=False)
        
        # Empty Delete Values sheet
        empty_delete_df = pd.DataFrame({
            'Message': [f'{message} - Delete Values'],
            'Broker': ['Business Nature'],
            'Record_Count': [0]
        })
        empty_delete_df.to_excel(writer, sheet_name='Delete_Values-Business_Nature', index=False)
    
    def create_business_nature_add_delete_sheets(self, writer, result: DataComparisonResult):
        """Create separate Add Values and Delete Values sheets for Business Nature"""
        logger.info("Creating Business Nature Add/Delete sheets using proper comparison...")
        
        # Check if we have the raw dataframes needed for Business Nature comparison
        if not hasattr(result, 'df_extracted') or not hasattr(result, 'df_database'):
            logger.warning("No raw dataframes available for Business Nature comparison")
            self.create_empty_business_nature_sheets(writer, "No raw data available")
            return

        try:
            # Filter raw dataframes for Business Nature records
            business_nature_extracted = result.df_extracted[
                result.df_extracted['Dropdown_Name'].str.contains('Business.*Nature|Nature.*Business', case=False, na=False, regex=True)
            ].copy()
            
            business_nature_database = result.df_database[
                result.df_database['Dropdown_Name'].str.contains('Business.*Nature|Business_Nature|Nature.*Business', case=False, na=False, regex=True)
            ].copy()
            
            logger.info(f"Found {len(business_nature_extracted)} extracted and {len(business_nature_database)} database Business Nature records")
            
            if business_nature_extracted.empty and business_nature_database.empty:
                logger.warning("No Business Nature records found in raw data")
                self.create_empty_business_nature_sheets(writer, "No Business Nature records found")
                return
            
            # CRITICAL FIX: Apply mapping service to Business Nature extracted data to align field names
            if not business_nature_extracted.empty and self.mapping_service:
                logger.info("Applying mapping service to Business Nature extracted data...")
                
                # Apply the mapping service to align field names
                from src.services.value_comparison_service.mapping_service import MappingService
                from src.services.value_comparison_service.value_comparison_db import DataComparisonDBService
                
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
                
                # Apply mappings to business nature extracted data
                business_nature_extracted_mapped, _ = mapping_service.apply_mappings_for_comparison(business_nature_extracted)
                
                # Use the mapped data for comparison
                business_nature_extracted = business_nature_extracted_mapped
            
            # Perform proper Business Nature comparison (excluding TPA/Network)
            business_nature_comparison = self.compare_business_nature_data(
                business_nature_extracted, 
                business_nature_database
            )
            
            if business_nature_comparison.empty:
                logger.warning("Business Nature comparison returned no results")
                self.create_empty_business_nature_sheets(writer, "No Business Nature comparison results")
                return
            
            # Add broker information to Business Nature data
            business_nature_comparison = self.add_broker_info_to_business_nature(business_nature_comparison)
            
            # Create Add Values sheet for Business Nature
            self.create_business_nature_add_values_sheet(writer, business_nature_comparison)
            
            # Create Delete Values sheet for Business Nature
            self.create_business_nature_delete_values_sheet(writer, business_nature_comparison)
            
            logger.info("Business Nature Add/Delete sheets created successfully using proper comparison")
            
        except Exception as e:
            logger.error(f"Error creating Business Nature Add/Delete sheets: {e}")
            self.create_empty_business_nature_sheets(writer, f"Error: {str(e)}")
    
    def format_business_nature_for_main_comparison(self, business_nature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Format Business Nature comparison results to match the main comparison dataframe structure
        """
        if business_nature_df.empty:
            return pd.DataFrame()
        
        try:
            # Create a copy and map Business Nature mismatch types to main comparison types
            formatted_df = business_nature_df.copy()
            
            # Map Business Nature mismatch types to main comparison types
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
                        formatted_df[col] = 'N/A'  # Business Nature doesn't use TPA/Network
                    else:
                        formatted_df[col] = ''
            
            # Add original field name for Business Nature (for display in Value_Mismatch)
            formatted_df['Original_Extracted_Field_Name'] = 'Business Nature'
            formatted_df['DB_Field_Display_Name'] = 'Business Nature'
            
            # Use the string versions for display in Value_Mismatch sheet
            # The list data should already be intact, just use string versions for export
            formatted_df['Values_String_Extracted'] = formatted_df.get('Selection_Value_Extracted_Str', formatted_df.get('Selection_Value_Extracted', ''))
            formatted_df['Values_String_Database'] = formatted_df.get('Selection_Value_Database_Str', formatted_df.get('Selection_Value_Database', ''))
            formatted_df['Values_Only_Extracted_Str'] = formatted_df.get('Values_Only_Extracted_Str', formatted_df.get('Values_Only_Extracted', ''))
            formatted_df['Values_Only_Database_Str'] = formatted_df.get('Values_Only_Database_Str', formatted_df.get('Values_Only_Database', ''))
            formatted_df['Values_Common_Str'] = formatted_df.get('Values_Common_Str', formatted_df.get('Values_Common', ''))
            
            logger.info(f"✅ Formatted {len(formatted_df)} Business Nature records for main comparison")
            return formatted_df
            
        except Exception as e:
            logger.error(f"❌ Error formatting Business Nature results: {e}")
            return pd.DataFrame()
    
    def add_business_nature_to_comparison(self, comparison_df: pd.DataFrame, result: DataComparisonResult) -> pd.DataFrame:
        """
        Add Business Nature comparison results to the main comparison dataframe for inclusion in Value_Mismatch sheet
        """
        logger.info("🔀 Adding Business Nature results to main comparison for Value_Mismatch sheet...")
        
        try:
            # Check if we have the raw dataframes needed for Business Nature comparison
            if not hasattr(result, 'df_extracted') or not hasattr(result, 'df_database'):
                logger.warning("⚠️ No raw dataframes available for Business Nature comparison")
                return comparison_df
            
            # Filter raw dataframes for Business Nature records
            business_nature_extracted = result.df_extracted[
                result.df_extracted['Dropdown_Name'].str.contains('Business.*Nature|Nature.*Business', case=False, na=False, regex=True)
            ].copy()
            
            business_nature_database = result.df_database[
                result.df_database['Dropdown_Name'].str.contains('Business.*Nature|Business_Nature|Nature.*Business', case=False, na=False, regex=True)
            ].copy()
            
            if business_nature_extracted.empty and business_nature_database.empty:
                logger.info("ℹ️ No Business Nature records to add to comparison")
                return comparison_df
            
            # Get Business Nature comparison results
            business_nature_comparison = self.compare_business_nature_data(
                business_nature_extracted, 
                business_nature_database
            )
            
            if business_nature_comparison.empty:
                logger.info("ℹ️ Business Nature comparison returned no results for Value_Mismatch")
                return comparison_df
            
            # Transform Business Nature results to match main comparison format
            business_nature_formatted = self.format_business_nature_for_main_comparison(business_nature_comparison)
            
            if not business_nature_formatted.empty:
                # Combine with main comparison
                combined_comparison = pd.concat([comparison_df, business_nature_formatted], ignore_index=True)
                logger.info(f"✅ Added {len(business_nature_formatted)} Business Nature records to main comparison")
                return combined_comparison
            else:
                logger.info("ℹ️ No Business Nature records formatted for main comparison")
                return comparison_df
                
        except Exception as e:
            logger.error(f"❌ Error adding Business Nature to main comparison: {e}")
            return comparison_df
