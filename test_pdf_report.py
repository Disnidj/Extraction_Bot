"""Test script to verify PDF report generation with new styling"""
import os
from datetime import datetime, timedelta
from src.services.extraction_report.report_generator import generate_extraction_report
from src.services.db_service.api_data.staging_models import ChangeReport, ChangeRecord

# Test data
run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
start_time = datetime.now() - timedelta(minutes=5)
end_time = datetime.now()

# Mock portal timings
portal_timings = {
    'Orient Aura': {
        'start': start_time,
        'end': start_time + timedelta(seconds=45),
        'duration': timedelta(seconds=45)
    },
    'ADNIC': {
        'start': start_time + timedelta(seconds=50),
        'end': start_time + timedelta(seconds=90),
        'duration': timedelta(seconds=40)
    },
    'SUKOON INSURANCE': {
        'start': start_time + timedelta(seconds=95),
        'end': start_time + timedelta(seconds=150),
        'duration': timedelta(seconds=55)
    }
}

# Mock portal results
portal_results = {
    'Orient Aura': {'success': True, 'attempts': 1},
    'ADNIC': {'success': True, 'attempts': 1},
    'SUKOON INSURANCE': {'success': True, 'attempts': 1}
}

# Mock mapping details with inserted dropdown names
mapping_details = {
    'only_mapped_mode': True,
    'applied_mappings': {
        'Orient Aura': {
            'Business Nature': 'Business_Nature',
            'Territory': 'Terotory',
            'Annual Limit': 'Annual'
        },
        'ADNIC': {
            'Business Nature': 'Business_Nature',
            'Annual Limit': 'Annual',
            'Deductible': 'Deductable',
            'CoPayment': 'CoPayment'
        }
    },
    'unmapped_names': {
        'Orient Aura': ['Unknown_Field_1', 'Legacy_Dropdown'],
        'ADNIC': []
    },
    'inserted_dropdown_names': {
        'Orient Aura': ['Business_Nature', 'Terotory', 'Annual', 'Gender', 'MaritalStatus', 'MaternityCover', 'Room_Type', 'Visa_Type', 'City', 'Region'],
        'ADNIC': ['Business_Nature', 'Annual', 'Deductable', 'CoPayment', 'Psycharaty', 'Alternativemedecine', 'DentalNetwork', 'OpticalNetwork'],
        'SUKOON INSURANCE': ['Business_Nature', 'Network', 'Plan_Type', 'Coverage_Type', 'TPA']
    }
}

# Create sample ChangeReport with actual changes
change_report = ChangeReport(
    run_id=run_timestamp,
    companies_processed=['Orient Aura', 'ADNIC', 'SUKOON INSURANCE'],
    unchanged_count=11781,
    staging_count=11829,
    backup_count=28936,
    old_backups_removed=1250,
    staging_cleared=10500,
    audit_records_logged=51,
    full_backup_file='database/backups/Medical_CTN_Cascading_Dropdown_Lifecare_backup_20260224_144553.sql',
    backup_table='Medical_CTN_Cascading_Dropdown_Backup',
    staging_table='Medical_CTN_Cascading_Dropdown_Staging',
    original_table='Medical_CTN_Cascading_Dropdown_Lifecare',
    audit_table='Medical_CTN_Cascading_Dropdown_Audit'
)

# Add sample NEW records (48 new for Orient Aura Business_Nature)
new_values = ['Educational Institutes', 'Medical Providers', 'Other Industries']
tpa_networks = [
    ('Nextcare Sme - Nextcare', 'Plan1 GN'),
    ('Nextcare Sme - Nextcare', 'Plan2 GN'),
    ('Nextcare Sme - Nextcare', 'Plan3 RN'),
    ('Nextcare Sme - Nextcare', 'Plan1 GN+ (Ip)'),
    ('NAS - Almadallah', 'Essential Network'),
    ('NAS - Almadallah', 'Enhanced Network'),
    ('NAS - Almadallah', 'Premium Network'),
    ('NAS - Almadallah', 'Basic Network'),
    ('Mednet Premium', 'Gold Plan'),
    ('Mednet Premium', 'Silver Plan'),
    ('Mednet Premium', 'Bronze Plan'),
    ('Mednet Premium', 'Platinum Plan'),
    ('Harmony TPA', 'Standard Network'),
    ('Harmony TPA', 'Extended Network'),
    ('Harmony TPA', 'Full Coverage'),
    ('Harmony TPA', 'Basic Coverage'),
]

for tpa, network in tpa_networks:
    for value in new_values:
        change_report.new_records.append(ChangeRecord(
            change_type='INSERT',
            broker_id=3,
            company='Orient Aura',
            tpa=tpa,
            network=network,
            region='UAE',
            dropdown_name='Business_Nature',
            new_value=value,
            difference_type='VALUE_CHANGE'
        ))

# Add sample DELETED records (3 deleted)
deleted_combos = [
    ('Old TPA - Deprecated', 'Legacy Network', 'Educational Institutes'),
    ('Old TPA - Deprecated', 'Legacy Network', 'Medical Providers'),
    ('Old TPA - Deprecated', 'Legacy Network', 'Other Industries'),
]
for tpa, network, value in deleted_combos:
    change_report.deleted_records.append(ChangeRecord(
        change_type='DELETE',
        broker_id=3,
        company='Orient Aura',
        tpa=tpa,
        network=network,
        region='UAE',
        dropdown_name='Business_Nature',
        old_value=value,
        difference_type='VALUE_CHANGE'
    ))

# Add sample MODIFIED record for ADNIC
change_report.modified_records.append(ChangeRecord(
    change_type='UPDATE',
    broker_id=3,
    company='ADNIC',
    tpa='Nextcare',
    network='Premium Plan',
    region='Dubai',
    dropdown_name='Business_Nature',
    old_value='Social Workssss',
    new_value='Social Work',
    difference_type='VALUE_CHANGE'
))

# Generate test PDF
print("=" * 60)
print("Testing PDF Report Generation with Enhanced Staging Details")
print("=" * 60)

try:
    pdf_path = generate_extraction_report(
        run_timestamp=run_timestamp,
        overall_start_time=start_time,
        overall_end_time=end_time,
        portal_timings=portal_timings,
        portal_results=portal_results,
        db_upload_success=True,
        db_rows_inserted=11829,
        db_upload_duration=2.5,
        db_upload_start=end_time - timedelta(seconds=3),
        db_upload_end=end_time,
        total_duration=(end_time - start_time).total_seconds(),
        output_folder='extracted_data/' + run_timestamp,
        portals_processed=['Orient Aura', 'ADNIC', 'SUKOON INSURANCE'],
        deletion_details=None,
        mapping_details=mapping_details,
        change_report=change_report
    )
    
    print(f"\n✅ PDF generated successfully!")
    print(f"📄 Location: {pdf_path}")
    print(f"\nEnhanced sections to verify:")
    print("  - Staging Comparison Results (48 new, 1 modified, 3 deleted)")
    print("  - Detailed Dropdown Changes (ALL values shown, not samples)")
    print("  - Dropdown Names Inserted to Staging (per company)")
    print("  - Database Operations Summary")
    
    # Open the PDF
    os.startfile(pdf_path)
    
except Exception as e:
    print(f"\n❌ Error generating PDF: {e}")
    import traceback
    traceback.print_exc()
