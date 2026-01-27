import pandas as pd
from src.utils.logger import logger
import re

def combine_fidelity_tpa_group(tpa_values, group_values):
    """
    For Fidelity United, combine each group value with each TPA value.
    Returns a list of combined strings: "<group> - <tpa>"
    """
    combined = []
    for group in group_values:
        group = str(group).strip()
        if not group or group.lower().startswith("select"):
            continue
        for tpa in tpa_values:
            tpa = str(tpa).strip()
            if not tpa or tpa.lower().startswith("select"):
                continue
            combined.append(f"{group} - {tpa}")
    return combined

def combine_fidelity_tpa_group_from_extracted(group_values, tpa_values):
    """
    For Fidelity United, combine each group value with each TPA value from extracted data.
    Returns a list of combined strings: "<group> - <tpa>"
    """
    combined = []
    for group in group_values:
        group = str(group).strip()
        if not group or group.lower().startswith("select"):
            continue
        for tpa in tpa_values:
            tpa = str(tpa).strip()
            if not tpa or tpa.lower().startswith("select"):
                continue
            combined.append(f"{group} - {tpa}")
    return combined

class TPAComparisonService:
    def __init__(self, db_service):
        self.db_service = db_service
        # Define values to exclude from TPA dropdown comparison
        self.excluded_values = {
            'select tpa',
            'please select',
            'Select Network Provider',
            'select',
            'choose tpa',
            'pick tpa',
            'select an option',
            'select option',
            '--select--',
            '--please select--',
            'default',
        }
        
        # Define company-specific exclusions: {company: {excluded_values}}
        self.company_specific_exclusions = {
            # 'SUKOON INSURANCE': set()
        }
        
        # Define company-specific TPA mappings: {company: {extracted_value: [db_values]}}
        self.company_tpa_mappings = {
            # 'WATANIA TAKAFUL': {
            #     'NAS': ['Plan - 1', 'Plan - 2', 'Plan - 3', 'Plan - 4']
            # }
        }

    def _should_exclude_value(self, value, company=None):
        if not value or not isinstance(value, str):
            return True

        cleaned_value = value.strip().lower()

        # Exclude if the value contains 'select'
        if "select" in cleaned_value:
            return True

        # Optionally, exclude other generic placeholders
        if cleaned_value in {"please select", "choose tpa", "pick tpa", "default", "none", "n/a", "na"}:
            return True

        # Company-specific exclusions
        if company and company in self.company_specific_exclusions:
            if cleaned_value in {v.lower() for v in self.company_specific_exclusions[company]}:
                logger.warning(f"Excluding company-specific value for '{company}': '{value}'")
                return True

        return False

    def _apply_company_tpa_mapping(self, extracted_tpas, company):
        """Apply company-specific TPA mappings to extracted values"""
        if company.strip().upper() not in self.company_tpa_mappings:
            return extracted_tpas
        
        company_mappings = self.company_tpa_mappings[company.strip().upper()]
        mapped_tpas = []
        
        for tpa in extracted_tpas:
            tpa_upper = tpa.strip().upper()
            if tpa_upper in company_mappings:
                # Replace the extracted value with mapped DB values
                mapped_values = company_mappings[tpa_upper]
                mapped_tpas.extend(mapped_values)
                logger.info(f"Applied mapping for '{company}': '{tpa}' -> {mapped_values}")
            else:
                # Keep the original value if no mapping exists
                mapped_tpas.append(tpa)
        
        return mapped_tpas

    def get_extracted_tpa_dropdown(self, df, company, region):
        logger.debug(f"Extracting TPA dropdown options for Company: '{company}', Region: '{region}'")
        
        extracted_tpas = []
        
        # For DUBAI INSURANCE CO, we need to handle the combined TPA values differently
        if company == 'DUBAI INSURANCE CO':
            # After processing, Dubai Insurance records should have combined TPA values in the TPA field
            # We only want the combined values (those with " - " in them), not the original individual ones
            dubai_data_records = df[
                (df['Company'] == company) &
                (df['Region'] == region) &
                (df['Dropdown_Name'] != 'TPA 1') &
                (df['Dropdown_Name'] != 'TPA 2') &
                (df['Dropdown_Name'] != 'TPA Combined') &
                (df['TPA'].notna()) &
                (df['TPA'] != '') &
                (df['TPA'].astype(str).str.strip() != '')
            ]
            
            if not dubai_data_records.empty:
                # Extract unique TPA values from the processed data records
                unique_tpas = dubai_data_records['TPA'].unique()
                for tpa in unique_tpas:
                    tpa_str = str(tpa).strip()
                    # Only include combined TPA values (those containing " - ") for Dubai Insurance
                    if (tpa_str and 
                        not self._should_exclude_value(tpa_str, company=company) and
                        ' - ' in tpa_str):  # Only combined format TPAs
                        extracted_tpas.append(tpa_str)
                
                logger.debug(f"Extracted Dubai Insurance combined TPAs: {extracted_tpas}")
                
                # If we didn't find any combined TPAs, log a warning
                if not extracted_tpas:
                    all_tpas = [str(tpa).strip() for tpa in unique_tpas if str(tpa).strip()]
                    logger.warning(f"No combined TPAs found for Dubai Insurance. All TPAs found: {all_tpas}")
            else:
                # Fallback: check for TPA 1 and TPA 2 dropdown fields (if processing hasn't happened yet)
                logger.debug(f"No processed TPA records found, falling back to TPA 1 and TPA 2 fields")
                tpa_rows = df[
                    (df['Company'] == company) &
                    (df['Region'] == region) &
                    (df['Dropdown_Name'].isin(['TPA 1', 'TPA 2']))
                ]
                
                for v in tpa_rows['Selection_Value']:
                    if isinstance(v, list):
                        valid_values = [
                            x.strip() for x in v 
                            if x and not self._should_exclude_value(x, company=company)
                        ]
                        extracted_tpas.extend(valid_values)
                    elif v and isinstance(v, str):
                        if not self._should_exclude_value(v, company=company):
                            extracted_tpas.append(v.strip())
        else:
            # Find the TPA dropdown row(s) for other companies
            tpa_rows = df[
                (df['Company'] == company) &
                (df['Region'] == region) &
                (df['Dropdown_Name'] == 'TPA')
            ]
            
            count = 0
            for v in tpa_rows['Selection_Value']:
                count += 1
                if isinstance(v, list):
                    logger.debug(f"  Found list for Selection_Value in row {count}: {v}")
                    # Filter out excluded values from list
                    valid_values = [
                        x.strip() for x in v 
                        if x and not self._should_exclude_value(x, company=company)
                    ]
                    extracted_tpas.extend(valid_values)
                    
                elif v and isinstance(v, str):
                    logger.debug(f"  Found string for Selection_Value in row {count}: '{v}'")
                    # Check if single string value should be excluded
                    if not self._should_exclude_value(v, company=company):
                        extracted_tpas.append(v.strip())
                    else:
                        logger.debug(f"  Excluded placeholder value: '{v}'")
        
        # Apply company-specific TPA mappings
        extracted_tpas = self._apply_company_tpa_mapping(extracted_tpas, company)
        
        # Fidelity United special logic: combine Group and TPA values from extracted data
        if company.strip().lower() == "fidelity united":
            # Get Group values from extracted data for this company/region
            group_rows = df[
                (df['Company'] == company) &
                (df['Region'] == region) &
                (df['Dropdown_Name'].str.lower() == 'group')
            ]
            group_values = []
            for v in group_rows['Selection_Value']:
                if isinstance(v, list):
                    group_values.extend([x.strip() for x in v if x and not str(x).lower().startswith("select")])
                elif v and isinstance(v, str) and not v.lower().startswith("select"):
                    group_values.append(v.strip())
            # Only use the combinations, do NOT add original TPA values
            unique_tpas = sorted(set(combine_fidelity_tpa_group_from_extracted(group_values, extracted_tpas)))
        else:
            unique_tpas = sorted(set(extracted_tpas))

        logger.info(f"Extracted TPA dropdowns for Company: '{company}', Region: '{region}': {unique_tpas}")
        return unique_tpas

        logger.info(f"Extracted TPA dropdowns for Company: '{company}', Region: '{region}': {unique_tpas}")
        return unique_tpas

    def fetch_db_tpas(self, company, region):
        if self.df_tpa_dropdowns is not None:
            filtered = self.df_tpa_dropdowns[
                (self.df_tpa_dropdowns['Company'] == company) &
                (self.df_tpa_dropdowns['Region'] == region)
            ]
            db_tpas = sorted(set(filtered['TPA'].dropna().astype(str).str.strip()))
            logger.info(f"DB TPAs for Company: '{company}', Region: '{region}': {db_tpas}")
            return db_tpas
        
    def compare_tpa_values(self, df_extracted: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting TPA Dropdown comparison (pre-mapping)...")
        results = []
        pairs = df_extracted[['Company', 'Region']].drop_duplicates()
        logger.info(f"Found {len(pairs)} unique (Company, Region) pairs in extracted data")
        
        for idx, row in pairs.iterrows():
            company = row['Company']
            region = row['Region']
            logger.debug(f"Comparing TPA dropdowns for Company: '{company}', Region: '{region}'")
            
            extracted_tpas = self.get_extracted_tpa_dropdown(df_extracted, company, region)
            db_tpas = self.fetch_db_tpas(company, region)

            # Skip if there are no extracted values for this company/region
            if not extracted_tpas:
                continue     
                   
            only_in_extracted = sorted(set(extracted_tpas) - set(db_tpas))
            only_in_db = sorted(set(db_tpas) - set(extracted_tpas))
            # common = sorted(set(extracted_tpas) & set(db_tpas))  # Not needed
            
            # Only add to results if there is a mismatch
            if only_in_extracted or only_in_db:
                results.append({
                    "Company": company,
                    "Region": region,
                    "TPA_Extracted_Values": ', '.join(extracted_tpas),
                    "TPA_Database_Values": ', '.join(db_tpas),
                    "Values_Mismatch": ", ".join(only_in_extracted + only_in_db)
                })
        
        logger.info(f"TPA Dropdown comparison completed. Total results: {len(results)}")
        return pd.DataFrame(results)