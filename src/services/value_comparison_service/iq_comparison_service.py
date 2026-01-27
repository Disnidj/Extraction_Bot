import pandas as pd
from src.utils.logger import logger
from typing import Dict, List
# from src.services.value_comparison_service.mapping_service import MappingService
from src.config.constants import IQ_COMPANIES

class IQComparisonService:
    def __init__(self, db_service, mapping_service):
        self.db_service = db_service
        self.mapping_service = mapping_service
        self.df_iq_data = None

    def set_iq_data(self, df_iq_data: pd.DataFrame):
        """Set the IQ data from main data fetch"""
        self.df_iq_data = df_iq_data
        logger.info(f"IQ data set with {len(df_iq_data)} records")

    def compare_iq_data(self, df_extracted: pd.DataFrame) -> pd.DataFrame:
        """
        Loads, prepares, and compares extracted data against the database,
        returning a DataFrame of the differences.
        """
        try:
            logger.info("Starting IQ comparison...")
            
            if self.df_iq_data is None or self.df_iq_data.empty:
                logger.warning("No database IQ data available.")
                return pd.DataFrame()
            
            db_wide = self._prepare_database_for_comparison()
            if db_wide.empty:
                logger.warning("No database IQ data prepared.")
                return pd.DataFrame()

            extracted_wide = self._prepare_extracted_for_comparison(df_extracted, db_wide)
            if extracted_wide.empty:
                logger.warning("No extracted IQ data prepared.")
                return pd.DataFrame()
            
            # Perform the full comparison
            comparison_results = self._perform_wide_comparison(extracted_wide, db_wide)
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error in IQ comparison: {e}", exc_info=True)
            return pd.DataFrame()

    def _prepare_database_for_comparison(self) -> pd.DataFrame:
        """Prepares the database data, keeping it in a wide format."""
        try:
            if self.df_iq_data is None or self.df_iq_data.empty:
                return pd.DataFrame()
            
            df_db = self.df_iq_data.copy()
            
            if 'id' in df_db.columns:
                df_db = df_db.drop(columns=['id'])

            return df_db
        except Exception as e:
            logger.error(f"Error preparing database data: {e}", exc_info=True)
            return pd.DataFrame()

    def _prepare_extracted_for_comparison(self, df_extracted: pd.DataFrame, db_wide: pd.DataFrame) -> pd.DataFrame:
        """
        Prepares extracted data by filtering, mapping, and pivoting to a wide format.
        """
        try:
            if df_extracted.empty:
                return pd.DataFrame()

            iq_extracted = df_extracted[
                df_extracted['Company'].str.lower().isin([c.lower() for c in IQ_COMPANIES])
            ].copy()

            if iq_extracted.empty:
                logger.warning("No data found for the specified IQ companies after filtering.")
                return pd.DataFrame()

            iq_extracted = iq_extracted[~iq_extracted['Network'].str.startswith('EBP')]

            iq_extracted['Dropdown_Name'] = iq_extracted.apply(
                lambda row: self.mapping_service.get_mapping_for_field(row['Dropdown_Name'], row['Company'])[0], axis=1
            )

            valid_db_cols = set(db_wide.columns)
            unmapped_mask = ~iq_extracted['Dropdown_Name'].isin(valid_db_cols)
            if unmapped_mask.any():
                unmapped_names = iq_extracted[unmapped_mask]['Dropdown_Name'].unique()
                logger.warning(f"Ignoring unmapped dropdowns: {list(unmapped_names)}")
                iq_extracted = iq_extracted[~unmapped_mask]

            plan_defining_cols = ['Outpatient_Plan', 'Additionaly_Benefits_Plan']
            iq_extracted = iq_extracted[~iq_extracted['Dropdown_Name'].isin(plan_defining_cols)]

            id_cols = ['Company', 'TPA', 'Plan', 'Network', 'Region', 'Outpatient_Plan', 'Additionaly_Benefits_Plan']
            
            for col in id_cols:
                if col not in iq_extracted.columns:
                    iq_extracted[col] = ''
            
            iq_extracted[id_cols] = iq_extracted[id_cols].fillna('')

            extracted_wide = iq_extracted.pivot_table(
                index=id_cols,
                columns='Dropdown_Name',
                values='Selection_Value',
                aggfunc='first'
            ).reset_index()

            return extracted_wide

        except Exception as e:
            logger.error(f"Error preparing extracted data for comparison: {e}", exc_info=True)
            return pd.DataFrame()

    def _perform_wide_comparison(self, extracted_wide: pd.DataFrame, db_wide: pd.DataFrame) -> pd.DataFrame:
        """
        Performs a full comparison between extracted and database data,
        identifying adds, deletes, and updates.
        """
        try:
            merge_cols = ['Company', 'TPA', 'Plan', 'Network', 'Region', 'Outpatient_Plan', 'Additionaly_Benefits_Plan']
            
            # Scope the database data to only the companies in the extraction
            companies_in_extraction = extracted_wide['Company'].unique()
            db_wide_scoped = db_wide[db_wide['Company'].isin(companies_in_extraction)].copy()

            # Merge the two dataframes to align rows for comparison
            merged_df = pd.merge(
                extracted_wide,
                db_wide_scoped,
                on=merge_cols,
                how='inner',
                suffixes=('_ext', '_db')
            )

            # Identify all unique benefit columns from both datasets
            ext_cols = [col for col in extracted_wide.columns if col not in merge_cols]
            db_cols = [col for col in db_wide.columns if col not in merge_cols]
            all_benefit_cols = sorted(list(set(ext_cols) | set(db_cols)))

            comparison_output = []
            
            for index, row in merged_df.iterrows():
                result_record = {col: row[col] for col in merge_cols}
                has_mismatch = False

                for col in all_benefit_cols:
                    # Get values, filling missing ones (NaN) with an empty string
                    db_val = str(row.get(f"{col}_db", ''))
                    ext_val = str(row.get(f"{col}_ext", ''))

                    if db_val == 'nan': db_val = ''
                    if ext_val == 'nan': ext_val = ''

                    # Simple string comparison
                    if db_val != ext_val:
                        has_mismatch = True
                        result_record[col] = f"{db_val} -> {ext_val}"
                    else:
                        result_record[col] = db_val

                if has_mismatch:
                    comparison_output.append(result_record)

            if not comparison_output:
                return pd.DataFrame()

            final_df = pd.DataFrame(comparison_output)
            # Ensure all columns are present in the final DataFrame
            all_output_cols = merge_cols + all_benefit_cols
            for col in all_output_cols:
                if col not in final_df.columns:
                    final_df[col] = ''
            
            return final_df[all_output_cols]

        except Exception as e:
            logger.error(f"Error during wide comparison: {e}", exc_info=True)
            return pd.DataFrame()

    def prepare_iq_add_data(self, comparison_df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for Add IQ Values sheet in a wide format, showing only the
        values to be added.
        """
        try:
            if comparison_df.empty:
                return pd.DataFrame()

            add_data_records = []
            id_cols = ['Company', 'TPA', 'Plan', 'Network', 'Region', 'Outpatient_Plan', 'Additionaly_Benefits_Plan']
            
            benefit_cols = [col for col in comparison_df.columns if col not in id_cols]

            for _, row in comparison_df.iterrows():
                add_record = {col: row[col] for col in id_cols}
                has_data_to_add = False
                
                for col in benefit_cols:
                    add_record[col] = ''

                for col_name in benefit_cols:
                    value = row[col_name]
                    if isinstance(value, str) and '->' in value:
                        _, ext_val = value.split('->', 1)
                        ext_val = ext_val.strip()
                        
                        if ext_val:
                            add_record[col_name] = ext_val
                            has_data_to_add = True
                
                if has_data_to_add:
                    add_data_records.append(add_record)
            
            if not add_data_records:
                return pd.DataFrame()

            result_df = pd.DataFrame(add_data_records)
            final_cols = id_cols + benefit_cols
            return result_df[final_cols]
                
        except Exception as e:
            logger.error(f"Error preparing IQ add data: {e}", exc_info=True)
            return pd.DataFrame()

    def prepare_iq_delete_data(self, comparison_df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for Delete IQ Values sheet in a wide format, showing only the
        values to be deleted.
        """
        try:
            if comparison_df.empty:
                return pd.DataFrame()
                
            delete_data_records = []
            id_cols = ['Company', 'TPA', 'Plan', 'Network', 'Region', 'Outpatient_Plan', 'Additionaly_Benefits_Plan']
            
            benefit_cols = [col for col in comparison_df.columns if col not in id_cols]

            for _, row in comparison_df.iterrows():
                delete_record = {col: row[col] for col in id_cols}
                has_data_to_delete = False

                for col in benefit_cols:
                    delete_record[col] = ''

                for col_name in benefit_cols:
                    value = row[col_name]
                    if isinstance(value, str) and '->' in value:
                        db_val, _ = value.split('->', 1)
                        db_val = db_val.strip()
                        
                        if db_val:
                           delete_record[col_name] = db_val
                           has_data_to_delete = True
            
                if has_data_to_delete:
                    delete_data_records.append(delete_record)

            if not delete_data_records:
                return pd.DataFrame()

            result_df = pd.DataFrame(delete_data_records)
            final_cols = id_cols + benefit_cols
            return result_df[final_cols]
                
        except Exception as e:
            logger.error(f"Error preparing IQ delete data: {e}", exc_info=True)
            return pd.DataFrame()
