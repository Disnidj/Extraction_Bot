from typing import Dict, Any, Optional, List, Tuple
from src.utils.logger import logger
import pandas as pd
import os
from src.services.value_comparison_service.mapping_service import MappingService
from src.services.value_comparison_service.value_comparison_db import DataComparisonDBService

class ConditionValidator:
    """Validates special care conditions and prepares data for Special_Care sheet"""
    
    def __init__(self, mapping_service: MappingService):
        self.mapping_service = mapping_service
       
        # Define all company field relationships using EXTRACTED field names
        self.field_relationships = {
            # Daman Insurance mappings
            "Daman Insurance": [
                {
                    "trigger_field": "PC Copay",
                    "dependent_field": "PC Out of Pocket",
                },
                {
                    "trigger_field": "Dental Coverage",
                    "dependent_field": "Dental Limit",
                },
                {
                    "trigger_field": "Optical Coverage",
                    "dependent_field": "Optical Limit"
                }
            ],
            # ISON mapping
            "ISON": [
                {
                    "trigger_field": "Plan",
                    "dependent_field": "PreExisting and Chronic Conditions",
                }
            ],
            # AL SAGR mapping with conditions
            "AL SAGR INSURANCE COMPANY": [
                {
                    "conditions": {
                        "TPA": "NEXT CARE MANAGEMENT LLC",
                        "Network": "RN3"
                    },
                    "trigger_field": "Pharmacy",
                    "dependent_field": "Pharmacy Limit",
                }
            ],
            # NLGIC mapping
            "NLGIC": [
                {
                    "trigger_field": "Dental Limit",
                    "dependent_field": "Dental CO",
                }
            ],
            # RAK INSURANCE mapping
            "RAK INSURANCE": [
                {
                    "trigger_field": "Dental",
                    "dependent_field": "Dental CO"
                },
                {
                    "trigger_field": "Optical",
                    "dependent_field": "Optical CO"
                },
                {
                    "trigger_field": "Alternative Medicine",
                    "dependent_field": "Alternative Medicine CO"
                }
            ],
            # ORIENT INSURANCE PJSC mapping
            "ORIENT INSURANCE PJSC": [
                {
                    "trigger_field": "Dental",
                    "dependent_field": "Dental CO"
                },
                {
                    "trigger_field": "Optical",
                    "dependent_field": "Optical CO"
                },
                {
                    "trigger_field": "Alternative Medicine",
                    "dependent_field": "Alternative Medicine CO"
                }
            ],
            # Dubai National Insurance mapping
            "Dubai National Insurance And Reinsurance Co": [
                {
                    "trigger_field": "Dental",
                    "dependent_field": "Dental CO",
                },
                {
                    "trigger_field": "Optical",
                    "dependent_field": "Optical CO",
                },
                {
                    "trigger_field": "Alternative Medicine",
                    "dependent_field": "Alternative Medicine CO",
                }
            ],
            # SUKOON INSURANCE mapping - TPA as trigger with multiple dependent fields
            "SUKOON INSURANCE": [
                # {
                #     "trigger_field": "Nature of Business",
                #     "dependent_field": "Nature of Business",
                # },
                {
                    "trigger_field": "TPA",
                    "dependent_field": "Geographical Area",
                },
                # {
                #     "trigger_field": "TPA",
                #     "dependent_field": "Applicable Network",
                # },
                {
                    "trigger_field": "TPA",
                    "dependent_field": "Co-Insurance",
                },
                {
                    "trigger_field": "TPA",
                    "dependent_field": "Deductible",
                },
                {
                    "trigger_field": "TPA",
                    "dependent_field": "Dental Cover",
                },
                {
                    "trigger_field": "TPA",
                    "dependent_field": "Optical Cover",
                },
                {
                    "trigger_field": "TPA",
                    "dependent_field": "Lab & X-Ray",
                }
            ]
        }
        
        # Store validation results for Excel export
        self.validation_results = []
        
    def validate_conditions(self, df_extracted: pd.DataFrame, df_database: pd.DataFrame) -> pd.DataFrame:
        """
        Validate special care conditions between extracted and database data.
        
        Args:
            df_extracted: Extracted data with original field names
            df_database: Database data with DB field names
            
        Returns:
            DataFrame with validation results for Special_Care sheet
        """
        logger.info("Starting condition validation with mapping service...")
        
        # Reset results
        self.validation_results = []
        
        # Process each company's field relationships
        for company, relationships in self.field_relationships.items():
            logger.info(f"Processing company: {company}")
            
            # Filter data for this company
            company_extracted = df_extracted[df_extracted['Company'] == company].copy()
            company_database = df_database[df_database['Company'] == company].copy()
            
            if company_extracted.empty:
                logger.warning(f"No extracted data found for company: {company}")
                continue
                
            if company_database.empty:
                logger.warning(f"No database data found for company: {company}")
                continue
            
            # Special handling for SUKOON INSURANCE
            if company == "SUKOON INSURANCE":
                # Load special SUKOON database data
                sukoon_database = self._load_sukoon_special_database()
                logger.info(f"Loaded SUKOON database: {len(sukoon_database)} records")
                
                # Get unique TPA values from the extracted data, excluding null/empty values
                unique_tpas = company_extracted['TPA'].dropna().unique()
                # Filter out empty strings and non-numeric TPA values
                valid_tpas = [tpa for tpa in unique_tpas if str(tpa).strip() and str(tpa).strip() != 'N/A']
                
                if not valid_tpas:
                    logger.warning(f"No valid TPA values found for SUKOON. Available TPAs: {unique_tpas}")
                    continue
                    
                logger.info(f"Found valid TPAs for SUKOON: {valid_tpas}")

                for tpa_value in valid_tpas:
                    logger.info(f"  Processing for TPA: {tpa_value}")
                    # Filter data for the specific TPA - ensure both are same type
                    tpa_extracted = company_extracted[company_extracted['TPA'] == tpa_value]
                    # Convert TPA to string for filtering since database stores TPA as string
                    tpa_database = sukoon_database[sukoon_database['TPA'] == str(tpa_value)]
                    
                    logger.info(f"  TPA {tpa_value}: Extracted records: {len(tpa_extracted)}, Database records: {len(tpa_database)}")

                    # Process each relationship for this TPA using the new method
                    for relationship in relationships:
                        if relationship['trigger_field'] == 'TPA':
                            self._process_sukoon_tpa_relationship(tpa_extracted, tpa_database, relationship['dependent_field'])
            else:
                # Original logic for other companies
                for relationship in relationships:
                    self._process_relationship(company, relationship, company_extracted, company_database)
        
        # Create results DataFrame
        results_df = self._create_results_dataframe()
        return results_df

    def _process_relationship(self, company: str, relationship: Dict[str, Any], 
                            company_extracted: pd.DataFrame, company_database: pd.DataFrame):
        """Process a single field relationship for a company"""
        
        # Extract relationship components
        trigger_field = relationship['trigger_field']
        dependent_field = relationship['dependent_field']
        conditions = relationship.get('conditions', {})
        
        logger.info(f"  Processing relationship: '{trigger_field}' -> '{dependent_field}'")
        
        # Apply additional conditions if specified
        filtered_extracted = company_extracted.copy()
        filtered_database = company_database.copy()
        
        if conditions:
            logger.info(f"    Applying conditions: {conditions}")
            for condition_field, condition_value in conditions.items():
                if condition_field in filtered_extracted.columns:
                    filtered_extracted = filtered_extracted[
                        filtered_extracted[condition_field] == condition_value
                    ]
                if condition_field in filtered_database.columns:
                    filtered_database = filtered_database[
                        filtered_database[condition_field] == condition_value
                    ]
        
        # Special handling for SUKOON INSURANCE TPA trigger
        if company == "SUKOON INSURANCE" and trigger_field == "TPA":
            # For SUKOON, TPA is a column value, not a dropdown field
            # We process each unique TPA value separately in validate_conditions
            self._process_sukoon_tpa_relationship(filtered_extracted, filtered_database, dependent_field)
            return
        
        # Map extracted field names to database field names using mapping service
        trigger_db_name, _ = self.mapping_service.get_mapping_for_field(trigger_field, company)
        dependent_db_name, _ = self.mapping_service.get_mapping_for_field(dependent_field, company)
        
        # Find field data in both datasets
        trigger_extracted_data = self._find_field_data(filtered_extracted, trigger_field)
        trigger_database_data = self._find_field_data(filtered_database, trigger_db_name)
        dependent_extracted_data = self._find_field_data(filtered_extracted, dependent_field)
        dependent_database_data = self._find_field_data(filtered_database, dependent_db_name)
        
        # Create validation result
        validation_result = self._create_validation_result(
            company=company,
            trigger_field_mapped=trigger_db_name,
            dependent_field_mapped=dependent_db_name,
            trigger_extracted_data=trigger_extracted_data,
            dependent_extracted_data=dependent_extracted_data,
            trigger_database_data=trigger_database_data,
            dependent_database_data=dependent_database_data
        )
        
        self.validation_results.append(validation_result)
    
    def _process_sukoon_tpa_relationship(self, company_extracted: pd.DataFrame, 
                                       company_database: pd.DataFrame, dependent_field: str):
        """Special processing for SUKOON INSURANCE TPA relationships"""
        
        # Get the TPA value from the extracted data (it should be consistent within the filtered data)
        tpa_values = company_extracted['TPA'].dropna().unique()
        
        if len(tpa_values) == 0:
            logger.warning("No TPA values found for SUKOON relationship")
            return
        
        # Validate that we have a proper TPA value
        valid_tpa_values = [tpa for tpa in tpa_values if str(tpa).strip() and str(tpa).strip() != 'N/A' and str(tpa) != 'nan']
        
        if len(valid_tpa_values) == 0:
            logger.warning(f"No valid TPA values found for SUKOON relationship. Available: {tpa_values}")
            return
            
        # Use the first (and should be only) valid TPA value
        tpa_value = str(valid_tpa_values[0])
        logger.info(f"    Processing SUKOON TPA relationship for TPA: {tpa_value}")
        
        # Manual mapping for SUKOON INSURANCE fields since they're not in the mapping service
        sukoon_field_mapping = {
            "Geographical Area": "Terotory",
            # "Applicable Network": "Network", 
            "Co-Insurance": "DiagnosticCopay", 
            "Deductible": "Deductable",
            "Dental Cover": "Dental",
            "Optical Cover": "Optical", 
            "Lab & X-Ray": "Lab&X-Ray"
        }
        
        # Get the mapped database field name
        dependent_db_name = sukoon_field_mapping.get(dependent_field, dependent_field)
        
        # Find dependent field data in extracted data
        dependent_extracted_data = self._find_field_data(company_extracted, dependent_field)
        
        # Find dependent field data in database for the same TPA value
        # Filter database data by TPA value first - ensure string type matching
        tpa_filtered_database = company_database[company_database['TPA'] == str(tpa_value)]
        
        # Debug logging for database structure
        logger.debug(f"    TPA filtered database shape: {tpa_filtered_database.shape}")
        logger.debug(f"    TPA filtered database columns: {list(tpa_filtered_database.columns)}")
        
        # Check for field name column
        field_column = None
        for col in ['field name', 'Dropdown_Name', 'Field_Name']:
            if col in tpa_filtered_database.columns:
                field_column = col
                logger.debug(f"    Found field column: {col}")
                break
        
        if field_column:
            unique_field_names = tpa_filtered_database[field_column].unique()
            logger.debug(f"    Available field names in database: {sorted(unique_field_names)}")
            logger.debug(f"    Looking for field: '{dependent_db_name}'")
        
        dependent_database_data = self._find_field_data(tpa_filtered_database, dependent_db_name)
        
        logger.debug(f"    SUKOON TPA {tpa_value}: Found {len(dependent_extracted_data)} extracted records for {dependent_field}")
        logger.debug(f"    SUKOON TPA {tpa_value}: Found {len(dependent_database_data)} database records for {dependent_db_name}")
        
        # Extract values
        dependent_extracted_values = self._extract_values(dependent_extracted_data)
        dependent_database_values = self._extract_values(dependent_database_data)
        
        # If no database values found, indicate this clearly
        if not dependent_database_values:
            if dependent_db_name and dependent_db_name != dependent_field:
                dependent_database_values = [f"Not found in Database (looking for: {dependent_db_name})"]
            else:
                dependent_database_values = ["Not found in Database"]
        
        # Calculate Values_Mismatch for SUKOON
        values_mismatch = self._calculate_values_mismatch(
            dependent_extracted_values, dependent_database_values
        )
        
        # Create context information (region, network, etc.)
        context_info = self._create_context_info(company_extracted, pd.DataFrame())
        context_info['TPA'] = tpa_value  # Set the TPA value explicitly
        
        # Create validation result for this SUKOON TPA relationship
        result = {
            'Company': "SUKOON INSURANCE",
            'TPA': tpa_value,
            'Network': context_info.get('Network', ''),
            'Region': context_info.get('Region', ''),
            'Trigger_Field_Mapped': "TPA",  # The trigger is the TPA column
            'Trigger_Extracted_Values': tpa_value,  # The TPA value itself
            'Dependent_Field_Mapped': dependent_db_name if dependent_db_name else dependent_field,
            'Dependent_Extracted_Values': ','.join(dependent_extracted_values) if dependent_extracted_values else "",
            'Trigger_Database_Values': tpa_value,  # Same TPA value in database
            'Dependent_Database_Values': ','.join(dependent_database_values) if dependent_database_values else "Not found in Database",
            'Values_Mismatch': values_mismatch
        }
        
        self.validation_results.append(result)
    
    def _load_sukoon_special_database(self) -> pd.DataFrame:
        """Load special SUKOON database data from database"""
        try:
            logger.info("Loading SUKOON special data from database")
            
            with DataComparisonDBService() as db_service:
                # Query for SUKOON data with all the special fields
                query = """
                    SELECT CTN_ID, Broker_ID, Company, TPA, Network, Region, 
                           Dropdown_Name, Selection_Value
                    FROM Medical_CTN_Cascading_Dropdown 
                    WHERE UPPER(Company) LIKE '%SUKOON%'
                    AND Dropdown_Name IN ('Terotory', 'DiagnosticCopay', 'Deductable', 
                                         'Dental', 'Optical', 'Lab&X-Ray', 'BrokerCommission', 
                                         'Business_Nature', 'Medicine')
                    ORDER BY Dropdown_Name, Selection_Value
                """
                
                results = db_service.db.fetch_all(query)
                
                if not results:
                    logger.warning("No SUKOON special data found in database")
                    return pd.DataFrame()
                
                df_sukoon = pd.DataFrame(results)
                
                # Standardize company name to match condition validator expectations
                df_sukoon['Company'] = 'SUKOON INSURANCE'
                
                logger.info(f"Loaded {len(df_sukoon)} SUKOON special records from database")
                if not df_sukoon.empty:
                    logger.info(f"Available fields: {sorted(df_sukoon['Dropdown_Name'].unique())}")
                
                return df_sukoon
                
        except Exception as e:
            logger.error(f"Error loading SUKOON special database: {e}")
            return pd.DataFrame()
    
    def _find_field_data(self, df: pd.DataFrame, field_name: str) -> pd.DataFrame:
        """Find data for a specific field name"""
        
        # Check which column contains the field names
        field_column = None
        for col in ['field name', 'Dropdown_Name', 'Field_Name']:
            if col in df.columns:
                field_column = col
                break
        
        if not field_column:
            logger.warning(f"No field name column found. Available columns: {list(df.columns)}")
            return pd.DataFrame()
        
        # Filter by field name
        filtered = df[df[field_column] == field_name]
        
        return filtered
    
    def _create_validation_result(self, company: str, trigger_field_mapped: str, 
                                dependent_field_mapped: str,
                                trigger_extracted_data: pd.DataFrame,
                                dependent_extracted_data: pd.DataFrame,
                                trigger_database_data: pd.DataFrame,
                                dependent_database_data: pd.DataFrame) -> Dict[str, Any]:
        """Create a validation result dictionary"""
        
        # Extract values from dataframes
        trigger_extracted_values = self._extract_values(trigger_extracted_data)
        trigger_database_values = self._extract_values(trigger_database_data)
        dependent_extracted_values = self._extract_values(dependent_extracted_data)
        dependent_database_values = self._extract_values(dependent_database_data)
        
        # Create context information
        context_info = self._create_context_info(trigger_extracted_data, dependent_extracted_data)
        
        # Only mark as "Not Covered" if trigger has values but dependent doesn't
        if trigger_extracted_values and not dependent_extracted_values:
            dependent_extracted_values = ["Not Covered"]
        
        if trigger_database_values and not dependent_database_values:
            dependent_database_values = ["Not Covered"]
        
        # Calculate Values_Mismatch
        values_mismatch = self._calculate_values_mismatch(
            dependent_extracted_values, dependent_database_values
        )
        
        # Return the validation result
        result = {
            'Company': company,
            'TPA': context_info.get('TPA', ''),
            'Network': context_info.get('Network', ''),
            'Region': context_info.get('Region', ''),
            'Trigger_Field_Mapped': trigger_field_mapped,
            'Trigger_Extracted_Values': ','.join(trigger_extracted_values) if trigger_extracted_values else "",
            'Dependent_Field_Mapped': dependent_field_mapped,
            'Dependent_Extracted_Values': ','.join(dependent_extracted_values) if dependent_extracted_values else "",
            'Trigger_Database_Values': ','.join(trigger_database_values) if trigger_database_values else "",
            'Dependent_Database_Values': ','.join(dependent_database_values) if dependent_database_values else "",
            'Values_Mismatch': values_mismatch
        }

        return result
        
    def _calculate_values_mismatch(self, extracted_values: List[str], database_values: List[str]) -> str:
        """
        Calculate the mismatch between extracted and database values.
        Returns a string describing the mismatches.
        """
        if not extracted_values and not database_values:
            return ""
        
        # Convert to sets for comparison, excluding placeholder values
        extracted_set = set()
        database_set = set()
        
        # Process extracted values
        for val in extracted_values:
            val_str = str(val).strip()
            if val_str and val_str not in ["Not Covered", "Not found in Database"]:
                extracted_set.add(val_str)
        
        # Process database values  
        for val in database_values:
            val_str = str(val).strip()
            if val_str and val_str not in ["Not Covered", "Not found in Database"]:
                if not val_str.startswith("Not found in Database"):
                    database_set.add(val_str)
        
        # Calculate differences
        only_in_extracted = extracted_set - database_set
        only_in_database = database_set - extracted_set
        
        mismatch_parts = []
        
        if only_in_extracted:
            mismatch_parts.append(f"Only in Extracted: {', '.join(sorted(only_in_extracted))}")
        
        if only_in_database:
            mismatch_parts.append(f"Only in Database: {', '.join(sorted(only_in_database))}")
        
        # Special cases for not found/not covered
        if any("Not found in Database" in str(val) for val in database_values) and extracted_set:
            mismatch_parts.append(f"Missing from Database: {', '.join(sorted(extracted_set))}")
        
        if "Not Covered" in extracted_values and database_set:
            mismatch_parts.append(f"Not covered in Extracted but exists in Database: {', '.join(sorted(database_set))}")
        
        return "; ".join(mismatch_parts) if mismatch_parts else ""
        
    def _extract_values(self, df: pd.DataFrame) -> List[str]:
        """Extract unique selection values from dataframe"""
        
        if df.empty or 'Selection_Value' not in df.columns:
            return []
        
        values = []
        for value in df['Selection_Value'].dropna():
            if isinstance(value, list):
                values.extend([str(v).strip() for v in value if str(v).strip()])
            else:
                val_str = str(value).strip()
                if val_str:
                    values.append(val_str)
        
        return sorted(list(set(values)))
    
    def _create_context_info(self, trigger_extracted: pd.DataFrame, 
                           dependent_extracted: pd.DataFrame) -> Dict[str, str]:
        """Create context information from the extracted data"""
        
        context = {'TPA': '', 'Network': '', 'Region': ''}
        
        # Use trigger data first, then dependent data as fallback
        primary_df = trigger_extracted if not trigger_extracted.empty else dependent_extracted
        
        if not primary_df.empty:
            for field in context.keys():
                if field in primary_df.columns:
                    unique_values = primary_df[field].dropna().unique()
                    if len(unique_values) > 0:
                        context[field] = str(unique_values[0])
        
        return context
    
    def _create_results_dataframe(self) -> pd.DataFrame:
        """Create DataFrame from validation results"""
        
        if not self.validation_results:
            logger.warning("No validation results to create DataFrame")
            return pd.DataFrame()
        
        df = pd.DataFrame(self.validation_results)
        
        # Sort by company
        df = df.sort_values(['Company', 'Trigger_Field_Mapped'])
        
        logger.info(f"Created validation results DataFrame with {len(df)} records")
        
        return df
    
    def create_special_care_sheet(self, df_extracted: pd.DataFrame, df_database: pd.DataFrame) -> pd.DataFrame:
        """
        Create Special Care sheet with condition validation results (excluding Sukoon).
        
        Args:
            df_extracted: Extracted data with original field names
            df_database: Database data with DB field names
            
        Returns:
            DataFrame formatted for Special_Care sheet (excluding Sukoon records)
        """
        
        logger.info("Creating Special Care sheet (excluding Sukoon)...")
        
        # Validate conditions for all companies
        validation_df = self.validate_conditions(df_extracted, df_database)
        
        if validation_df.empty:
            logger.warning("No validation results found")
            return pd.DataFrame()
        
        # Filter out SUKOON INSURANCE records (using consistent case)
        # special_care_df = validation_df[
        #     (validation_df['Company'] != 'SUKOON INSURANCE')
        # ].copy()
        special_care_df = validation_df.copy()
       
        if special_care_df.empty:
            logger.warning("No non-Sukoon validation results found")
            return pd.DataFrame()
        
        # Add timestamp
        special_care_df['Validation_Timestamp'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Reorder columns for better readability
        key_columns = ['Company', 'TPA', 'Network', 'Region']
        other_columns = [col for col in special_care_df.columns if col not in key_columns + ['Validation_Timestamp']]
        
        final_order = key_columns + other_columns + ['Validation_Timestamp']
        special_care_df = special_care_df[final_order]
        
        logger.info(f"Created Special Care sheet with {len(special_care_df)} records (excluding Sukoon)")
        
        return special_care_df