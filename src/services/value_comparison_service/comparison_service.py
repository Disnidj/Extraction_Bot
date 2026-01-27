import pandas as pd
from typing import List, Dict, Any
from src.utils.logger import logger
from src.models.data_models import ComparisonSummary, DataComparisonResult
from src.services.value_comparison_service.mapping_service import MappingService
from src.config.constants import EXCLUDED_COMPANIES
class ComparisonService:
    """Handles data comparison operations with direct extracted field display"""
    
    def __init__(self, mapping_service: MappingService):
        self.merge_columns = ['Company', 'TPA', 'Network', 'Region', 'Dropdown_Name']
        self.mapping_service = mapping_service
    
    def compare_datasets(self, df_extracted: pd.DataFrame, df_database: pd.DataFrame) -> DataComparisonResult:
        """Compare extracted and database datasets with original extracted names preserved"""

        # Filter out excluded companies from main comparison
        df_extracted = df_extracted[~df_extracted['Company'].isin(EXCLUDED_COMPANIES)].copy()
        df_database = df_database[~df_database['Company'].isin(EXCLUDED_COMPANIES)].copy()

        # Build mappings before creating groups
        self.mapping_service.build_global_mappings(df_extracted, df_database)
        
        # Apply mappings and get both versions
        df_extracted_mapped, df_extracted_original = self.mapping_service.apply_mappings_for_comparison(df_extracted)
        
        # Database data doesn't need mapping (already contains DB names)
        df_database_mapped = df_database.copy()
        
        # Create mapping lookup before grouping
        original_field_lookup = self._create_original_field_lookup(df_extracted_mapped, df_extracted_original)
        
        # Create groups from mapped data for comparison logic
        database_groups = self._create_groups(df_database_mapped, 'Database')
        extracted_groups = self._create_groups(df_extracted_mapped, 'Extracted')
        
        if database_groups.empty and extracted_groups.empty:
            logger.error("No groups created from either source")
            return DataComparisonResult(
                comparison_df=pd.DataFrame(),
                summary=ComparisonSummary(),
                database_companies=[],
                extracted_companies=[]
            )
        
        # Analyze dropdown overlap
        self._analyze_dropdown_overlap(database_groups, extracted_groups)
        
        # Merge and compare with original names preservation
        comparison_df = self._merge_and_compare(extracted_groups, database_groups, original_field_lookup)
        
        # Create summary
        summary = self._create_summary(comparison_df)
        
        return DataComparisonResult(
            comparison_df=comparison_df,
            summary=summary,
            database_companies=sorted(df_database['Company'].unique()) if 'Company' in df_database.columns else [],
            extracted_companies=sorted(df_extracted_original['Company'].unique()) if 'Company' in df_extracted_original.columns else []
        )
    
    def _create_original_field_lookup(self, df_extracted_mapped: pd.DataFrame, df_extracted_original: pd.DataFrame) -> Dict[tuple, str]:
        """Create lookup from mapped field names to original field names"""
        original_lookup = {}
        
        # Ensure both dataframes have the same length
        if len(df_extracted_mapped) != len(df_extracted_original):
            logger.error(f"DataFrame length mismatch: mapped={len(df_extracted_mapped)}, original={len(df_extracted_original)}")
            return original_lookup
        
        # Create row-by-row mapping
        for i in range(len(df_extracted_mapped)):
            mapped_row = df_extracted_mapped.iloc[i]
            original_row = df_extracted_original.iloc[i]
            
            # Create key from mapped data
            key = (
                mapped_row['Company'],
                mapped_row['TPA'], 
                mapped_row['Network'],
                mapped_row['Region'],
                mapped_row['Dropdown_Name']  # This is the mapped dropdown name
            )
            
            # Value is the original dropdown name
            original_dropdown_name = original_row['Dropdown_Name']
            
            # Store the mapping
            original_lookup[key] = original_dropdown_name
        
        return original_lookup
    
    def _create_groups(self, df: pd.DataFrame, source_name: str) -> pd.DataFrame:
        """Group data by dropdown fields - handles both list and string values"""
        if df.empty:
            return pd.DataFrame()
        
        def combine_selection_values(series):
            """Combine selection values, handling both lists and strings"""
            all_values = []
            
            for value in series.dropna():
                if isinstance(value, list):
                    # If it's already a list, extend it
                    all_values.extend([str(v) for v in value if str(v)])
                else:
                    # If it's a string, add it
                    val_str = str(value)
                    if val_str:
                        all_values.append(val_str)
            
            # Remove duplicates and sort
            unique_values = sorted(set(all_values))
            return unique_values
        
        # Group by merge columns 
        grouped = df.groupby(self.merge_columns)['Selection_Value'].apply(combine_selection_values).reset_index()
        
        grouped['Source'] = source_name
        grouped['Values_String'] = grouped['Selection_Value'].apply(lambda x: ','.join(x))
        
        logger.info(f"{source_name} groups created: {len(grouped)} unique dropdown combinations")
        
        return grouped
    
    def _analyze_dropdown_overlap(self, database_groups: pd.DataFrame, extracted_groups: pd.DataFrame):
        """Analyze dropdown name overlap between datasets"""
        if database_groups.empty or extracted_groups.empty:
            return
        
        db_dropdowns = set(database_groups['Dropdown_Name'].unique())
        ext_dropdowns = set(extracted_groups['Dropdown_Name'].unique())
        common_dropdowns = db_dropdowns & ext_dropdowns
        only_in_db = db_dropdowns - ext_dropdowns
        only_in_extracted = ext_dropdowns - db_dropdowns
        
        logger.info("Dropdown analysis:")
        logger.info(f"  Common dropdown names: {len(common_dropdowns)}")
        logger.info(f"  Only in database: {len(only_in_db)}")
        logger.info(f"  Only in extracted: {len(only_in_extracted)}")
    
    def _merge_and_compare(self, extracted_groups: pd.DataFrame, database_groups: pd.DataFrame, original_field_lookup: Dict[tuple, str]) -> pd.DataFrame:
        """Merge datasets and perform comparison with original extracted names preservation"""
        # Perform merge on mapped data for comparison logic
        comparison = pd.merge(
            extracted_groups[self.merge_columns + ['Selection_Value', 'Values_String']], 
            database_groups[self.merge_columns + ['Selection_Value', 'Values_String']], 
            on=self.merge_columns, 
            how='outer',
            suffixes=('_Extracted', '_Database')
        )
        
        # Add original extracted field names using lookup
        comparison = self._add_original_field_names_from_lookup(comparison, original_field_lookup)
        
        # Handle missing values
        comparison = self._handle_missing_values(comparison)
        
        # Calculate differences
        comparison = self._calculate_differences(comparison)
        
        # Determine mismatch types
        comparison['Mismatch_Type'] = comparison.apply(self._get_mismatch_type, axis=1)
        
        # Add DB field display names with priority logic
        comparison = self._add_db_field_display_names(comparison)
        
        # Add request names for DB update sheets
        comparison = self._add_request_names_for_display(comparison)
        
        # Convert lists to strings for export
        comparison = self._convert_lists_to_strings(comparison)
        
        return comparison
    
    def _add_original_field_names_from_lookup(self, comparison_df: pd.DataFrame, original_field_lookup: Dict[tuple, str]) -> pd.DataFrame:
        """Add original extracted field names using the pre-built lookup"""
        
        def get_original_name(row):
            # Create lookup key from comparison row
            key = (
                row['Company'],
                row['TPA'], 
                row['Network'],
                row['Region'],
                row['Dropdown_Name']  # This is the mapped dropdown name
            )
            
            original_name = original_field_lookup.get(key, "")
            
            # Handle company name mismatch (e.g., 'SUKOON INSURANCE' vs 'Sukoon Insurance')
            if not original_name:
                # Try with normalized company name
                normalized_company = row['Company']
                if normalized_company == 'SUKOON INSURANCE':
                    # Try with 'Sukoon Insurance' instead
                    fallback_key = (
                        'Sukoon Insurance',
                        row['TPA'], 
                        row['Network'],
                        row['Region'],
                        row['Dropdown_Name']
                    )
                    original_name = original_field_lookup.get(fallback_key, "")
                    
            return original_name
        
        comparison_df['Original_Extracted_Field_Name'] = comparison_df.apply(get_original_name, axis=1)
        
        # Log results
        non_empty_count = (comparison_df['Original_Extracted_Field_Name'] != "").sum()
        total_count = len(comparison_df)
        
        logger.info(f"Original field names added: {non_empty_count}/{total_count} records matched")
        
        return comparison_df
    
    def _add_db_field_display_names(self, comparison_df: pd.DataFrame) -> pd.DataFrame:
        """Add DB field display names with priority logic"""
        def get_db_display_name(row):
            dropdown_name = row.get('Dropdown_Name', '')
            return self.mapping_service.get_db_display_name(dropdown_name)
        
        comparison_df['DB_Field_Display_Name'] = comparison_df.apply(get_db_display_name, axis=1)
        
        return comparison_df
    
    def _add_request_names_for_display(self, comparison_df: pd.DataFrame) -> pd.DataFrame:
        """Add request names for display in DB update sheets"""
        def get_request_name(row):
            # Use the original extracted field name to find the request name
            original_extracted_name = row.get('Original_Extracted_Field_Name', '')
            company = row.get('Company', '')
            
            # If no original extracted name, fall back to dropdown name
            if not original_extracted_name:
                original_extracted_name = row.get('Dropdown_Name', '')
            
            return self.mapping_service.get_request_name_for_display(original_extracted_name, company)
        
        comparison_df['Request_Name_Display'] = comparison_df.apply(get_request_name, axis=1)
        
        return comparison_df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in comparison dataframe"""
        df['Selection_Value_Extracted'] = df['Selection_Value_Extracted'].fillna('').apply(
            lambda x: x if isinstance(x, list) else []
        )
        df['Selection_Value_Database'] = df['Selection_Value_Database'].fillna('').apply(
            lambda x: x if isinstance(x, list) else []
        )
        df[['Values_String_Extracted', 'Values_String_Database']] = df[
            ['Values_String_Extracted', 'Values_String_Database']
        ].fillna('')
        
        return df
    
    def _calculate_differences(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate value differences between datasets"""
        df['Values_Only_Extracted'] = df.apply(
            lambda row: sorted(set(row['Selection_Value_Extracted']) - set(row['Selection_Value_Database'])), 
            axis=1
        )
        df['Values_Only_Database'] = df.apply(
            lambda row: sorted(set(row['Selection_Value_Database']) - set(row['Selection_Value_Extracted'])), 
            axis=1
        )
        df['Values_Common'] = df.apply(
            lambda row: sorted(set(row['Selection_Value_Extracted']) & set(row['Selection_Value_Database'])), 
            axis=1
        )
        
        return df
    
    def _get_mismatch_type(self, row: pd.Series) -> str:
        """Determine mismatch type for a row"""
        if not row['Selection_Value_Extracted'] and row['Selection_Value_Database']:
            return 'Only in Database'
        elif row['Selection_Value_Extracted'] and not row['Selection_Value_Database']:
            return 'Only in Extracted'
        elif row['Values_Only_Extracted'] or row['Values_Only_Database']:
            return 'Value Mismatch'
        else:
            return 'Perfect Match'
    
    def _convert_lists_to_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert list columns to strings for Excel export"""
        for col in ['Values_Only_Extracted', 'Values_Only_Database', 'Values_Common']:
            df[f'{col}_Str'] = df[col].apply(lambda x: ','.join(x))
        return df
    
    def _create_summary(self, comparison_df: pd.DataFrame) -> ComparisonSummary:
        """Create comparison summary statistics"""
        if comparison_df.empty:
            return ComparisonSummary()
        
        mismatch_counts = comparison_df['Mismatch_Type'].value_counts().to_dict()
        
        value_mismatches = comparison_df[comparison_df['Mismatch_Type'] == 'Value Mismatch']
        
        return ComparisonSummary(
            total_records=len(comparison_df),
            perfect_matches=mismatch_counts.get('Perfect Match', 0),
            value_mismatches=mismatch_counts.get('Value Mismatch', 0),
            only_in_database=mismatch_counts.get('Only in Database', 0),
            only_in_extracted=mismatch_counts.get('Only in Extracted', 0),
            companies_affected=value_mismatches['Company'].nunique() if not value_mismatches.empty else 0,
            total_missing_values=value_mismatches['Values_Only_Extracted'].apply(len).sum() if not value_mismatches.empty else 0,
            total_extra_values=value_mismatches['Values_Only_Database'].apply(len).sum() if not value_mismatches.empty else 0
        )