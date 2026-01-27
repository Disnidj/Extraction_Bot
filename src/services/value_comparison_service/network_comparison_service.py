import pandas as pd
from src.utils.logger import logger
import re

def combine_fidelity_tpa_group_from_extracted(group_values, tpa_values):
    """
    For Fidelity United, combine each group value with each TPA value from extracted data.
    Returns a list of combined strings: "<group> - <tpa>"
    """
    combined = []
    for group in group_values:
        group = str(group)
        if not group or group.lower().startswith("select"):
            continue
        for tpa in tpa_values:
            tpa = str(tpa)
            if not tpa or tpa.lower().startswith("select"):
                continue
            combined.append(f"{group} - {tpa}")
    return combined

class NetworkComparisonService:
    def __init__(self, db_service):
        self.db_service = db_service
        self.excluded_values = {
            'select network',
            'select plans',
            'please select',
            'select',
            'choose network',
            'pick network',
            'select an option',
            'network type',
            'select network type',
            'select option',
            'select primary benefits',
            'default',
            'none',
            'n/a',
            'na'
        }
        self.placeholder_patterns = [
            r'^select\s*(network|plan|option|an\s*option)?$',
            r'^please\s*select',
            r'^choose\s*(network|plan|option)',
            r'^pick\s*(network|plan|option)',
            r'^\-+\s*select\s*\-+$',
            r'^\-+\s*please\s*select\s*\-+$'
        ]

    def _should_exclude_value(self, value):
        if not value or not isinstance(value, str):
            return True
        cleaned_value = value.lower()
        if not cleaned_value:
            return True
        if cleaned_value in self.excluded_values:
            return True
        for pattern in self.placeholder_patterns:
            if re.match(pattern, cleaned_value):
                return True
        return False

    def get_extracted_network_dropdown(self, df, company, region, tpa, field_names=('Network', 'Plan')):
        logger.debug(f"Extracting Network/Plan dropdown options for Company: '{company}', Region: '{region}', TPA: '{tpa}'")
        
        # Fidelity United special logic: compare only the combination of group + tpa
        if company and str(company).strip().lower() == "fidelity united":
            group_rows = df[
                (df['Company'] == company) &
                (df['Region'] == region) &
                (df['Dropdown_Name'].str.lower() == 'group')
            ]
            group_values = []
            for v in group_rows['Selection_Value']:
                if isinstance(v, list):
                    group_values.extend([x for x in v if x and not str(x).lower().startswith("select")])
                elif v and isinstance(v, str) and not v.lower().startswith("select"):
                    group_values.append(v)
            tpa_rows = df[
                (df['Company'] == company) &
                (df['Region'] == region) &
                (df['Dropdown_Name'].str.lower() == 'tpa')
            ]
            tpa_values = []
            for v in tpa_rows['Selection_Value']:
                if isinstance(v, list):
                    tpa_values.extend([x for x in v if x and not self._should_exclude_value(x)])
                elif v and isinstance(v, str) and not self._should_exclude_value(v):
                    tpa_values.append(v)
            combined = combine_fidelity_tpa_group_from_extracted(group_values, tpa_values)
            logger.info(f"Fidelity United combined group-tpa: {combined}")
            return sorted(set(combined))
        
        # ISON special logic: use only 'Network' as field name
        if company and str(company).strip().lower() == "ison":
            field_names = ('Network',)
            
        # For Dubai Insurance, ensure we're using the combined TPA values correctly
        if company == 'DUBAI INSURANCE CO':
            logger.debug(f"Dubai Insurance: Looking for networks with combined TPA '{tpa}'")
            # Make sure we're using the combined TPA format for filtering
            network_rows = df[
                (df['Company'] == company) &
                (df['Region'] == region) &
                (df['TPA'] == tpa) &  # This should now be the combined TPA value
                (df['Dropdown_Name'].isin(field_names))
            ]
            logger.debug(f"Dubai Insurance: Found {len(network_rows)} network rows for TPA '{tpa}'")
        else:
            # Standard logic for other companies
            network_rows = df[
                (df['Company'] == company) &
                (df['Region'] == region) &
                (df['TPA'] == tpa) &
                (df['Dropdown_Name'].isin(field_names))
            ]
        
        extracted_networks = []
        for v in network_rows['Selection_Value']:
            if isinstance(v, list):
                extracted_networks.extend([x for x in v if x and not self._should_exclude_value(x)])
            elif v and isinstance(v, str) and not self._should_exclude_value(v):
                extracted_networks.append(v)
        logger.info(f"Extracted Network/Plan dropdowns for Company: '{company}', Region: '{region}', TPA: '{tpa}': {extracted_networks}")
        return sorted(set(extracted_networks))

    def fetch_db_networks(self, company, region, tpa):
        if hasattr(self, 'df_network_dropdowns') and self.df_network_dropdowns is not None:
            # For Dubai Insurance, handle both individual and combined TPA formats for database lookup
            db_tpa = tpa
            if company == 'DUBAI INSURANCE CO':
                # If TPA is already in combined format (e.g., "Dubai Care - Dubai Care"), use as is
                if ' - ' in tpa:
                    db_tpa = tpa
                    logger.debug(f"Dubai Insurance: Using combined TPA format '{tpa}' for database lookup")
                # If TPA is individual format, convert to combined format  
                elif tpa in ['Dubai Care', 'Mednet', 'Nas']:
                    db_tpa = f"{tpa} - {tpa}"
                    logger.debug(f"Dubai Insurance: Converting individual TPA '{tpa}' to combined format '{db_tpa}' for database lookup")
                else:
                    # Handle other potential individual TPA values
                    db_tpa = f"{tpa} - {tpa}"
                    logger.debug(f"Dubai Insurance: Converting unknown TPA '{tpa}' to combined format '{db_tpa}' for database lookup")
            
            filtered = self.df_network_dropdowns[
                (self.df_network_dropdowns['Company'] == company) &
                (self.df_network_dropdowns['Region'] == region) &
                (self.df_network_dropdowns['TPA'] == db_tpa)
            ]
            db_networks = sorted(set(filtered['Network'].dropna().astype(str)))
            logger.info(f"DB Networks/Plans for Company: '{company}', Region: '{region}', TPA: '{tpa}' (DB lookup: '{db_tpa}'): {db_networks}")
            return db_networks
        else:
            logger.warning("df_network_dropdowns not loaded; cannot fetch DB networks efficiently.")
            return []

    def compare_network_values(self, df_extracted: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting Network/Plan Dropdown comparison...")
        results = []
        required_cols = ['Company', 'Region', 'TPA']
        for col in required_cols:
            if col not in df_extracted.columns:
                logger.warning(f"Missing required column '{col}' in extracted data, skipping comparison.")
                return pd.DataFrame()
        valid_mask = (
            df_extracted['Company'].notna() & df_extracted['Region'].notna() & df_extracted['TPA'].notna() &
            (df_extracted['Company'].astype(str).str.strip() != '') &
            (df_extracted['Region'].astype(str).str.strip() != '') &
            (df_extracted['TPA'].astype(str).str.strip() != '') &
            (df_extracted['Company'].astype(str).str.lower() != 'nan') &
            (df_extracted['Region'].astype(str).str.lower() != 'nan') &
            (df_extracted['TPA'].astype(str).str.lower() != 'nan')
        )
        filtered_df = df_extracted[valid_mask]
        pairs = filtered_df[['Company', 'Region', 'TPA']].drop_duplicates()
        pairs = pairs.sort_values(by=['Company', 'Region', 'TPA'])
        logger.info(f"Found {len(pairs)} unique (Company, Region, TPA) triplets in extracted data")
        for idx, row in pairs.iterrows():
            company = row['Company']
            region = row['Region']
            tpa = row['TPA']
            extracted_networks = self.get_extracted_network_dropdown(filtered_df, company, region, tpa)
            db_networks = self.fetch_db_networks(company, region, tpa)

            # For WATANIA TAKAFUL, get the Network field value from the extracted data
            network_field_value = ""
            if str(company).strip().lower() == "watania takaful":
                network_rows = filtered_df[
                    (filtered_df['Company'] == company) &
                    (filtered_df['Region'] == region) &
                    (filtered_df['TPA'] == tpa) &
                    (filtered_df['Dropdown_Name'].str.lower() == 'network')
                ]
                network_values = []
                for v in network_rows['Selection_Value']:
                    if isinstance(v, list):
                        network_values.extend([x for x in v if x and not self._should_exclude_value(x)])
                    elif v and isinstance(v, str) and not self._should_exclude_value(v):
                        network_values.append(v)
                network_field_value = network_values[0] if network_values else ""

            extracted_set = set(extracted_networks)
            db_set = set(db_networks)
            common = sorted(extracted_set & db_set)
            only_in_extracted = sorted(extracted_set - db_set)
            only_in_db = sorted(db_set - extracted_set)

            for val in common:
                results.append({
                    "Company": company,
                    "Region": region,
                    "TPA": tpa,
                    "Network_Extracted_Values": val,
                    "Watania_Network_Field_Name": network_field_value if str(company).strip().lower() == "watania takaful" else "",
                    "Network_Database_Values": val
                })
            for val in only_in_extracted:
                results.append({
                    "Company": company,
                    "Region": region,
                    "TPA": tpa,
                    "Network_Extracted_Values": val,
                    "Watania_Network_Field_Name": network_field_value if str(company).strip().lower() == "watania takaful" else "",
                    "Network_Database_Values": ""
                })
            for val in only_in_db:
                results.append({
                    "Company": company,
                    "Region": region,
                    "TPA": tpa,
                    "Network_Extracted_Values": "",
                    "Watania_Network_Field_Name": network_field_value if str(company).strip().lower() == "watania takaful" else "",
                    "Network_Database_Values": val
                })
        logger.info(f"Network/Plan Dropdown comparison completed. Total results: {len(results)}")
        return pd.DataFrame(results)

    def export_to_excel(self, comparison_df, path='Network_Dropdown_Comparison.xlsx'):
        logger.info(f"Exporting Network/Plan Dropdown Comparison to Excel: {path}")
        with pd.ExcelWriter(path) as writer:
            comparison_df.to_excel(writer, sheet_name='Network_Dropdown_Comparison', index=False)
        logger.info(f"Exported Network/Plan Dropdown Comparison to {path}")