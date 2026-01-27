from datetime import datetime
from pathlib import Path
from src.services.value_comparison_service.value_comparator import ValueComparator
from src.services.value_comparison_service.value_comparison_db import DataComparisonDBService
from src.utils.logger import logger

def main():
    """Main execution function - Single processing, broker-aware comparison"""
    
    # Determine extracted data file path
    today_str = datetime.now().strftime('%Y%m%d')
    extracted_file = Path(f'c:/Users/AkalankaDias/OneDrive - Algospring (PVT) LTD/Documents/Insurance_Playwright_Compare/extracted_data/extracted_data_{today_str}.txt')
    
    if not extracted_file.exists():
        logger.error(f"Extracted data file not found: {extracted_file}")
        return
    
    # # ✅ Add verification step
    # logger.info("🔍 Verifying broker data distribution...")
    # with DataComparisonDBService() as db_service:
    #     db_service.verify_broker_data(
    #         company="Dubai National Insurance And Reinsurance Co",
    #         tpa="MEDNET UAE", 
    #         network="SME Plan- Gold",
    #         dropdown_name="Dental(Co)"
    #     )
    
    # logger.info(f"\n{'='*60}")
    # logger.info(f"🏢 PROCESSING ALL BROKERS - BROKER-AWARE MODE")
    # logger.info(f"Current Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # logger.info(f"{'='*60}")
    
    try:
        # Initialize comparator (broker_id doesn't matter for data processing)
        comparator = ValueComparator(broker_id=0)
        
        # Run comparison with broker-aware data loading
        rpa_filename, db_update_filename = comparator.run_comparison(extracted_file)
        
        # Report results
        print(f"\n{'='*60}")
        print(f"📊 FINAL SUMMARY - BROKER-AWARE COMPARISON")
        print(f"{'='*60}")
        
        if rpa_filename:
            print(f"✅ RPA Results: {Path(rpa_filename).name}")
            logger.info(f"RPA Excel file created: {rpa_filename}")
        
        if db_update_filename:
            print(f"✅ DB Update Results: {Path(db_update_filename).name}")
            logger.info(f"DB Update Excel file created: {db_update_filename}")
        
        print(f"\n📈 RESULTS:")
        print(f"   ✅ Total files created: 2")
        print(f"   📊 Processing: Broker-aware comparison")
        print(f"   📋 Export: Broker-specific filtering applied")
        
        if rpa_filename and db_update_filename:
            logger.info("🎉 Broker-aware process completed successfully")
        else:
            logger.error("💥 Process failed")
            
    except Exception as e:
        logger.error(f"❌ Error in processing: {e}")
        return
    
    logger.info("Data comparison tool finished - Broker-aware mode")
    logger.info(f"{'='*60}\n")

if __name__ == '__main__':
    main()