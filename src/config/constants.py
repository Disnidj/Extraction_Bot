"""Application constants"""

# Target portals for comparison
TARGET_PORTALS = [
    'ADNIC', 
    'Al Ittihad Al Watani', 
    'AL SAGR INSURANCE COMPANY', 
    'Daman Insurance', 
    # 'Dubai National Insurance And Reinsurance Co', 
    'DUBAI INSURANCE CO', 
    'Fidelity United', 
    'GIG Insurance', 
    'ISON', 
    'MaxHealth', 
    'Medgulf', 
    'NLGIC', 
    'ORIENT INSURANCE PJSC', 
    'QATAR INSURANCE CO', 
    'RAK INSURANCE', 
    'SUKOON INSURANCE',  # Keep extracted data case for filtering
    'TAKAFUL EMARAT', 
    'Watania Takaful'
]

BROKER_PORTALS = {
    "Broker 1": [
        "ADNIC",
        "Al Ittihad Al Watani",
        "AL SAGR INSURANCE COMPANY",
        "Daman Insurance",
        "DUBAI INSURANCE CO",
        "GIG Insurance",
        "Medgulf",
        "NLGIC",
        "SUKOON INSURANCE",
        "TAKAFUL EMARAT",
    ],
    "Broker 2": [
        "ADNIC",
        "AL SAGR INSURANCE COMPANY",
        "DUBAI INSURANCE CO",
        # "Dubai National Insurance And Reinsurance Co",
        "GIG Insurance",
        "NLGIC",
        "ORIENT INSURANCE PJSC",
        "SUKOON INSURANCE",
        "TAKAFUL EMARAT"
    ],
    "Broker 3": [
        "ADNIC",
        "Al Ittihad Al Watani",
        "Daman Insurance",
        "DUBAI INSURANCE CO",
        # "Dubai National Insurance And Reinsurance Co",
        "Fidelity United",
        "GIG Insurance",
        "ISON",
        "MaxHealth",
        "Medgulf", #
        "NLGIC", #
        "ORIENT INSURANCE PJSC",   #
        "QATAR INSURANCE CO",
        "RAK INSURANCE", #
        "SUKOON INSURANCE",
        "TAKAFUL EMARAT",
        "Watania Takaful"
    ],
    "Broker 4": [],
    "Broker 6": [
        "AL SAGR INSURANCE COMPANY",
        "DUBAI INSURANCE CO",
        "NLGIC",
        "SUKOON INSURANCE",
        "TAKAFUL EMARAT",
        "GIG Insurance"

    ]
}


# Column mappings
COLUMN_MAPPINGS = {
    'Portal': 'Company',
    'field name': 'Dropdown_Name',
    'values': 'Selection_Value',
    'Outpatient Plan': 'Outpatient_Plan',
    'Additional Benefits Plan': 'Additionaly_Benefits_Plan'
}

# Required columns for processing
REQUIRED_COLUMNS = ['Company', 'TPA', 'Region', 'Network', 'Dropdown_Name', 'Selection_Value']

# String columns for cleaning
STRING_COLUMNS = ['Company', 'TPA', 'Region', 'Network', 'Dropdown_Name', 'Selection_Value']

# Fields to exclude from processing
EXCLUDED_FIELDS = ['region', 'network', 'tpa', 'tpa (network provider)', 'network type', 'network part 1', 'network part 2', 'salary band', 'location', 'policy holder type', 'quotation for', 'group']

# Select value patterns to filter out
SELECT_PATTERNS = [
    r'.*select.*',
    r'.*choose.*',
    r'.*pick.*',
    r'.*loading.*' 
]

# Export column mappings
EXPORT_COLUMN_MAPPINGS = {
    'standard': [
        'Company', 'TPA', 'Network', 'Region',
        'Extracted_Field_Name',      
        'DB_Field_Name',             
        'Mismatch_Type',
        'All_Values_Extracted', 'All_Values_Database',
        'Only_in_Extracted', 'Only_in_Database', 'Common_Values'
    ],
    'enhanced_value_mismatch': [
        'Company', 'TPA', 'Network', 'Region',
        'Extracted_Field_Name',           
        'DB_Field_Name',                    
        'Mismatch_Type',
        'All_Values_in_Extraction',
        'All_Values_in_Database',
        'Values_MISSING_from_Database',   
        'Values_EXTRA_in_Database',       
        'Values_MATCHING_Both_Sources'
    ]
}



EXCLUDED_COMPANIES = [
    'SUKOON INSURANCE',
    'Orient Insurance PJSC',
    'Dubai National Insurance And Reinsurance Co'
]


IQ_COMPANIES = [
    'Orient Insurance PJSC',
    'Dubai National Insurance And Reinsurance Co'
]