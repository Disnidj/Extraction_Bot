from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import Optional, Tuple
from src.utils.logger import logger
from src.services.value_comparison_service.value_comparison_db import DataComparisonDBService
from src.services.value_comparison_service.value_processor import ValueProcessor
from src.services.value_comparison_service.mapping_service import MappingService
from src.services.value_comparison_service.comparison_service import ComparisonService
from src.services.value_comparison_service.dev_help_export_service import ExportService
from src.services.value_comparison_service.db_update_export_service import DBUpdateExportService 
from src.models.data_models import DataComparisonResult
from src.services.value_comparison_service.condition_validator import ConditionValidator
from src.services.value_comparison_service.tpa_comparison_service import TPAComparisonService
from src.services.value_comparison_service.network_comparison_service import NetworkComparisonService
from src.services.value_comparison_service.iq_comparison_service import IQComparisonService

class ValueComparator:
    """Main data comparison orchestrator - single processing for all brokers"""
    
    def __init__(self, broker_id: int):
        self.broker_id = broker_id
        
        # Initialize services
        self.db_service = DataComparisonDBService()
        self.data_processor = ValueProcessor()
        self.mapping_service = MappingService()
        self.comparison_service = ComparisonService(self.mapping_service)
        self.export_service = ExportService(broker_id)
        # self.db_update_export_service = DBUpdateExportService(
        #     broker_id=broker_id,
        #     mapping_service=self.mapping_service  # Pass the mapping service
        # )
        self.condition_validator = ConditionValidator(
            mapping_service=self.mapping_service
        )

        self.iq_comparison_service = IQComparisonService(
            db_service=self.db_service,
            mapping_service=self.mapping_service
        )

        self.db_update_export_service = DBUpdateExportService(
            broker_id=broker_id,
            mapping_service=self.mapping_service,
            iq_comparison_service=self.iq_comparison_service  # NEW: Pass IQ service
        )
        
        self.result: Optional[DataComparisonResult] = None


    def run_comparison(self, extracted_file_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """Run the complete data comparison process for all brokers"""
        try:
            logger.info("Starting comparison process for all brokers")
            
            # Load all data and mappings
            self._load_all_data_and_mappings()

            # Load extracted data
            df_extracted = self._load_extracted_data(extracted_file_path)

            # Run TPA comparison and keep the DataFrame
            tpa_comparison_df = self.run_tpa_comparison(extracted_file_path)
            
            # Run Network comparison and keep the DataFrame
            network_comparison_df = self.run_network_comparison(extracted_file_path)

            iq_comparison_df = self.run_iq_comparison(extracted_file_path)

            # Validate data
            if not self._validate_data(self.df_database, df_extracted):
                return None, None
            
            # Compare data
            self.result = self.comparison_service.compare_datasets(df_extracted, self.df_database)
            
            # Attach raw dataframes for specialized processing (e.g., Business Nature comparison)
            self.result.df_extracted = df_extracted
            self.result.df_database = self.df_database

            logger.debug(f"Db values: {self.df_database}")
            # Process special care conditions validation
            self._process_special_care_validation(df_extracted)
            
            # Export results, now passing tpa_comparison_df and network_comparison_df
            rpa_filename = self.export_service.save_comparison_results(self.result)
            db_update_filename = self.db_update_export_service.save_db_update_results(
                self.result,
                tpa_comparison_df=tpa_comparison_df,
                network_comparison_df=network_comparison_df,
                iq_comparison_df=iq_comparison_df   
            )
            
            # Print summary
            self.print_summary()
            
            return rpa_filename, db_update_filename
            
        except Exception as e:
            logger.error(f"Error in comparison process: {e}")
            return None, None

    def _create_special_care_filter(self, comparison_df: pd.DataFrame, special_care_df: pd.DataFrame) -> pd.Series:
        """Create filter to exclude special care records from main comparison"""
        logger.info("Creating special care exclusion filter")
        
        # Initialize filter as all False
        special_care_filter = pd.Series([False] * len(comparison_df), index=comparison_df.index)
        
        if special_care_df.empty:
            logger.info("No special care records to filter")
            return special_care_filter
        
        # Get special care fields
        special_care_fields = self._get_special_care_fields(special_care_df)
        logger.info(f"Special care fields to exclude: {sorted(special_care_fields)}")
        
        # Create filter for comparison dataframe
        for idx, comp_row in comparison_df.iterrows():
            company = comp_row['Company']
            dropdown_name = str(comp_row['Dropdown_Name']).lower()
            context_key = self._build_context_key(comp_row)
            
            # Check if this field is marked for special care
            if dropdown_name in special_care_fields:
                special_care_filter.loc[idx] = True
                # logger.debug(f"Marking for exclusion - Company: {company}, Field: {dropdown_name}, Context: {context_key}")
        
        excluded_count = special_care_filter.sum()
        logger.info(f"Identified {excluded_count} special care records to exclude from Add/Delete sheets")
        
        return special_care_filter

    def _build_context_key(self, row: pd.Series) -> str:
        context_parts = []
        
        for field in ['TPA', 'Network', 'Region']:
            if field in row and pd.notna(row[field]) and str(row[field]):
                context_parts.append(f"{field}:{str(row[field])}")
        
        context_key = "|".join(context_parts) if context_parts else ""
        # logger.debug(f"Built context key '{context_key}' for row with Company: {row.get('Company', '')}")
        return context_key

    def _load_all_data_and_mappings(self):
        """Load all data and mappings in a single database connection"""
        logger.info("Loading all data and mappings in single database session")
        
        # Fetch everything in one go
        (self.df_database,
        self.df_tpa_dropdowns,
        self.df_network_dropdowns,
        self.df_iq_data_plans,
        direct_mappings, 
        global_request_mappings, 
        company_specific_mappings, 
        dropdown_mappings,
        company_specific_direct_mappings

        ) = self.db_service.fetch_all_data_with_mappings()
        
        if self.df_database.empty:
            logger.error("No database data loaded")
            return
        
        self.iq_comparison_service.set_iq_data(self.df_iq_data_plans)

        # Load mappings into mapping service
        self.mapping_service.load_mappings(
            direct_mappings, 
            global_request_mappings, 
            company_specific_mappings, 
            dropdown_mappings,
            company_specific_direct_mappings
        )

    def _validate_data(self, df_database: pd.DataFrame, df_extracted: pd.DataFrame) -> bool:
        """Validate that both datasets have data"""
        if df_database.empty:
            logger.error("Database dataset is empty")
            return False
        
        if df_extracted.empty:
            logger.error("Extracted dataset is empty")
            return False
        
        logger.info("Both datasets validated successfully")
        return True

    def _load_extracted_data(self, file_path: Path) -> pd.DataFrame:
        """Load and process extracted data"""
        logger.info(f"Loading extracted data from: {file_path}")
        df_extracted = self.data_processor.load_extracted_data(file_path)
        
        if df_extracted.empty:
            logger.error("No extracted data loaded")
            return df_extracted
        
        logger.info(f"Loaded {len(df_extracted)} extracted records")
        return df_extracted
    
    def _process_special_care_validation(self, df_extracted: pd.DataFrame):
        """Process special care conditions validation and update results"""
        try:
            logger.info("Starting special care conditions validation")
            
            # Validate special care conditions and get results
            special_care_results = self.condition_validator.validate_conditions(
                df_extracted, 
                self.df_database
            )
            
            if not special_care_results.empty:
                logger.info(f"Generated {len(special_care_results)} special care validation results")
                
                # Add special care results to the main result object
                self.result.special_care_df = special_care_results
                
                # Remove special care records from main comparison DataFrame
                # so they don't appear in Add_Values or Delete_Values sheets
                if not self.result.comparison_df.empty:
                    original_count = len(self.result.comparison_df)
                    
                    # Create filter to exclude special care records
                    special_care_filter = self._create_special_care_filter(
                        self.result.comparison_df, 
                        special_care_results
                    )
                    
                    # Remove special care records from main comparison
                    self.result.comparison_df = self.result.comparison_df[~special_care_filter].copy()
                    
                    removed_count = original_count - len(self.result.comparison_df)
                    logger.info(f"Removed {removed_count} special care records from main comparison")
                
                # Log summary of special care results
                if 'Status' in special_care_results.columns:
                    status_counts = special_care_results['Status'].value_counts()
                    logger.info("Special care validation summary:")
                    for status, count in status_counts.items():
                        logger.info(f"  {status}: {count}")
            else:
                logger.warning("No special care validation results generated")
                
        except Exception as e:
            logger.error(f"Error in special care validation: {e}")
            # Continue with normal processing even if special care validation fails

    def run_tpa_comparison(self, extracted_file_path: Path) -> pd.DataFrame:
        df_extracted_raw = self.data_processor.load_raw_extracted_data(extracted_file_path)
        tpa_service = TPAComparisonService(self.db_service)
        tpa_service.df_tpa_dropdowns = self.df_tpa_dropdowns  # Pass the preloaded DataFrame
        comparison_df = tpa_service.compare_tpa_values(df_extracted_raw)
        return comparison_df
    
    def run_network_comparison(self, extracted_file_path: Path) -> pd.DataFrame:
        # Load raw extracted data for Network dropdown comparison
        df_extracted_raw = self.data_processor.load_raw_extracted_data(extracted_file_path)
        network_service = NetworkComparisonService(self.db_service)
        network_service.df_network_dropdowns = self.df_network_dropdowns
        comparison_df = network_service.compare_network_values(df_extracted_raw)
        # Do not export to Excel here
        return comparison_df

    def run_iq_comparison(self, extracted_file_path: Path) -> pd.DataFrame:
        """Run IQ comparison using the processed extracted data"""
        try:
            logger.info("Starting IQ comparison...")
            
            # Load extracted data for IQ comparison
            df_iq = self.data_processor.load_iq_extracted_data(extracted_file_path)
            # Run IQ comparison
            iq_comparison_df = self.iq_comparison_service.compare_iq_data(df_iq)
            print("This is iq comparison df", iq_comparison_df)
            if not iq_comparison_df.empty:
                logger.info(f"IQ comparison completed with {len(iq_comparison_df)} results")
            else:
                logger.warning("No IQ comparison results generated")
            
            return iq_comparison_df
            
        except Exception as e:
            print(f"AN ERROR OCCURRED: {e}")
            logger.error(f"Error in IQ comparison: {e}")
            return pd.DataFrame()
        
    def print_summary(self):
        """Print comparison summary"""
        if not self.result:
            logger.warning("No comparison results available")
            return
        
        print("\nALL BROKERS SUMMARY:")
        print("COMPANY COUNTS:")
        print(f"  Companies in Database: {len(self.result.database_companies)}")
        print(f"  Companies in Extracted Data: {len(self.result.extracted_companies)}")
        
        self._print_company_lists()
        self._print_missing_companies()
        self._print_mapping_summary()
        self._print_comparison_results()

    def _print_company_lists(self):
        """Print database and extracted company lists"""
        if self.result.database_companies:
            print("\nDATABASE COMPANIES:")
            for i, company in enumerate(self.result.database_companies, 1):
                print(f"  {i:2d}. {company}")
        
        if self.result.extracted_companies:
            print("\nEXTRACTED COMPANIES:")
            for i, company in enumerate(self.result.extracted_companies, 1):
                print(f"  {i:2d}. {company}")

    def _print_missing_companies(self):
        """Print companies that are missing from each dataset"""
        missing_in_extracted = set(self.result.database_companies) - set(self.result.extracted_companies)
        missing_in_db = set(self.result.extracted_companies) - set(self.result.database_companies)
        
        if missing_in_extracted:
            print(f"\nCOMPANIES ONLY IN DATABASE ({len(missing_in_extracted)}):")
            for i, company in enumerate(sorted(missing_in_extracted), 1):
                print(f"  {i:2d}. {company}")
        
        if missing_in_db:
            print(f"\nCOMPANIES ONLY IN EXTRACTED ({len(missing_in_db)}):")
            for i, company in enumerate(sorted(missing_in_db), 1):
                print(f"  {i:2d}. {company}")

    def _print_mapping_summary(self):
        """Print mapping statistics summary"""
        mapping_summary = self.mapping_service.get_mapping_summary()
        print("\nALL BROKERS MAPPING SUMMARY:")
        print(f"  Direct mappings available: {mapping_summary['direct_mappings_count']}")
        print(f"  Global two-step mappings available: {mapping_summary['combined_global_mappings_count']}")
        print(f"  Company-specific mappings available: {mapping_summary['combined_company_mappings_count']}")
        print(f"  Direct mappings used: {mapping_summary['direct_mapping_used']}")
        print(f"  Global two-step mappings used: {mapping_summary['global_two_step_mapping_used']}")
        print(f"  Company-specific mappings used: {mapping_summary['company_specific_mapping_used']}")
        print(f"  Fields without mapping: {mapping_summary['no_mapping_found']}")
        
        self._print_mapping_success_rate(mapping_summary)

    def _print_mapping_success_rate(self, mapping_summary: dict):
        """Calculate and print mapping success rate"""
        total_mapped = (mapping_summary['direct_mapping_used'] + 
                        mapping_summary['global_two_step_mapping_used'] + 
                        mapping_summary['company_specific_mapping_used'])
        total_processed = total_mapped + mapping_summary['no_mapping_found']
        
        if total_processed > 0:
            success_rate = (total_mapped / total_processed) * 100
            print(f"  Overall mapping success rate: {success_rate:.1f}%")
    
    def _print_comparison_results(self):
        """Print comparison results and special care records"""
        print("\nCOMPARISON RESULTS (excluding special care):")
        for mismatch_type, count in self.result.summary.to_dict().items():
            print(f"  {mismatch_type}: {count}")
        
        # NEW: Print IQ comparison stats if available
        if hasattr(self, '_iq_comparison_stats'):
            print("\nIQ COMPARISON RESULTS:")
            for stat_name, count in self._iq_comparison_stats.items():
                print(f"  {stat_name}: {count}")
        
        if hasattr(self.result, 'special_care_df') and not self.result.special_care_df.empty:
            print(f"SPECIAL CARE RECORDS: {len(self.result.special_care_df)}")
    
    def _get_special_care_fields(self, special_care_df: pd.DataFrame) -> set:
        """Extract special care fields from special care dataframe"""
        special_care_fields = set()
        for _, sc_row in special_care_df.iterrows():
            trigger = sc_row.get('Trigger_Field_Mapped', '') or sc_row.get('Trigger_Field_Original', '')
            dependent = sc_row.get('Dependent_Field_Mapped', '') or sc_row.get('Dependent_Field_Original', '')
            if trigger: 
                special_care_fields.add(trigger.lower())
            if dependent: 
                special_care_fields.add(dependent.lower())
        return special_care_fields

    # def export_database_to_excel(self, path: str = "database_data_dump.xlsx"):
    #     """Export the loaded database data to an Excel file for inspection."""
    #     if hasattr(self, 'df_database') and self.df_database is not None and not self.df_database.empty:
    #         self.df_database.to_excel(path, index=False)
    #         logger.info(f"Database data exported to {path}")
    #     else:
    #         logger.warning("No database data available to export.")
