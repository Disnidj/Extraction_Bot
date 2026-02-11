"""
Qatar API Extractor
Orchestrates extraction of all benefit dropdowns using API calls.
"""

import json
import os
from datetime import datetime
from src.utils.logger import qatar_logger
from .mapping import QATAR_MAPPING
from .client import QatarAPIClient


class QatarAPIExtractor:
    """Extracts all benefit dropdowns from Qatar Insurance portal via API."""
    
    def __init__(self, auth):
        """
        Initialize extractor.
        
        Args:
            auth: QatarAuthToken instance with valid token
        """
        self.auth = auth
        self.results = {
            "portal": QATAR_MAPPING["portal_name"],
            "group_id": QATAR_MAPPING["group_id"],
            "extracted_at": datetime.now().isoformat(),
            "industry_categories": [],
            "emirates": {}
        }
        self.stats = {
            "emirates": 0,
            "tpas": 0,
            "plans": 0,
            "benefits": 0
        }
    
    async def extract_all_benefits(self) -> dict:
        """
        Extract all benefits for Dubai + NAS TPA configuration.
        Also extracts Industry Categories (Business Nature) as Pre-Level.
        
        Returns:
            dict: Complete extraction results
        """
        qatar_logger.info("="*60)
        qatar_logger.info("🚀 QATAR API EXTRACTION STARTED")
        qatar_logger.info("="*60)
        
        async with QatarAPIClient(self.auth) as client:
            # Pre-Level: Extract Industry Categories
            print("\n📥 Pre-Level: Extracting Industry Categories...")
            qatar_logger.info("Pre-Level: Extracting Industry Categories")
            industries = await client.get_industries()
            if industries:
                industry_names = [ind["industry_name"] for ind in industries]
                self.results["industry_categories"] = industry_names
                qatar_logger.info(f"Industry Categories: {len(industry_names)} options extracted")
                print(f"   ✓ Industry Categories: {len(industry_names)} options")
            else:
                qatar_logger.warning("No Industry Categories found")
                print("   ⚠️ No Industry Categories found")
            
            # Iterate through hardcoded mapping (Dubai only, NAS only)
            for emirate_name, emirate_config in QATAR_MAPPING["emirates"].items():
                print(f"\n📍 Processing emirate: {emirate_name}")
                qatar_logger.info(f"Processing emirate: {emirate_name}")
                
                self.results["emirates"][emirate_name] = {
                    "emirates_id": emirate_config["emirates_id"],
                    "tpas": {}
                }
                self.stats["emirates"] += 1
                
                # Process each TPA (only NAS)
                for tpa_name, tpa_config in emirate_config["tpas"].items():
                    print(f"   🏥 Processing TPA: {tpa_name}")
                    qatar_logger.info(f"Processing TPA: {tpa_name}")
                    
                    tpa_id = tpa_config["tpa_id"]
                    reinsurer_company_id = tpa_config["reinsurer_company_id"]
                    
                    self.results["emirates"][emirate_name]["tpas"][tpa_name] = {
                        "tpa_id": tpa_id,
                        "reinsurer_company_id": reinsurer_company_id,
                        "plans": {}
                    }
                    self.stats["tpas"] += 1
                    
                    # Fetch plans for this TPA
                    plans = await client.get_plans(tpa_id)
                    print(f"      📋 Found {len(plans)} plans")
                    
                    for plan in plans:
                        plan_name = plan.get("plans", plan.get("reinsurer_plan_name", "Unknown"))
                        plan_id = plan.get("plan_id")
                        reinsurer_plan_id = plan.get("reinsurer_plan_id")
                        
                        print(f"         📄 Extracting benefits for plan: {plan_name}")
                        qatar_logger.debug(f"Extracting plan: {plan_name} (ID: {plan_id})")
                        
                        # Fetch benefits for this plan
                        benefits = await client.get_benefits(plan_id, reinsurer_company_id)
                        
                        self.results["emirates"][emirate_name]["tpas"][tpa_name]["plans"][plan_name] = {
                            "plan_id": plan_id,
                            "reinsurer_plan_id": reinsurer_plan_id,
                            "reinsurer_company_id": reinsurer_company_id,
                            "benefits": benefits
                        }
                        self.stats["plans"] += 1
                        
                        # Count benefit fields
                        if isinstance(benefits, dict):
                            self.stats["benefits"] += len(benefits)
        
        return self.results
    
    def save_results(self, output_dir: str = "extracted_data") -> str:
        """
        Save extraction results to JSON file.
        
        Args:
            output_dir: Base directory to save file
            
        Returns:
            str: Path to saved file
        """
        # Save to portal-specific subfolder
        portal_dir = os.path.join(output_dir, "qatar")
        os.makedirs(portal_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"qatar_benefits_{timestamp}.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 JSON results saved to {output_file}")
        qatar_logger.info(f"Results saved to {output_file}")
        return output_file
    
    def print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"   Emirates processed: {self.stats['emirates']}")
        print(f"   TPAs processed: {self.stats['tpas']}")
        print(f"   Plans extracted: {self.stats['plans']}")
        print(f"   Benefit fields: {self.stats['benefits']}")
