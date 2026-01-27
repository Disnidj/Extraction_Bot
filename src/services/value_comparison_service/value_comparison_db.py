import pandas as pd
from typing import Dict, Tuple, Any
from contextlib import contextmanager

from pandas import DataFrame

from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_LIVE_HOST, DB_LIVE_NAME, DB_LIVE_USER, DB_LIVE_PASSWORD
from src.utils.logger import logger
from src.config.constants import TARGET_PORTALS as target_companies, BROKER_PORTALS

class DataComparisonDBService:
    """Database service for data comparison operations with broker-aware filtering"""
    
    def __init__(self):
        self.db = MySQLDatabase(DB_LIVE_HOST, DB_LIVE_NAME, DB_LIVE_USER, DB_LIVE_PASSWORD)
        self._is_connected = False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup"""
        self.disconnect()
    
    def connect(self) -> bool:
        """Establish database connection if not already connected"""
        if not self._is_connected:
            try:
                if self.db.connect():
                    self._is_connected = True
                    logger.info("Database connection established")
                    return True
                else:
                    logger.error("Failed to establish database connection")
                    return False
            except Exception as e:
                logger.error(f"Connection error: {e}")
                return False
        return True
    
    def disconnect(self):
        """Close database connection if connected"""
        if self._is_connected:
            try:
                self.db.disconnect()
                self._is_connected = False
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Disconnection error: {e}")
    
    @contextmanager
    def _db_session(self):
        """Context manager for database session handling"""
        connected = self.connect()
        if not connected:
            raise ConnectionError("Failed to establish database connection")
        try:
            yield
        finally:
            self.disconnect()
    
    def fetch_all_data_with_mappings(self) -> tuple[
                                                  DataFrame, DataFrame, DataFrame, DataFrame, dict[str, str], dict[str, str], dict[
                                                      tuple[str, str], str], dict[str, str], dict[
                                                      tuple[str, str], str]] | tuple[
                                                  DataFrame, DataFrame, DataFrame, DataFrame, dict[Any, Any], dict[Any, Any], dict[Any, Any], dict[
                                                      Any, Any], dict[Any, Any]]:
        """Fetch broker-aware data and mappings in a single connection session"""
        try:
            with self._db_session():
                logger.info("Fetching broker-aware data and mappings in single session")
                
                # Fetch broker-aware database data
                self.df_database = self._fetch_broker_aware_database_data()
                self.df_tpa_dropdowns = self._fetch_all_tpa_dropdowns()
                self.df_network_dropdowns = self._fetch_all_network_dropdowns()
                self.df_iq_data_plans = self._fetch_all_iq_data_plans()
                
                direct_mappings, company_specific_direct_mappings = self._fetch_field_mappings_internal()
                global_request_mappings, company_specific_mappings = self._fetch_request_mappings_internal()
                dropdown_mappings = direct_mappings.copy()  # dropdown_mappings is same as direct_mappings
                
                logger.info("All broker-aware data and mappings fetched successfully")
                return (
                    self.df_database,
                    self.df_tpa_dropdowns,
                    self.df_network_dropdowns,
                    self.df_iq_data_plans, 
                    direct_mappings,
                    global_request_mappings,
                    company_specific_mappings,
                    dropdown_mappings,
                    company_specific_direct_mappings
                )
                
        except Exception as e:
            logger.error(f"Error in single session fetch: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, {}, {}, {}, {}    
        
    def _fetch_broker_aware_database_data(self) -> pd.DataFrame:
        """Fetch database data for companies that may exist in multiple brokers"""
        try:
            # Create company-to-brokers mapping
            company_to_brokers = self._build_company_to_brokers_mapping()
            
            # Log multi-broker companies
            multi_broker_companies = {comp: brokers for comp, brokers in company_to_brokers.items() if len(brokers) > 1}
            if multi_broker_companies:
                logger.info("Multi-broker companies found:")
                for company, brokers in multi_broker_companies.items():
                    logger.info(f"   {company}: Brokers {brokers}")
            
            logger.info(f"Company-to-Brokers mapping: {len(company_to_brokers)} companies mapped")
            
            # Fetch data for all broker-company combinations
            all_data = self._fetch_all_broker_data(company_to_brokers)
            
            # Combine and validate data
            return self._combine_and_validate_data(all_data)
            
        except Exception as e:
            logger.error(f"Error fetching multi-broker database data: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return pd.DataFrame()
    
    # This is for TPA comparison
    def _fetch_all_tpa_dropdowns(self) -> pd.DataFrame:
        """Fetch all TPA dropdowns for all companies/regions in one go."""
        query = """
            SELECT Company, Region, TPA
            FROM Medical_CTN_Cascading_Dropdown
            WHERE TPA IS NOT NULL AND TPA != ''
        """
        results = self.db.fetch_all(query)
        if results:
            return pd.DataFrame(results)
        else:
            return pd.DataFrame(columns=["Company", "Region", "TPA"])    

    # This is for Network comparison
    def _fetch_all_network_dropdowns(self) -> pd.DataFrame:
        query = """
            SELECT Company, Region, TPA, Network
            FROM Medical_CTN_Cascading_Dropdown
            WHERE Network IS NOT NULL AND Network != ''
        """
        results = self.db.fetch_all(query)
        if results:
            return pd.DataFrame(results)
        else:
            return pd.DataFrame(columns=["Company", "Region", "TPA", "Network"])   
         
    def _fetch_field_mappings_internal(self) -> Tuple[Dict[str, str], Dict[Tuple[str, str], str]]:
        """Internal method to fetch field mappings (assumes connection exists)"""
        try:
            query = """
                SELECT *
                FROM medical_dropdown_field_mapping
                WHERE Dropdown_Name IS NOT NULL 
                AND DB_Name IS NOT NULL
                ORDER BY created_date DESC
            """
            
            results = self.db.fetch_all(query)
            
            if not results:
                logger.warning("No field mapping data returned")
                return {}, {}
            
            df = pd.DataFrame(results)
            logger.info(f"Fetched {len(df)} field mapping records")
            
            general_mappings = {}
            company_specific_mappings = {}
            general_duplicate_count = 0
            company_duplicate_count = 0
            
            for _, row in df.iterrows():
                request_name = self._clean_string(row['Dropdown_Name'])
                db_name = self._clean_string(row['DB_Name'])
                company = self._clean_string(row.get('Company', '')) if 'Company' in row else None
                
                if not self._is_valid_string(request_name) or not self._is_valid_string(db_name):
                    continue
                
                if company and company.lower() not in ['null', 'none', '']:
                    # Company-specific mapping
                    company_key = (request_name, company)
                    if company_key in company_specific_mappings:
                        company_duplicate_count += 1
                    company_specific_mappings[company_key] = db_name
                else:
                    # General mapping
                    if request_name in general_mappings:
                        general_duplicate_count += 1
                    general_mappings[request_name] = db_name
            
            logger.info(f"Processed {len(general_mappings)} general field mappings")
            logger.info(f"Processed {len(company_specific_mappings)} company-specific field mappings")
            if general_duplicate_count > 0:
                logger.info(f"Found {general_duplicate_count} duplicate general field mappings, kept most recent")
            if company_duplicate_count > 0:
                logger.info(f"Found {company_duplicate_count} duplicate company-specific field mappings, kept most recent")
            
            return general_mappings, company_specific_mappings
            
        except Exception as e:
            logger.error(f"Error fetching field mappings: {e}")
            return {}, {}
    
    def _fetch_request_mappings_internal(self) -> Tuple[Dict[str, str], Dict[Tuple[str, str], str]]:
        """Internal method to fetch request mappings (assumes connection exists)"""
        try:
            query = """
                SELECT *
                FROM medical_dropdown_request_mapping
                WHERE request_name IS NOT NULL 
                AND extracted_dropdown_name IS NOT NULL
                ORDER BY created_date DESC
            """
            
            results = self.db.fetch_all(query)
            
            if not results:
                logger.warning("No request mapping data returned")
                return {}, {}
            
            df = pd.DataFrame(results)
            logger.info(f"Fetched {len(df)} request mapping records")
            
            global_mappings = {}
            company_mappings = {}
            duplicate_count = 0
            
            for _, row in df.iterrows():
                extracted_name = self._clean_string(row['extracted_dropdown_name'])
                request_name = self._clean_string(row['request_name'])
                company = self._clean_string(row.get('company', '')) if pd.notna(row.get('company')) else None
                
                if not self._is_valid_string(extracted_name) or not self._is_valid_string(request_name):
                    continue
                
                if company and self._is_valid_string(company):
                    key = (extracted_name, company)
                    if key in company_mappings:
                        duplicate_count += 1
                    company_mappings[key] = request_name
                else:
                    if extracted_name in global_mappings:
                        duplicate_count += 1
                    global_mappings[extracted_name] = request_name
            
            logger.info(f"Processed request mappings: Global={len(global_mappings)}, Company-specific={len(company_mappings)}")
            if duplicate_count > 0:
                logger.info(f"Found {duplicate_count} duplicate request mappings, kept most recent")
            
            return global_mappings, company_mappings
            
        except Exception as e:
            logger.error(f"Error fetching request mappings: {e}")
            return {}, {}
    
    def _clean_string(self, value) -> str:
        """Clean and normalize string values"""
        if pd.isna(value):
            return ""
        return str(value)
    
    def _is_valid_string(self, value: str) -> bool:
        """Check if string is valid (not empty, not 'nan')"""
        return bool(value and value.lower() != 'nan')
    
    def verify_broker_data(self, company: str, tpa: str, network: str, dropdown_name: str):
        """Verify what broker data exists for specific record"""
        try:
            with self._db_session():
                query = """
                    SELECT Broker_ID, Company, TPA, Network, Dropdown_Name, Selection_Value
                    FROM Medical_CTN_Cascading_Dropdown
                    WHERE Company = %s 
                        AND TPA = %s 
                        AND Network = %s 
                        AND Dropdown_Name = %s
                    ORDER BY Broker_ID, Selection_Value
                """
                
                results = self.db.fetch_all(query, [company, tpa, network, dropdown_name])
                
                if results:
                    df = pd.DataFrame(results)
                    logger.info(f"VERIFICATION for {company} - {dropdown_name}:")
                    for broker_id in sorted(df['Broker_ID'].unique()):
                        broker_data = df[df['Broker_ID'] == broker_id]
                        values = sorted(broker_data['Selection_Value'].tolist())
                        logger.info(f"   Broker {broker_id}: {values}")
                    return df
                else:
                    logger.info(f"No data found for {company} - {dropdown_name}")
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"Error in verification: {e}")
            return pd.DataFrame()

    def fetch_direct_mappings(self) -> Dict[str, str]:
        """Fetch direct mappings - useful for testing and debugging"""
        try:
            with self._db_session():
                general_mappings, _ = self._fetch_field_mappings_internal()
                return general_mappings
        except Exception as e:
            logger.error(f"Error in fetch_direct_mappings: {e}")
            return {}

    def fetch_request_mappings(self) -> Tuple[Dict[str, str], Dict[Tuple[str, str], str]]:
        """Fetch request mappings - useful for testing and debugging"""
        try:
            with self._db_session():
                return self._fetch_request_mappings_internal()
        except Exception as e:
            logger.error(f"Error in fetch_request_mappings: {e}")
            return {}, {}

    def fetch_dropdown_mappings(self) -> Dict[str, str]:
        """Fetch dropdown mappings - useful for testing and debugging"""
        try:
            with self._db_session():
                general_mappings, _ = self._fetch_field_mappings_internal()
                return general_mappings
        except Exception as e:
            logger.error(f"Error in fetch_dropdown_mappings: {e}")
            return {}

    def get_company_count(self, df: pd.DataFrame) -> int:
        """Helper method to get company count from dataframe"""
        if df.empty or 'Company' not in df.columns:
            return 0
        return df['Company'].nunique()
    
    def _fetch_all_iq_data_plans(self) -> pd.DataFrame:
        """Fetch all IQ Data Plans for comparison"""
        try:
            query = """
                SELECT *
                FROM IQ_Data_Plans
                WHERE Company IS NOT NULL AND Company != ''
                    AND Region IS NOT NULL AND Region != ''
                ORDER BY Company, Region, TPA, Plan, Network
            """
            
            results = self.db.fetch_all(query)
            if results:
                df = pd.DataFrame(results)
                logger.info(f"Fetched {len(df)} IQ Data Plans records")
                return df
            
            else:
                logger.warning("No IQ Data Plans found")
                return pd.DataFrame(columns=["Region", "Company", "TPA", "Plan", "Network"])
                
        except Exception as e:
            print(f"Error fetching IQ Data Plans: {e}")
            logger.error(f"Error fetching IQ Data Plans: {e}")
            return pd.DataFrame()
    
    def _build_company_to_brokers_mapping(self) -> Dict[str, list]:
        """Build mapping of companies to their associated brokers"""
        company_to_brokers = {}
        for broker_name, companies in BROKER_PORTALS.items():
            broker_id = int(broker_name.split()[1]) if "Broker" in broker_name else 0
            for company in companies:
                if company not in company_to_brokers:
                    company_to_brokers[company] = []
                company_to_brokers[company].append(broker_id)
        return company_to_brokers

    def _fetch_all_broker_data(self, company_to_brokers: Dict[str, list]) -> list:
        """Fetch data for all broker-company combinations"""
        all_data = []
        
        for broker_id in [1, 2, 3, 6]:  # Process each broker
            # Get companies that exist in this broker
            broker_companies = [comp for comp, brokers in company_to_brokers.items() if broker_id in brokers]
            
            if not broker_companies:
                logger.info(f"Broker {broker_id}: No companies assigned")
                continue
            
            logger.info(f"Broker {broker_id} companies ({len(broker_companies)}): {broker_companies}")
            
            # Fetch data for this broker
            broker_df = self._fetch_broker_data(broker_id, broker_companies)
            if not broker_df.empty:
                all_data.append(broker_df)
                
                # Log details for this broker
                unique_companies = broker_df['Company'].nunique()
                logger.info(f"Broker {broker_id}: {len(broker_df)} records, {unique_companies} companies")
            else:
                logger.warning(f"Broker {broker_id}: No data found")
        
        return all_data

    def _fetch_broker_data(self, broker_id: int, broker_companies: list) -> pd.DataFrame:
        """Fetch data for a specific broker and its companies"""
        try:
            # Create placeholders for IN clause
            placeholders = ', '.join(['%s'] * len(broker_companies))
            
            query = f"""
                SELECT Broker_ID, Company, TPA, Network, Region, 
                    Dropdown_Name, Selection_Value
                FROM Medical_CTN_Cascading_Dropdown
                WHERE Broker_ID = %s
                    AND Company IN ({placeholders})
                    AND Company IS NOT NULL 
                    AND Company != ''
                    AND Dropdown_Name IS NOT NULL 
                    AND Dropdown_Name != ''
                    AND Selection_Value IS NOT NULL 
                    AND Selection_Value != ''
                ORDER BY Company, Dropdown_Name, Selection_Value
            """
            
            # Parameters: broker_id + company list
            params = [broker_id] + broker_companies
            
            logger.info(f"Fetching Broker {broker_id} data")
            results = self.db.fetch_all(query, params)
            
            if results:
                return pd.DataFrame(results)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching data for broker {broker_id}: {e}")
            return pd.DataFrame()

    def _combine_and_validate_data(self, all_data: list) -> pd.DataFrame:
        """Combine all broker data and perform validation"""
        if not all_data:
            logger.warning("No broker-aware data found")
            return pd.DataFrame()
        
        df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Combined multi-broker data: {len(df)} total records")
        
        # Log broker distribution
        self._log_broker_distribution(df)
        
        return df

    def _log_broker_distribution(self, df: pd.DataFrame):
        """Log broker distribution statistics"""
        if 'Broker_ID' in df.columns:
            broker_counts = df['Broker_ID'].value_counts().sort_index()
            logger.info("Final records by Broker:")
            for broker_id, count in broker_counts.items():
                broker_companies_count = df[df['Broker_ID'] == broker_id]['Company'].nunique()
                logger.info(f"   Broker {broker_id}: {count} records, {broker_companies_count} companies")

    # def export_raw_database_to_excel(self, path: str = "raw_database_data_dump.xlsx"):
    #     """
    #     Export all raw database data (from all brokers/companies) to an Excel file for inspection.
    #     """
    #     try:
    #         df_database = self._fetch_broker_aware_database_data()
    #         if df_database is not None and not df_database.empty:
    #             df_database.to_excel(path, index=False)
    #             logger.info(f"Raw database data exported to {path}")
    #         else:
    #             logger.warning("No raw database data available to export.")
    #     except Exception as e:
    #         logger.error(f"Error exporting raw database data: {e}")