"""
Qatar API Extractor
Orchestrates extraction of all benefit dropdowns using API calls.
Updated to follow Orient Aura pattern with dynamic API calls.

Flow:
Pre-Level: Industry Categories (Business Nature)
Level 0: Groups (hardcoded to SME NAS)
Level 1: Emirates (per group, filtered to Dubai)
Level 2: TPAs (per emirate)
Level 3: Plans (per TPA)
Level 4: Benefits (per plan)
"""

import json
import os
from datetime import datetime
from src.utils.logger import qatar_logger
from .mapping import QATAR_MAPPING, PORTAL_REGION
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
        self.results = None
    
    async def extract_all_benefits(self) -> dict:
        """
        Extract all benefits for SME NAS group, Dubai region.
        Follows Orient Aura pattern: Groups → Emirates → TPAs → Plans → Benefits
        
        Returns:
            dict: Complete extraction results
        """
        qatar_logger.info("="*60)
        qatar_logger.info("🚀 QATAR API EXTRACTION STARTED")
        qatar_logger.info("="*60)
        
        self.results = {
            "portal": QATAR_MAPPING["portal_name"],
            "extracted_at": datetime.now().isoformat(),
            "industry_categories": [],
            "groups": {}
        }
        
        async with QatarAPIClient(self.auth) as client:
            # Pre-Level: Extract Industry Categories
            print("\n📥 Pre-Level: Extracting Industry Categories (Business Nature)...")
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
            
            # Level 0: Get groups from API and find matching group by name
            target_group_name = QATAR_MAPPING["group"]["group_name"]  # "SME NAS"
            print(f"\n📥 Level 0: Fetching groups from API, looking for: {target_group_name}")
            qatar_logger.info(f"Fetching groups from API, target: {target_group_name}")
            
            all_groups = await client.get_groups(version_id=QATAR_MAPPING["version_id"])
            qatar_logger.info(f"Found {len(all_groups)} groups from API")
            
            # Find the matching group by name
            matching_group = None
            for g in all_groups:
                if g.get("group_name", "").strip() == target_group_name:
                    matching_group = g
                    break
            
            if not matching_group:
                qatar_logger.error(f"Group '{target_group_name}' not found in API response!")
                print(f"   ❌ Group '{target_group_name}' not found!")
                print(f"   Available groups: {[g.get('group_name') for g in all_groups]}")
                return self.results
            
            # Use group_id from API response (not hardcoded)
            group_name = matching_group.get("group_name", "")
            group_id = matching_group.get("group_id")
            reinsurer_company_id = matching_group.get("reinsurer_company_id")
            
            print(f"   ✓ Found Group: {group_name} (ID: {group_id}) from API")
            qatar_logger.info(f"Using Group from API: {group_name} (ID: {group_id})")
            
            # Process the matched group
            print(f"\n🏢 Processing Group: {group_name} (ID: {group_id})")
            qatar_logger.info(f"Processing Group: {group_name}")
            
            group_results = await self._extract_group_data(
                client, group_name, group_id, reinsurer_company_id
            )
            self.results["groups"][group_name] = group_results
        
        return self.results
    
    async def _extract_group_data(self, client, group_name, group_id, reinsurer_company_id):
        """
        Extract data for a single group.
        
        Args:
            client: QatarAPIClient instance
            group_name: Name of the group
            group_id: Group ID
            reinsurer_company_id: Reinsurer company ID
            
        Returns:
            dict: Group extraction results
        """
        group_results = {
            "group_id": group_id,
            "reinsurer_company_id": reinsurer_company_id,
            "emirates": {}
        }
        
        # Fetch emirates for this group
        emirates_list = await client.get_emirates(group_id)
        
        if not emirates_list:
            qatar_logger.warning(f"No emirates found for group {group_name}")
            print(f"   ⚠️ No emirates found")
            return group_results
        
        # Filter to Dubai only
        dubai_emirate = None
        for emirate in emirates_list:
            if emirate.get("emirates", "").strip().lower() == "dubai":
                dubai_emirate = emirate
                break
        
        if not dubai_emirate:
            qatar_logger.warning(f"Dubai emirate not found for group {group_name}")
            print(f"   ⚠️ Dubai emirate not found")
            return group_results
        
        print(f"   📍 Processing: Dubai only")
        qatar_logger.info(f"Processing Dubai emirate only")
        
        # Process Dubai emirate only
        emirate_name = dubai_emirate.get("emirates")
        emirate_results = await self._extract_emirate_data(client, emirate_name, dubai_emirate)
        group_results["emirates"][emirate_name] = emirate_results
        
        return group_results
    
    async def _extract_emirate_data(self, client, emirate_name, emirate_data):
        """
        Extract data for a single emirate.
        
        Args:
            client: QatarAPIClient instance
            emirate_name: Name of the emirate
            emirate_data: Emirate data from API
            
        Returns:
            dict: Emirate extraction results
        """
        emirate_results = {
            "emirates_master_id": emirate_data.get("emirates_master_id"),
            "tpas": {}
        }
        
        emirates_id = emirate_data.get("emirates_master_id", "")
        
        # Fetch TPAs for this emirate
        tpas = await client.get_tpas(emirates_id)
        
        if not tpas:
            qatar_logger.warning(f"No TPAs found for {emirate_name}")
            print(f"      ⚠️ No TPAs found")
            return emirate_results
        
        for tpa in tpas:
            tpa_name = tpa.get("tpa_name", "Unknown")
            tpa_id = tpa.get("tpa_id", "")
            reinsurer_company_id = int(str(tpa.get("reinsurer_company_id", "7")).split(",")[0])
            
            print(f"      🏥 Processing TPA: {tpa_name}")
            qatar_logger.info(f"Processing TPA: {tpa_name}")
            
            tpa_results = await self._extract_tpa_data(
                client, tpa_name, tpa_id, reinsurer_company_id
            )
            emirate_results["tpas"][tpa_name] = tpa_results
        
        return emirate_results
    
    async def _extract_tpa_data(self, client, tpa_name, tpa_id, reinsurer_company_id):
        """
        Extract data for a single TPA.
        
        Args:
            client: QatarAPIClient instance
            tpa_name: Name of the TPA
            tpa_id: TPA ID
            reinsurer_company_id: Reinsurer company ID
            
        Returns:
            dict: TPA extraction results
        """
        tpa_results = {
            "tpa_id": tpa_id,
            "reinsurer_company_id": reinsurer_company_id,
            "plans": {}
        }
        
        # Fetch plans for this TPA
        plans = await client.get_plans(tpa_id)
        
        if not plans:
            qatar_logger.warning(f"No plans found for TPA {tpa_name}")
            print(f"         ⚠️ No plans found")
            return tpa_results
        
        print(f"         📋 Found {len(plans)} plans")
        
        for plan in plans:
            plan_name = plan.get("plans", plan.get("reinsurer_plan_name", "Unknown"))
            plan_id = plan.get("plan_id")
            reinsurer_plan_id = plan.get("reinsurer_plan_id")
            plan_reinsurer_id = plan.get("reinsurer_company_id", reinsurer_company_id)
            
            print(f"            📄 Extracting benefits for plan: {plan_name}")
            qatar_logger.debug(f"Extracting plan: {plan_name} (ID: {plan_id})")
            
            # Fetch benefits for this plan
            benefits = await client.get_benefits(plan_id, plan_reinsurer_id)
            
            tpa_results["plans"][plan_name] = {
                "plan_id": plan_id,
                "reinsurer_plan_id": reinsurer_plan_id,
                "reinsurer_company_id": plan_reinsurer_id,
                "benefits": benefits
            }
        
        return tpa_results
    
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
        
        # Count from results
        group_count = len(self.results.get("groups", {}))
        emirate_count = 0
        tpa_count = 0
        plan_count = 0
        benefit_count = 0
        
        for group_data in self.results.get("groups", {}).values():
            for emirate_data in group_data.get("emirates", {}).values():
                emirate_count += 1
                for tpa_data in emirate_data.get("tpas", {}).values():
                    tpa_count += 1
                    for plan_data in tpa_data.get("plans", {}).values():
                        plan_count += 1
                        benefit_count += len(plan_data.get("benefits", {}))
        
        print(f"   Groups processed: {group_count}")
        print(f"   Emirates processed: {emirate_count}")
        print(f"   TPAs processed: {tpa_count}")
        print(f"   Plans extracted: {plan_count}")
        print(f"   Benefit fields: {benefit_count}")
