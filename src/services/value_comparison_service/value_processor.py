import pandas as pd
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.utils.logger import logger
from src.config.constants import *
from src.models.data_models import ProcessingStats
from src.config.constants import IQ_COMPANIES
from collections import defaultdict
import itertools

class ValueProcessor:
    """Handles data loading and processing operations with value combination"""
    
    def __init__(self):
        self.stats = ProcessingStats()
    
    def load_extracted_data(self, file_path: Path) -> pd.DataFrame:
        """Load and process extracted JSON data"""
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return pd.DataFrame()
            
            records = self._read_json_lines(file_path)
            if not records:
                logger.warning("No valid records found in extracted data")
                return pd.DataFrame()
            
            df = pd.DataFrame(records)
            logger.info(f"Loaded {len(df)} records from extracted data")
            
            return self._process_extracted_data(df)
            
        except Exception as e:
            logger.error(f"Error loading extracted data: {e}")
            return pd.DataFrame()
    
    def _read_json_lines(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read JSON lines from file"""
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    record = json.loads(line)
                    data = record.get('data', record)
                    records.append(data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON on line {line_num}")
                    continue
        return records
    
    def load_raw_extracted_data(self, file_path: Path) -> pd.DataFrame:
        """Load extracted JSON data as a DataFrame WITHOUT any processing/cleaning.
        Flattens data field if present and applies minimum column mappings."""
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return pd.DataFrame()
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if isinstance(record, dict) and "data" in record and isinstance(record["data"], dict):
                        records.append(record["data"])
                    elif isinstance(record, dict):
                        records.append(record)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON on line {line_num}")
                    continue
        if not records:
            logger.warning("No valid records found in extracted data")
            return pd.DataFrame()
        df = pd.DataFrame(records)

        existing_mappings = {k: v for k, v in COLUMN_MAPPINGS.items() if k in df.columns}
        if existing_mappings:
            df = df.rename(columns=existing_mappings)
        # Drop duplicate columns that might arise from duplicate mappings
        df = df.loc[:, ~df.columns.duplicated()]
        # Ensure required columns exist
        for col in ['Company', 'Region', 'Dropdown_Name', 'Selection_Value']:
            if col not in df.columns:
                df[col] = None
        # Set default region to 'Dubai' if missing/blank/nan
        df['Region'] = df['Region'].fillna('Dubai')
        df.loc[df['Region'].astype(str).isin(['', 'nan', 'None']), 'Region'] = 'Dubai'
        return df

    ## IQ related value processing start #######################################
    def load_iq_extracted_data(self, file_path: Path) -> pd.DataFrame:
        """
        Loads and processes IQ extracted data by grouping records and generating
        valid plan/network combinations to prevent duplicate rows.
        """
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return pd.DataFrame()

            # Read raw JSON records
            raw_records = self._read_json_lines(file_path)
            if not raw_records:
                return pd.DataFrame()

            # Process records to create a clean, long-format DataFrame
            processed_records = self._process_iq_records(raw_records)
            if not processed_records:
                return pd.DataFrame()

            return pd.DataFrame(processed_records)

        except Exception as e:
            logger.error(f"Error loading IQ extracted data: {e}", exc_info=True)
            return pd.DataFrame()

    def _process_iq_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Groups raw records and intelligently combines plan and network variations
        to create a clean, long-format list of records.
        """
        print(f"--- Starting _process_iq_records with {len(records)} raw records ---")
        
        # Filter for IQ companies first
        iq_company_names_lower = [c.lower() for c in IQ_COMPANIES]
        records = [
            r for r in records
            if r.get('Portal') and r.get('Portal').lower() in iq_company_names_lower
        ]
        print(f"--- After filtering for IQ companies, {len(records)} records remain ---")

        # Group records by their core identifiers
        grouped_data = defaultdict(list)
        for record in records:
            # Skip records like 'Business Nature' that don't define plan benefits
            if record.get('field name') in ['Business Nature']:
                continue

            # Use a tuple of core identifiers as the key for grouping
            key = (
                record.get('Portal'),
                record.get('TPA'),
                record.get('Region', 'Dubai'),
                record.get('Outpatient Plan'),
                record.get('Additional Benefits Plan')
            )
            grouped_data[key].append(record)
        
        print(f"--- Grouped data into {len(grouped_data)} groups ---")
        
        final_records = []
        # Process each group of records
        for i, (key, group_records) in enumerate(grouped_data.items()):
            print(f"\n--- Processing Group {i+1}/{len(grouped_data)} ---")
            print(f"Key: {key}")
            print(f"Number of records in group: {len(group_records)}")
            company, tpa, region, outpatient_plan, additional_benefits_plan = key

            # *** CHANGE: Identify the specific plan for this group from the 'Network' field ***
            # We assume the 'Network' field is consistent for all records in the group and represents the actual plan.
            context_plan = next((r.get('Network') for r in group_records if r.get('Network')), None)
            print(f"Identified Context Plan for this group: {context_plan}")

            # If a context plan is found, this is the only plan we process for this group.
            # Otherwise, fall back to the old logic (though this case should be rare).
            if context_plan:
                plans = [context_plan]
            else:
                plans = [v for r in group_records if r.get('field name') == 'Plan' for v in r.get('values', [])]
                if not plans:
                     plans = [r.get('Network') for r in group_records if r.get('Network')]


            part1s = [v for r in group_records if r.get('field name') == 'Network Part 1' for v in r.get('values', [])]
            part2s = [v for r in group_records if r.get('field name') == 'Network Part 2' for v in r.get('values', [])]
            
            print(f"Extracted Network Part 1s: {part1s}")
            print(f"Extracted Network Part 2s: {part2s}")

            # Store other attributes (benefits) in a dictionary
            other_attributes = {
                r['field name']: r['values']
                for r in group_records
                if r.get('field name') not in ['Plan', 'Network Part 1', 'Network Part 2']
            }
            print(f"Found {len(other_attributes)} other attributes.")

            # If there are no network parts, use the original network value if available
            if not part1s and not part2s:
                original_networks = {r.get('Network') for r in group_records if r.get('Network')}
                combined_networks = list(original_networks) if original_networks else ['']
            else:
                # Create all combinations of network parts
                combined_networks = [f"{p1}- {p2}" for p1 in (part1s or ['']) for p2 in (part2s or [''])]
            
            print(f"Combined Networks: {combined_networks}")
            print(f"Final Plans to iterate: {list(set(plans))}")


            # Generate a record for each combination of plan and combined network
            for plan in set(plans):
                for network in set(combined_networks):
                    # For each plan/network combo, add all the other benefit attributes
                    for dropdown_name, selection_values in other_attributes.items():
                        # The 'values' field is a list, so we create a row for each value in it
                        for selection_value in selection_values:
                            final_records.append({
                                'Company': company,
                                'TPA': tpa,
                                'Region': region,
                                'Outpatient_Plan': outpatient_plan,
                                'Additionaly_Benefits_Plan': additional_benefits_plan,
                                'Plan': plan,
                                'Network': network,
                                'Dropdown_Name': dropdown_name,
                                'Selection_Value': selection_value
                            })
        
        print(f"\n--- Generated a total of {len(final_records)} final records ---")
        return final_records

    ## IQ related value processing end ############################################

    def _process_extracted_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean extracted data with value combination"""
        self.stats.original_records = len(df)
        self.stats.original_portals = df['Portal'].nunique() if 'Portal' in df.columns else 0
        
        logger.info(f"Starting processing with {self.stats.original_records} records from {self.stats.original_portals} portals")
        
        # Processing pipeline
        df = self._filter_target_portals(df)
        df = self._apply_column_mappings(df)
        df = self._normalize_company_names(df)
        df = self._filter_excluded_fields(df)
        df = self._explode_list_values(df)
        df = self._filter_select_values(df)
        df = self._ensure_required_columns(df)
        df = self._remove_empty_values(df)
        df = self._handle_fidelity_tpa_combination(df)
        df = self._combine_dubai_insurance_tpa_fields_df(df)
        df = self._combine_duplicate_dropdown_values(df)
        
        # Update final stats
        # self._update_final_stats(df)
        
        logger.info(f"Final processed data: {df.shape}")

        return df
    
    def _combine_duplicate_dropdown_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combine multiple selection values for same dropdown combination"""
        if df.empty:
            return df
        
        logger.info("Combining duplicate dropdown values...")
        
        original_count = len(df)
        
        # Group by all columns except Selection_Value
        groupby_columns = ['Company', 'TPA', 'Network', 'Region', 'Dropdown_Name']
        existing_groupby_columns = [col for col in groupby_columns if col in df.columns]
        
        if not existing_groupby_columns:
            logger.warning("No groupby columns found for combining values")
            return df
        
        try:
            def combine_values_agg(series):
                """Combine selection values from multiple rows"""
                all_values = []
                for value in series:
                    if pd.notna(value) and str(value) != '':
                        all_values.append(str(value))
                
                # Remove duplicates and sort
                unique_values = sorted(list(set(all_values)))
                return unique_values
            
            # Use agg with a dictionary to specify what to do with each column
            agg_dict = {'Selection_Value': combine_values_agg}
            
            # For other columns, take the first value (they should be the same within each group)
            for col in df.columns:
                if col not in existing_groupby_columns and col != 'Selection_Value':
                    agg_dict[col] = 'first'
            
            # Apply aggregation
            combined_df = df.groupby(existing_groupby_columns, as_index=False).agg(agg_dict)
            
            final_count = len(combined_df)
            combined_count = original_count - final_count
            
            logger.info(f"Combined values: {original_count} → {final_count} records ({combined_count} combinations)")
            
            return combined_df
            
        except Exception as e:
            logger.error(f"Error in combining duplicate values: {e}")
            logger.warning("Returning original dataframe without combination")
            return df
    
    def _explode_list_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Explode list values in Selection_Value column"""
        if 'Selection_Value' in df.columns:
            list_mask = df['Selection_Value'].apply(lambda x: isinstance(x, list))
            list_count = list_mask.sum()
            
            if list_count > 0:
                logger.info(f"Found {list_count} records with list values, exploding...")
                
                # Explode the lists
                df = df.explode('Selection_Value').reset_index(drop=True)
                
                logger.info(f"After explosion: {len(df)} records")
            else:
                logger.info("No list values found to explode")
        
        return df
    
    def _filter_target_portals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter data by target portals"""
        if 'Portal' not in df.columns:
            return df
        
        # Log portal analysis
        all_portals = sorted(df['Portal'].unique())
        logger.info(f"Found {len(all_portals)} portals in raw data")
        
        found_portals = [p for p in TARGET_PORTALS if p in all_portals]
        missing_portals = [p for p in TARGET_PORTALS if p not in all_portals]
        
        logger.info(f"Found target portals: {len(found_portals)}/{len(TARGET_PORTALS)}")
        if missing_portals:
            logger.warning(f"Missing target portals: {missing_portals}")
        
        # Apply filter
        return df[df['Portal'].isin(TARGET_PORTALS)]
    
    def _apply_column_mappings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply column name mappings"""
        existing_mappings = {k: v for k, v in COLUMN_MAPPINGS.items() if k in df.columns}
        if existing_mappings:
            df = df.rename(columns=existing_mappings)
            logger.info(f"Applied column mappings: {existing_mappings}")
        
        return df
    
    def _filter_excluded_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out excluded field names"""
        if 'Dropdown_Name' in df.columns:
            excluded_mask = df['Dropdown_Name'].str.lower().isin(EXCLUDED_FIELDS)
            excluded_count = excluded_mask.sum()
            df = df[~excluded_mask]
            logger.info(f"Filtered out {excluded_count} records with excluded field names")
        return df
    
    def _filter_select_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out select-type values"""
        if 'Selection_Value' not in df.columns:
            return df
        
        original_count = len(df)
        
        # Filter out select patterns for individual values
        def is_valid_value(value):
            if pd.isna(value):
                return False
            
            value_str = str(value)
            
            # Check against select patterns
            is_select_value = any(re.match(pattern, value_str, re.IGNORECASE) for pattern in SELECT_PATTERNS)
            
            # Check for empty/null values
            is_empty = value_str in ['none', 'null', 'nan']
            
            return not (is_select_value or is_empty)
        
        # Apply filter
        df = df[df['Selection_Value'].apply(is_valid_value)]
        
        filtered_count = original_count - len(df)
        if filtered_count > 0:
            logger.info(f"Filtered out {filtered_count} select/empty values")
        
        return df
    
    def _ensure_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all required columns exist"""
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                df[col] = None
                logger.warning(f"Added missing column '{col}' with None values")
        return df
    
    def _remove_empty_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove empty values from Selection_Value"""
        if 'Selection_Value' in df.columns:
            # Handle both list and string values
            def is_valid_selection_value(value):
                if isinstance(value, list):
                    # For lists, check if any value is valid
                    return any(
                        str(v) not in ['None', 'nan'] and pd.notna(v)
                        for v in value
                    )
                else:
                    # For single values
                    return (
                        pd.notna(value) and 
                        str(value) not in ['None', 'nan']
                    )
            
            # Apply filter
            df = df[df['Selection_Value'].apply(is_valid_selection_value)]
        
        return df
    
    def _normalize_company_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize company names to match database format"""
        if 'Company' not in df.columns:
            return df
        
        # Company name mappings for database compatibility
        company_mappings = {
            # Remove Sukoon mapping since we now use consistent case
            # 'SUKOON INSURANCE': 'Sukoon Insurance',
            # Add other mappings as needed
        }
        
        # Apply mappings
        df['Company'] = df['Company'].replace(company_mappings)
        
        # Log the transformation
        for old_name, new_name in company_mappings.items():
            count = (df['Company'] == new_name).sum()
            if count > 0:
                logger.info(f"Normalized company name: '{old_name}' -> '{new_name}' ({count} records)")
        
        return df
    
    def _handle_fidelity_tpa_combination(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Special handling for Fidelity United: Combine TPA group with specific TPA values from Plan records

        After filtering, we have:
        1. TPA group records: TPA="Employees Guard Plans A - F", Dropdown_Name="Annual Limit", Selection_Value="AED 1,000,000"
        2. Plan records with specific TPA values: TPA="Mednet", Dropdown_Name="Plan", Selection_Value=["Employees Guard Plan A - Gold", ...]

        We need to extract TPA values only from Plan records and combine them with group records for the same region.
        This ensures we only create combinations for TPAs that actually have plan data.
        """
        if df.empty or 'Company' not in df.columns:
            return df

        # Ensure all relevant columns are string for .str operations, skip lists
        for col in ['Company', 'TPA', 'Dropdown_Name', 'Selection_Value', 'Region']:
            if col in df.columns:
                mask = ~df[col].apply(lambda x: isinstance(x, list))
                df.loc[mask, col] = df.loc[mask, col].astype(str)

        # Filter for Fidelity United only
        fidelity_mask = df['Company'].astype(str).str.contains('Fidelity United', case=False, na=False)
        fidelity_count = fidelity_mask.sum()

        if fidelity_count == 0:
            logger.info("No Fidelity United records found - skipping TPA combination")
            return df

        logger.info(f"Processing {fidelity_count} Fidelity United records for TPA combination")

        fidelity_df = df[fidelity_mask].copy()
        other_df = df[~fidelity_mask].copy()

        # Find records with field name "Plan" - these contain the actual plan values with specific TPAs
        plan_records = fidelity_df[
            (fidelity_df['Dropdown_Name'].notna()) & 
            (fidelity_df['Dropdown_Name'].str.lower() == 'plan') &
            (fidelity_df['TPA'].notna()) & 
            (fidelity_df['TPA'] != '') & 
            (fidelity_df['TPA'] != 'nan') & 
            (~fidelity_df['TPA'].str.contains('Employees Guard Plans', case=False, na=False))
        ]
        
        # Find group records that need TPA combination (those with "Employees Guard Plans A - F")
        group_records = fidelity_df[
            (fidelity_df['TPA'].notna()) & 
            (fidelity_df['TPA'].str.contains('Employees Guard Plans', case=False, na=False))
        ]
        
        # Find other records (those that are neither Plan records nor group records)
        other_fidelity_records = fidelity_df[
            ~fidelity_df.index.isin(plan_records.index) & 
            ~fidelity_df.index.isin(group_records.index)
        ]

        # Extract TPA values from Plan records - these are the actual available TPAs
        plan_tpa_mapping = {}
        if not plan_records.empty:
            for _, plan_row in plan_records.iterrows():
                region = plan_row['Region']
                tpa = plan_row['TPA']
                if pd.notna(region) and region != 'nan' and pd.notna(tpa) and tpa != 'nan':
                    if region not in plan_tpa_mapping:
                        plan_tpa_mapping[region] = set()
                    plan_tpa_mapping[region].add(tpa)
        
        logger.info(f"Plan TPA mapping by region: {dict(plan_tpa_mapping)}")

        # Create combinations only for TPAs that have Plan records
        combined_rows = []
        if not group_records.empty and plan_tpa_mapping:
            for region, tpa_set in plan_tpa_mapping.items():
                region_group_records = group_records[group_records['Region'] == region]
                
                # For each group record in this region, create a new row for each TPA that has Plan records
                for _, group_row in region_group_records.iterrows():
                    for tpa in tpa_set:
                        new_row = group_row.copy()
                        new_row['TPA'] = f"{group_row['TPA']} - {tpa}"
                        combined_rows.append(new_row)
                        logger.debug(f"Created combination: {new_row['TPA']} for region {region}")

        logger.info(f"Created {len(combined_rows)} TPA combination records")

        # Build final Fidelity dataframe
        final_fidelity_records = []
        
        # Add Plan records and other non-group records as-is
        if not plan_records.empty:
            final_fidelity_records.append(plan_records)
        if not other_fidelity_records.empty:
            final_fidelity_records.append(other_fidelity_records)
            
        # Add combined rows instead of original group records
        if combined_rows:
            final_fidelity_records.append(pd.DataFrame(combined_rows))
        
        # Combine all Fidelity records
        if final_fidelity_records:
            fidelity_df = pd.concat(final_fidelity_records, ignore_index=True)
        else:
            fidelity_df = pd.DataFrame()

        result_df = pd.concat([fidelity_df, other_df], ignore_index=True)
        logger.info(f"Completed Fidelity TPA combination: {len(result_df)} total records")
        return result_df
    
    def _combine_dubai_insurance_tpa_fields_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        For DUBAI INSURANCE CO, ensures all records use the combined TPA value.
        Handles cases where JSON processing has already created TPA Combined records.
        
        Args:
            df: DataFrame containing extracted data
            
        Returns:
            DataFrame: Updated DataFrame with combined TPA information
        """
        if df.empty or 'Company' not in df.columns:
            return df
            
        # Filter for DUBAI INSURANCE CO records only
        dubai_mask = df['Company'] == 'DUBAI INSURANCE CO'
        dubai_count = dubai_mask.sum()
        
        if dubai_count == 0:
            logger.info("No DUBAI INSURANCE CO records found - skipping TPA combination")
            return df
            
        logger.info(f"Processing {dubai_count} DUBAI INSURANCE CO records for TPA combination")
        
        # Check if we have TPA Combined records (from JSON processing)
        tpa_combined_mask = (df['Company'] == 'DUBAI INSURANCE CO') & (df['Dropdown_Name'] == 'TPA Combined')
        tpa_combined_records = df[tpa_combined_mask]
        
        # Also check for TPA 1 and TPA 2 records (in case JSON processing didn't happen)
        tpa_1_mask = (df['Company'] == 'DUBAI INSURANCE CO') & (df['Dropdown_Name'] == 'TPA 1')
        tpa_2_mask = (df['Company'] == 'DUBAI INSURANCE CO') & (df['Dropdown_Name'] == 'TPA 2')
        
        tpa_1_records = df[tpa_1_mask]
        tpa_2_records = df[tpa_2_mask]
        
        print(f"📋 TPA Records Found:")
        print(f"   • TPA Combined records: {len(tpa_combined_records)}")
        print(f"   • TPA 1 records: {len(tpa_1_records)}")
        print(f"   • TPA 2 records: {len(tpa_2_records)}")   

        # If we have TPA Combined records, use those values directly
        if not tpa_combined_records.empty:
            # Extract all unique TPA Combined values
            combined_tpa_values = tpa_combined_records['TPA'].unique()
            print(f"✅ Found existing TPA Combined values: {list(combined_tpa_values)}")
            
            # Apply each combined TPA value to matching records
            for combined_tpa in combined_tpa_values:
                # Find records that should use this combined TPA
                matching_records = tpa_combined_records[tpa_combined_records['TPA'] == combined_tpa]
                if not matching_records.empty:
                    # Update all Dubai Insurance records to use this combined TPA
                    # This assumes all records should use the same combined TPA for now
                    dubai_records_mask = df['Company'] == 'DUBAI INSURANCE CO'
                    df.loc[dubai_records_mask, 'TPA'] = combined_tpa
                    print(f"🚀 Applied combined TPA '{combined_tpa}' to all DUBAI INSURANCE CO records")

        # If we have TPA 1 and TPA 2 records (and no TPA Combined), create combinations
        elif not tpa_1_records.empty and not tpa_2_records.empty:
            print(f"🔧 Creating TPA combinations from TPA 1 and TPA 2 records:")
            
            # Debug: Print first few TPA 1 and TPA 2 records to understand structure
            print(f"📊 TPA 1 Records sample:")
            for i, (idx, record) in enumerate(tpa_1_records.head(3).iterrows()):
                tpa_value = record.get('TPA', 'N/A')
                print(f"   Record {i+1}: TPA='{tpa_value}', Dropdown='{record.get('Dropdown_Name', 'N/A')}'")
            
            print(f"📊 TPA 2 Records sample:")
            for i, (idx, record) in enumerate(tpa_2_records.head(3).iterrows()):
                tpa_value = record.get('TPA', 'N/A')
                print(f"   Record {i+1}: TPA='{tpa_value}', Dropdown='{record.get('Dropdown_Name', 'N/A')}'")
            
            # Create a mapping of original TPA values to their corresponding records
            # This will help us apply the correct combination to each record
            dubai_non_tpa_records = df[dubai_mask & ~(tpa_1_mask | tpa_2_mask | tpa_combined_mask)]
            print(f"🎯 Found {len(dubai_non_tpa_records)} DUBAI INSURANCE CO records to process")
            
            # Get all unique TPA values from the non-TPA records (these are the original TPA values)
            original_tpa_values = dubai_non_tpa_records['TPA'].dropna().unique()
            print(f"📋 Original TPA values in records: {list(original_tpa_values)}")
            
            # Collect all unique TPA 1 values
            tpa_1_values = []
            for _, record in tpa_1_records.iterrows():
                if 'TPA' in record and pd.notna(record['TPA']):
                    value = str(record['TPA'])
                    if value and not value.lower().startswith('select') and value not in tpa_1_values:
                        tpa_1_values.append(value)
                        print(f"   📋 Added TPA 1 value: '{value}'")
            
            # Collect all unique TPA 2 values
            tpa_2_values = []
            for _, record in tpa_2_records.iterrows():
                if 'TPA' in record and pd.notna(record['TPA']):
                    value = str(record['TPA'])
                    if value and not value.lower().startswith('select') and value not in tpa_2_values:
                        tpa_2_values.append(value)
                        print(f"   📋 Added TPA 2 value: '{value}'")

            print(f"   • Total unique TPA 1 values: {len(tpa_1_values)} - {tpa_1_values}")
            print(f"   • Total unique TPA 2 values: {len(tpa_2_values)} - {tpa_2_values}")
            
            if len(tpa_1_values) > 0 and len(tpa_2_values) > 0:
                print(f"🔗 Creating TPA combinations and mapping to original records:")
                
                # Create a mapping from original TPA values to combined TPA values
                tpa_mapping = {}
                
                # Strategy: Map each original TPA value to its appropriate combination
                # For Dubai Insurance, we need to determine which TPA 1 and TPA 2 values
                # correspond to each original TPA value in the records
                
                for original_tpa in original_tpa_values:
                    if pd.notna(original_tpa) and str(original_tpa):
                        original_tpa_str = str(original_tpa)
                        
                        # Find matching TPA 1 and TPA 2 values for this original TPA
                        # This is where we need to implement the logic to determine
                        # which TPA 1 and TPA 2 values correspond to each original TPA
                        
                        # For now, let's try to match based on the TPA name
                        matching_tpa1 = None
                        matching_tpa2 = None
                        
                        # Check if the original TPA matches any TPA 1 values
                        for tpa1 in tpa_1_values:
                            if original_tpa_str == tpa1 or original_tpa_str in tpa1:
                                matching_tpa1 = tpa1
                                break
                        
                        # Check if the original TPA matches any TPA 2 values  
                        for tpa2 in tpa_2_values:
                            if original_tpa_str == tpa2 or original_tpa_str in tpa2:
                                matching_tpa2 = tpa2
                                break
                        
                        # If we found matches, create the combination
                        if matching_tpa1 and matching_tpa2:
                            combined_tpa = f"{matching_tpa1} - {matching_tpa2}"
                            tpa_mapping[original_tpa_str] = combined_tpa
                            print(f"   🔗 Mapped '{original_tpa_str}' -> '{combined_tpa}'")
                        else:
                            # If no direct match, we might need to use the first available combination
                            # or implement more sophisticated matching logic
                            if tpa_1_values and tpa_2_values:
                                # For simplicity, map to the first TPA 1 and first TPA 2
                                # In reality, you might need more complex logic here
                                combined_tpa = f"{tpa_1_values[0]} - {tpa_2_values[0]}"
                                tpa_mapping[original_tpa_str] = combined_tpa
                                print(f"   ⚠️ No direct match for '{original_tpa_str}', using default: '{combined_tpa}'")
                
                print(f"🚀 Created TPA mapping: {tpa_mapping}")
                
                # Apply the specific combinations to records based on their original TPA values
                records_updated = 0
                for original_tpa, combined_tpa in tpa_mapping.items():
                    # Find all records with this original TPA value
                    matching_records_mask = (
                        dubai_mask & 
                        ~(tpa_1_mask | tpa_2_mask | tpa_combined_mask) & 
                        (df['TPA'] == original_tpa)
                    )
                    matching_count = matching_records_mask.sum()
                    
                    if matching_count > 0:
                        # Update these specific records with the combined TPA
                        df.loc[matching_records_mask, 'TPA'] = combined_tpa
                        records_updated += matching_count
                        print(f"   ✅ Applied '{combined_tpa}' to {matching_count} records with original TPA '{original_tpa}'")
                
                print(f"🎯 Total records updated: {records_updated}")
                print(f"✅ TPA combination process completed with specific mapping")
            else:
                print(f"❌ Insufficient TPA values found for combination")

        # Remove TPA 1, TPA 2, and TPA Combined dropdown records
        if not tpa_1_records.empty or not tpa_2_records.empty or not tpa_combined_records.empty:
            removal_mask = tpa_1_mask | tpa_2_mask | tpa_combined_mask
            records_to_remove = removal_mask.sum()
            print(f"🗑️ Removing {records_to_remove} TPA dropdown records (TPA 1, TPA 2, TPA Combined)")
            df = df[~removal_mask]
            logger.info("All DUBAI INSURANCE CO extracted values now use combined TPA for comparison")
        else:
            print(f"❌ Could not determine combined TPA values for DUBAI INSURANCE CO")
            logger.warning("Could not determine combined TPA value for DUBAI INSURANCE CO")
        
        logger.info(f"Completed DUBAI INSURANCE CO TPA combination: {len(df)} total records")
        return df
