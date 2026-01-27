import pandas as pd
from typing import Dict, List, Any, Tuple
from src.utils.logger import logger

class MappingService:
    """Handles data mapping operations with company-specific fallback mechanism"""
    
    def __init__(self):
        # Direct mapping: request_name -> db_name (from medical_dropdown_field_mapping)
        self.direct_mappings = {}
        # Company-specific direct mapping: (request_name, company) -> db_name
        self.company_specific_direct_mappings = {}
        
        # Two-step mappings
        # Global: extracted_dropdown_name -> request_name (when company is NULL)
        self.global_request_mappings = {}
        # Company-specific: (extracted_dropdown_name, company) -> request_name
        self.company_specific_mappings = {}
        # Step 2: request_name -> db_name (from medical_dropdown_field_mapping)  
        self.dropdown_mappings = {}
        
        # Combined mappings for easy lookup
        self.combined_global_mappings = {}
        self.combined_company_mappings = {}
        
        # Statistics
        self.direct_mapping_used = 0
        self.global_two_step_mapping_used = 0
        self.company_specific_mapping_used = 0
        self.no_mapping_found = 0
        self.missing_mappings = set()

    def load_mappings(self, direct_mappings_dict: Dict[str, str], global_request_mappings_dict: Dict[str, str], 
                     company_specific_mappings_dict: Dict[Tuple[str, str], str], dropdown_mappings_dict: Dict[str, str],
                     company_specific_direct_mappings_dict: Dict[Tuple[str, str], str] = None):
        """
        Load all mapping dictionaries with company-specific fallback mechanism.
        
        Args:
            direct_mappings_dict: request_name -> db_name (from medical_dropdown_field_mapping)
            global_request_mappings_dict: extracted_dropdown_name -> request_name (global mappings)
            company_specific_mappings_dict: (extracted_dropdown_name, company) -> request_name
            dropdown_mappings_dict: request_name -> db_name (from medical_dropdown_field_mapping)
            company_specific_direct_mappings_dict: (request_name, company) -> db_name (optional)
        """
        self.direct_mappings = direct_mappings_dict
        self.global_request_mappings = global_request_mappings_dict
        self.company_specific_mappings = company_specific_mappings_dict
        self.dropdown_mappings = dropdown_mappings_dict
        self.company_specific_direct_mappings = company_specific_direct_mappings_dict or {}
        
        logger.info(f"Loaded mappings:")
        logger.info(f"  Direct mappings: {len(self.direct_mappings)}")
        logger.info(f"  Company-specific direct mappings: {len(self.company_specific_direct_mappings)}")
        logger.info(f"  Global request mappings: {len(self.global_request_mappings)}")
        logger.info(f"  Company-specific mappings: {len(self.company_specific_mappings)}")
        logger.info(f"  Dropdown mappings: {len(self.dropdown_mappings)}")
        
        # Create combined mappings
        self._create_combined_mappings()
        
        logger.info(f"  Combined global mappings: {len(self.combined_global_mappings)}")
        logger.info(f"  Combined company mappings: {len(self.combined_company_mappings)}")
        
        # Log mapping strategy
        self._log_mapping_strategy()

    def _create_combined_mappings(self):
        """Create combined mappings by chaining the mapping steps."""
        # Global combined mappings: extracted_dropdown_name -> db_name
        self.combined_global_mappings = {}
        for extracted_name, request_name in self.global_request_mappings.items():
            if request_name in self.dropdown_mappings:
                db_name = self.dropdown_mappings[request_name]
                self.combined_global_mappings[extracted_name] = db_name
        
        # Company-specific combined mappings: (extracted_dropdown_name, company) -> db_name
        self.combined_company_mappings = {}
        for (extracted_name, company), request_name in self.company_specific_mappings.items():
            if request_name in self.dropdown_mappings:
                db_name = self.dropdown_mappings[request_name]
                self.combined_company_mappings[(extracted_name, company)] = db_name

    def _log_mapping_strategy(self):
        """Log the mapping strategy and overlaps."""
        direct_fields = set(self.direct_mappings.keys())
        global_fields = set(self.combined_global_mappings.keys())
        company_fields = set([extracted_name for extracted_name, company in self.combined_company_mappings.keys()])
        
        logger.info(f"Mapping Strategy Analysis:")
        logger.info(f"  Fields with direct mapping: {len(direct_fields)}")
        logger.info(f"  Fields with global two-step mapping: {len(global_fields)}")
        logger.info(f"  Fields with company-specific mapping: {len(company_fields)}")
        
        # Check overlaps
        direct_global_overlap = direct_fields & global_fields
        global_company_overlap = global_fields & company_fields
        
        if direct_global_overlap:
            logger.info(f"  Fields with both direct and global mappings: {len(direct_global_overlap)}")
        if global_company_overlap:
            logger.info(f"  Fields with both global and company-specific mappings: {len(global_company_overlap)}")

    def get_mapping_for_field(self, extracted_name: str, company: str = None) -> Tuple[str, str]:
        """
        Get mapping for a field using company-specific fallback mechanism.
        
        Priority:
        1. Company-specific direct mapping (if company provided)
        2. General direct mapping (extracted_name as request_name)
        3. Company-specific two-step mapping (if company provided)
        4. Global two-step mapping
        5. No mapping found
        
        Args:
            extracted_name: The extracted dropdown name
            company: The company name (optional)
            
        Returns:
            tuple: (mapped_db_name, mapping_type)
        """
        extracted_name = str(extracted_name).strip()
        company = str(company).strip() if company and str(company).strip() != 'nan' else None
        
        # Add debug logging for input parameters
        logger.debug(f"get_mapping_for_field called with: extracted_name='{extracted_name}', company='{company}'")
        
        # STEP 1: Try company-specific direct mapping first (if company provided)
        if company:
            company_specific_direct_mapping = self._get_company_specific_direct_mapping(extracted_name, company)
            if company_specific_direct_mapping:
                db_name = company_specific_direct_mapping
                logger.debug(f"Company-specific direct mapping: '{extracted_name}' + '{company}' -> '{db_name}'")
                return db_name, 'company-specific-direct'
        
        # STEP 2: Try general direct mapping (only if no company provided OR no company-specific mapping exists for THIS specific company)
        if extracted_name in self.direct_mappings:
            if company:
                # Check if THIS specific company has a company-specific direct mapping for this field
                company_key = (extracted_name, company)
                has_company_specific_mapping_for_this_company = company_key in self.company_specific_direct_mappings
                
                if has_company_specific_mapping_for_this_company:
                    # This company has a specific mapping, but we didn't find it in Step 1 (shouldn't happen)
                    logger.debug(f"Unexpected: Company-specific mapping exists but wasn't found in Step 1: {company_key}")
                else:
                    # This company doesn't have a specific mapping, use general direct mapping
                    db_name = self.direct_mappings[extracted_name]
                    logger.debug(f"Direct mapping: '{extracted_name}' -> '{db_name}' (no company-specific mapping for '{company}')")
                    return db_name, 'direct'
            else:
                # No company provided, use direct mapping
                db_name = self.direct_mappings[extracted_name]
                logger.debug(f"Direct mapping: '{extracted_name}' -> '{db_name}' (no company provided)")
                return db_name, 'direct'
        
        # STEP 3: Try company-specific mapping (if company provided)
        if company:
            company_key = (extracted_name, company)
            if company_key in self.combined_company_mappings:
                db_name = self.combined_company_mappings[company_key]
                request_name = self.company_specific_mappings.get(company_key, 'unknown')
                logger.debug(f"Company-specific mapping: '{extracted_name}' + '{company}' -> '{request_name}' -> '{db_name}'")
                return db_name, 'company-specific'
        
        # STEP 4: Try global two-step mapping
        if extracted_name in self.combined_global_mappings:
            db_name = self.combined_global_mappings[extracted_name]
            request_name = self.global_request_mappings.get(extracted_name, 'unknown')
            logger.debug(f"Global mapping: '{extracted_name}' -> '{request_name}' -> '{db_name}'")
            return db_name, 'global-two-step'
        
        #STEP 5: No mapping found
        logger.debug(f"No mapping found for: '{extracted_name}'" + (f" + '{company}'" if company else ""))
        return extracted_name, 'none'

    def _get_company_specific_direct_mapping(self, extracted_name: str, company: str) -> str:
        """
        Get company-specific direct mapping for a field.
        
        Args:
            extracted_name: The extracted dropdown name
            company: The company name
            
        Returns:
            The DB name if company-specific direct mapping exists, None otherwise
        """
        if not extracted_name or not company:
            return None
            
        # Check if there's a company-specific direct mapping
        company_key = (extracted_name, company)
        if company_key in self.company_specific_direct_mappings:
            logger.debug(f"Found company-specific direct mapping: {company_key} -> {self.company_specific_direct_mappings[company_key]}")
            return self.company_specific_direct_mappings[company_key]
        
        # Debug: Show what company-specific mappings exist for this field
        field_specific_mappings = [
            (field, comp, db_name) 
            for (field, comp), db_name in self.company_specific_direct_mappings.items()
            if field == extracted_name
        ]
        
        if field_specific_mappings:
            logger.debug(f"Available company-specific mappings for field '{extracted_name}': {field_specific_mappings}")
            logger.debug(f"Looking for company: '{company}' (type: {type(company)})")
        
        return None

    def debug_field_mappings(self, extracted_name: str, company: str = None) -> Dict[str, Any]:
        """
        Debug helper to show all available mappings for a specific field.
        
        Args:
            extracted_name: The extracted dropdown name to debug
            company: The company name (optional)
            
        Returns:
            Dictionary with all mapping information for this field
        """
        debug_info = {
            'extracted_name': extracted_name,
            'company': company,
            'direct_mapping_exists': extracted_name in self.direct_mappings,
            'direct_mapping_value': self.direct_mappings.get(extracted_name),
            'company_specific_direct_mappings': [],
            'global_two_step_mapping_exists': extracted_name in self.combined_global_mappings,
            'global_two_step_mapping_value': self.combined_global_mappings.get(extracted_name),
            'company_specific_two_step_mappings': [],
        }
        
        # Find all company-specific direct mappings for this field
        for (field, comp), db_name in self.company_specific_direct_mappings.items():
            if field == extracted_name:
                debug_info['company_specific_direct_mappings'].append({
                    'company': comp,
                    'db_name': db_name,
                    'matches_current_company': comp == company if company else False
                })
        
        # Find all company-specific two-step mappings for this field
        for (field, comp), db_name in self.combined_company_mappings.items():
            if field == extracted_name:
                request_name = self.company_specific_mappings.get((field, comp), 'unknown')
                debug_info['company_specific_two_step_mappings'].append({
                    'company': comp,
                    'request_name': request_name,
                    'db_name': db_name,
                    'matches_current_company': comp == company if company else False
                })
        
        return debug_info

    def get_companies_for_field(self, extracted_name: str) -> Dict[str, List[str]]:
        """
        Get all companies that have mappings for a specific field.
        
        Args:
            extracted_name: The field name to check
            
        Returns:
            Dictionary with 'direct' and 'two_step' keys containing lists of companies
        """
        companies = {
            'direct': [],
            'two_step': []
        }
        
        # Direct mappings
        for (field, comp), db_name in self.company_specific_direct_mappings.items():
            if field == extracted_name:
                companies['direct'].append(comp)
        
        # Two-step mappings
        for (field, comp), db_name in self.combined_company_mappings.items():
            if field == extracted_name:
                companies['two_step'].append(comp)
        
        return companies

    def get_db_display_name(self, db_name: str) -> str:
        """
        Get display name for database field.
        Priority: db_name (if exists) > request_name > db_name
        """
        db_name = str(db_name).strip()
        
        # First priority: if db_name is valid, use it
        if db_name and db_name != 'nan' and db_name.strip():
            return db_name
        
        # Second priority: find request_name for this db_name
        for request_name, mapped_db_name in self.direct_mappings.items():
            if mapped_db_name == db_name:
                logger.debug(f"Using request name for display: '{db_name}' -> '{request_name}'")
                return request_name
        
        # Fallback: return original db_name
        return db_name

    def apply_mappings_for_comparison(self, df_extracted: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Apply mappings with company-specific logic but keep original data separate.
        
        Args:
            df_extracted: DataFrame with extracted data (original names)
            
        Returns:
            tuple: (df_mapped_for_comparison, df_original_for_display)
        """
        if df_extracted.empty or 'Dropdown_Name' not in df_extracted.columns:
            logger.warning("DataFrame is empty or missing 'Dropdown_Name' column")
            return df_extracted, df_extracted
        
        # Keep original data unchanged for display
        df_original = df_extracted.copy()
        
        # Create mapped copy for comparison logic
        df_mapped = df_extracted.copy()
        
        # Reset statistics
        self.direct_mapping_used = 0
        self.global_two_step_mapping_used = 0
        self.company_specific_mapping_used = 0
        self.no_mapping_found = 0
        self.missing_mappings = set()
        
        # Apply mappings with company context
        for idx, row in df_mapped.iterrows():
            original_name = str(row['Dropdown_Name']).strip()
            company = str(row.get('Company', '')).strip() if 'Company' in row else None
            
            # Get mapping with company context
            mapped_name, mapping_type = self.get_mapping_for_field(original_name, company)
            
            # Update ONLY the mapped DataFrame
            df_mapped.at[idx, 'Dropdown_Name'] = mapped_name
            
            # Update statistics
            if mapping_type == 'direct':
                self.direct_mapping_used += 1
            elif mapping_type == 'company-specific-direct':
                self.company_specific_mapping_used += 1
            elif mapping_type == 'company-specific':
                self.company_specific_mapping_used += 1
            elif mapping_type == 'global-two-step':
                self.global_two_step_mapping_used += 1
            else:
                self.no_mapping_found += 1
                self.missing_mappings.add(f"{original_name}" + (f" ({company})" if company else ""))
        
        # Log results
        total_mapped = self.direct_mapping_used + self.global_two_step_mapping_used + self.company_specific_mapping_used
        initial_count = len(df_mapped)
        logger.info(f"Mapping Results:")
        logger.info(f"  Total records processed: {initial_count}")
        logger.info(f"  Direct mappings used: {self.direct_mapping_used}")
        logger.info(f"  Company-specific mappings used: {self.company_specific_mapping_used}")
        logger.info(f"  Global two-step mappings used: {self.global_two_step_mapping_used}")
        logger.info(f"  No mapping found: {self.no_mapping_found}")
        logger.info(f"  Success rate: {total_mapped}/{initial_count} ({(total_mapped/initial_count*100):.1f}%)")
        
        return df_mapped, df_original

    def build_global_mappings(self, df_extracted: pd.DataFrame, df_database: pd.DataFrame):
        """Analyze mapping coverage with company-specific context"""
        logger.info("Analyzing mapping coverage with company specificity...")
        
        extracted_dropdowns = set()
        database_dropdowns = set()
        
        if not df_extracted.empty and 'Dropdown_Name' in df_extracted.columns:
            extracted_dropdowns = set(df_extracted['Dropdown_Name'].unique())
        
        if not df_database.empty and 'Dropdown_Name' in df_database.columns:
            database_dropdowns = set(df_database['Dropdown_Name'].unique())
        
        logger.info(f"Data Analysis:")
        logger.info(f"  Unique extracted dropdown names: {len(extracted_dropdowns)}")
        logger.info(f"  Unique database dropdown names: {len(database_dropdowns)}")
        
        # Check coverage with company context
        if not df_extracted.empty and 'Company' in df_extracted.columns:
            company_field_combinations = set()
            for _, row in df_extracted.iterrows():
                dropdown_name = str(row['Dropdown_Name'])
                company = str(row.get('Company', ''))
                company_field_combinations.add((dropdown_name, company))
            
            logger.info(f"  Unique (field, company) combinations: {len(company_field_combinations)}")
        
        # Coverage analysis
        direct_covered = set(self.direct_mappings.keys()) & extracted_dropdowns
        global_covered = set(self.combined_global_mappings.keys()) & extracted_dropdowns
        company_covered = set([name for name, company in self.combined_company_mappings.keys()]) & extracted_dropdowns
        
        total_covered = direct_covered | global_covered | company_covered
        uncovered = extracted_dropdowns - total_covered
        
        logger.info(f"Coverage Analysis:")
        logger.info(f"  Fields covered by direct mapping: {len(direct_covered)}")
        logger.info(f"  Fields covered by global mapping: {len(global_covered)}")
        logger.info(f"  Fields covered by company-specific mapping: {len(company_covered)}")
        logger.info(f"  Total unique fields covered: {len(total_covered)}")
        logger.info(f"  Fields without mapping: {len(uncovered)}")
        
        if len(extracted_dropdowns) > 0:
            coverage_percent = (len(total_covered) / len(extracted_dropdowns)) * 100
            logger.info(f"  Overall coverage: {len(total_covered)}/{len(extracted_dropdowns)} ({coverage_percent:.1f}%)")

    def get_mapping_summary(self) -> Dict[str, Any]:
        """Get summary of mapping operations with company-specific stats."""
        return {
            'direct_mappings_count': len(self.direct_mappings),
            'global_request_mappings_count': len(self.global_request_mappings),
            'company_specific_mappings_count': len(self.company_specific_mappings),
            'dropdown_mappings_count': len(self.dropdown_mappings),
            'combined_global_mappings_count': len(self.combined_global_mappings),
            'combined_company_mappings_count': len(self.combined_company_mappings),
            'direct_mapping_used': self.direct_mapping_used,
            'global_two_step_mapping_used': self.global_two_step_mapping_used,
            'company_specific_mapping_used': self.company_specific_mapping_used,
            'no_mapping_found': self.no_mapping_found,
            'missing_mappings_count': len(self.missing_mappings)
        }
    
    def get_request_name_for_display(self, extracted_field_name: str, company: str = None) -> str:
        """
        Get the request name (intermediate mapping name) for display in DB update sheets.
        
        Args:
            extracted_field_name: The extracted dropdown name
            company: The company name (optional)
            
        Returns:
            The request name if mapping exists, otherwise the extracted field name
        """
        extracted_field_name = str(extracted_field_name).strip()
        company = str(company).strip() if company and str(company).strip() != 'nan' else None
        
        # Check direct mappings first (extracted_field_name is the request_name)
        if extracted_field_name in self.direct_mappings:
            return extracted_field_name
        
        # Check company-specific mappings
        if company:
            company_key = (extracted_field_name, company)
            if company_key in self.company_specific_mappings:
                request_name = self.company_specific_mappings[company_key]
                logger.debug(f"Found company-specific request name: '{extracted_field_name}' + '{company}' -> '{request_name}'")
                return request_name
        
        # Check global request mappings
        if extracted_field_name in self.global_request_mappings:
            request_name = self.global_request_mappings[extracted_field_name]
            logger.debug(f"Found global request name: '{extracted_field_name}' -> '{request_name}'")
            return request_name
        
        # No mapping found, return original extracted field name
        return extracted_field_name