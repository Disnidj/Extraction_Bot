"""
Takaful API Extractor
Orchestrates extraction of all dropdown values using API calls.
Updated to follow Orient Aura/Qatar pattern with Groups → Emirates → TPAs → Plans flow.
"""

import asyncio
import json
import os
from datetime import datetime
from src.utils.logger import takaful_logger
from .client import TakafulAPIClient
from .mapping import TAKAFUL_MAPPING


class TakafulAPIExtractor:
    """Extracts all dropdown values via API calls."""
    
    def __init__(self, auth):
        """
        Initialize extractor with auth token.
        
        Args:
            auth: TakafulAuthToken instance with valid token
        """
        self.auth = auth
        self.results = None
        self.errors = []  # Track errors during extraction
    
    async def extract_all_benefits(self):
        """
        Extract all benefit dropdown values.
        Follows hierarchical flow: Groups → Emirates → TPAs → Plans → Benefits.
        Also extracts Industry Categories (Business Nature) as Pre-Level.
        
        Returns:
            dict: Complete extraction results with errors tracked
        """
        takaful_logger.info("="*60)
        takaful_logger.info("🚀 TAKAFUL API EXTRACTION STARTED")
        takaful_logger.info("="*60)
        
        self.errors = []  # Reset errors for new extraction
        self.results = {
            "portal": "TAKAFUL EMARAT",
            "extracted_at": datetime.now().isoformat(),
            "industry_categories": [],
            "groups": {},  # Hierarchical structure matching other portals
            "errors": []  # Will be populated at the end
        }
        
        async with TakafulAPIClient(self.auth) as client:
            # Pre-Level: Extract Industry Categories (Business Nature)
            print("\n📥 Pre-Level: Extracting Industry Categories (Business Nature)...")
            takaful_logger.info("Pre-Level: Extracting Industry Categories (Business Nature)")
            industries = await client.get_industries()
            if industries:
                # Only include industries where allows="true"
                allowed_industries = [
                    ind["industry_name"] 
                    for ind in industries 
                    if ind.get("allows", "").lower() == "true"
                ]
                self.results["industry_categories"] = allowed_industries
                takaful_logger.info(f"Industry Categories: {len(allowed_industries)} options extracted")
                print(f"   ✓ Industry Categories: {len(allowed_industries)} options")
            else:
                takaful_logger.warning("No Industry Categories found")
                print("   ⚠️ No Industry Categories found")
            
            # Level 0: Get groups from API and find matching group by name
            target_group_name = TAKAFUL_MAPPING["group"]["group_name"]  # "SME Medical"
            print(f"\n📥 Level 0: Fetching groups from API, looking for: {target_group_name}")
            takaful_logger.info(f"Fetching groups from API, target: {target_group_name}")
            
            all_groups = await client.get_groups(version_id=TAKAFUL_MAPPING["version_id"])
            takaful_logger.info(f"Found {len(all_groups)} groups from API")
            
            # Check if API returned empty (could be server error)
            if not all_groups:
                error_msg = f"API returned no groups - possible server error or connectivity issue"
                takaful_logger.error(error_msg)
                self.errors.append(error_msg)
                print(f"   ❌ {error_msg}")
                self.results["errors"] = self.errors
                return self.results
            
            # Find the matching group by name
            matching_group = None
            for g in all_groups:
                if g.get("group_name", "").strip() == target_group_name:
                    matching_group = g
                    break
            
            if not matching_group:
                error_msg = f"Group '{target_group_name}' not found in API response!"
                takaful_logger.error(error_msg)
                self.errors.append(error_msg)
                print(f"   ❌ {error_msg}")
                print(f"   Available groups: {[g.get('group_name') for g in all_groups]}")
                self.results["errors"] = self.errors
                return self.results
            
            # Use group_id from API response (not hardcoded)
            group_name = matching_group.get("group_name", "")
            group_id = matching_group.get("group_id")
            reinsurer_company_id = matching_group.get("reinsurer_company_id")
            
            print(f"   ✓ Found Group: {group_name} (ID: {group_id}) from API")
            takaful_logger.info(f"Using Group from API: {group_name} (ID: {group_id})")
            
            # Process the matched group
            print(f"\n🏢 Processing Group: {group_name} (ID: {group_id})")
            takaful_logger.info(f"Processing Group: {group_name}")
            
            group_results = await self._extract_group_data(
                client, group_name, group_id, reinsurer_company_id
            )
            self.results["groups"][group_name] = group_results
        
        # Add any errors to results
        self.results["errors"] = self.errors
        return self.results
    
    async def _extract_group_data(self, client, group_name, group_id, reinsurer_company_id):
        """
        Extract data for a single group.
        
        Args:
            client: TakafulAPIClient instance
            group_name: Name of the group
            group_id: Group ID
            reinsurer_company_id: Reinsurer company ID
            
        Returns:
            dict: Group extraction results with emirates
        """
        group_results = {
            "group_id": group_id,
            "reinsurer_company_id": reinsurer_company_id,
            "emirates": {}
        }
        
        # Fetch emirates for this group
        emirates = await client.get_emirates(group_id)
        takaful_logger.info(f"Found {len(emirates)} emirates for group {group_name}")
        
        # Filter to Dubai only (as per requirements)
        dubai_emirates = [e for e in emirates if e.get("emirates", "").strip() == "Dubai"]
        
        if not dubai_emirates:
            print(f"   ⚠️ No Dubai emirates found, using all emirates")
            dubai_emirates = emirates
        
        for emirate in dubai_emirates:
            emirate_name = emirate.get("emirates", "").strip()
            emirates_id = emirate.get("emirates_master_id", "")
            
            print(f"\n   🌍 Processing Emirate: {emirate_name}")
            takaful_logger.info(f"Processing Emirate: {emirate_name}")
            
            emirate_results = await self._extract_emirate_data(
                client, emirate_name, emirates_id, reinsurer_company_id, group_name
            )
            group_results["emirates"][emirate_name] = emirate_results
        
        return group_results
    
    async def _extract_emirate_data(self, client, emirate_name, emirates_id, 
                                     reinsurer_company_id, group_name):
        """
        Extract data for a single emirate.
        
        Args:
            client: TakafulAPIClient instance
            emirate_name: Name of the emirate
            emirates_id: Emirates ID (comma-separated format)
            reinsurer_company_id: Reinsurer company ID
            group_name: Name of the parent group
            
        Returns:
            dict: Emirate extraction results with TPAs
        """
        emirate_results = {
            "emirates_id": emirates_id,
            "tpas": {}
        }
        
        # Fetch TPAs for this emirate
        tpas = await client.get_tpas(emirates_id)
        takaful_logger.info(f"Found {len(tpas)} TPAs for {emirate_name}")
        
        for tpa in tpas:
            tpa_name = tpa.get("tpa_name", "").strip()
            tpa_id = tpa.get("tpa_id", "")
            
            # Get first reinsurer_company_id from comma-separated list
            tpa_reinsurer = tpa.get("reinsurer_company_id", "")
            if isinstance(tpa_reinsurer, str) and "," in tpa_reinsurer:
                tpa_reinsurer = int(tpa_reinsurer.split(",")[0])
            elif tpa_reinsurer:
                tpa_reinsurer = int(tpa_reinsurer) if isinstance(tpa_reinsurer, str) else tpa_reinsurer
            else:
                tpa_reinsurer = reinsurer_company_id
            
            tpa_results = await self._extract_tpa_data(
                client, tpa_name, tpa_id, tpa_reinsurer, group_name
            )
            
            # Use just TPA name (like Qatar, Orient Aura, NLGI Aura)
            emirate_results["tpas"][tpa_name] = tpa_results
        
        return emirate_results
    
    async def _extract_tpa_data(self, client, tpa_name, tpa_id, 
                                 reinsurer_company_id, group_name):
        """
        Extract data for a single TPA.
        
        Args:
            client: TakafulAPIClient instance
            tpa_name: Name of the TPA
            tpa_id: TPA ID (comma-separated format from API)
            reinsurer_company_id: Reinsurer company ID
            group_name: Name of the parent group
            
        Returns:
            dict: TPA extraction results with plans
        """
        print(f"\n      📍 Processing TPA: {tpa_name}")
        takaful_logger.info(f"Processing TPA: {tpa_name}")
        
        tpa_results = {
            "tpa_id": tpa_id,
            "reinsurer_company_id": reinsurer_company_id,
            "plans": {}
        }
        
        # Fetch plans for this TPA
        plans = await client.get_plans(tpa_id)
        print(f"         Found {len(plans)} plans")
        takaful_logger.info(f"Found {len(plans)} plans for TPA {tpa_name}")
        
        for plan in plans:
            plan_name = plan.get("plans", "").strip()
            plan_id = plan.get("plan_id")
            reinsurer_plan_id = plan.get("reinsurer_plan_id")
            plan_reinsurer = plan.get("reinsurer_company_id", reinsurer_company_id)
            
            print(f"         📋 Fetching benefits for: {plan_name} (ID: {plan_id})")
            
            # Fetch benefits for this plan
            benefits = await client.get_benefits(plan_id, plan_reinsurer)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.3)
            
            tpa_results["plans"][plan_name] = {
                "plan_id": plan_id,
                "reinsurer_plan_id": reinsurer_plan_id,
                "reinsurer_company_id": plan_reinsurer,
                "benefits": benefits
            }
        
        print(f"      ✅ Completed TPA: {tpa_name}")
        return tpa_results
    
    def save_results(self, output_dir="extracted_data"):
        """
        Save extraction results to JSON file.
        
        Args:
            output_dir: Base directory to save results
            
        Returns:
            str: Path to saved file
        """
        if not self.results:
            raise ValueError("No results to save. Run extract_all_benefits first.")
        
        # Save to portal-specific subfolder
        portal_dir = os.path.join(output_dir, "takaful")
        os.makedirs(portal_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"takaful_benefits_{timestamp}.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Results saved to {output_file}")
        takaful_logger.debug(f"Results saved to {output_file}")
        
        return output_file
    
    def print_summary(self):
        """Print extraction summary."""
        if not self.results:
            print("No results available.")
            return
        
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        
        for group_name, group_data in self.results.get("groups", {}).items():
            print(f"\n   Group: {group_name}")
            for emirate_name, emirate_data in group_data.get("emirates", {}).items():
                print(f"      {emirate_name}:")
                for tpa_name, tpa_data in emirate_data.get("tpas", {}).items():
                    plan_count = len(tpa_data.get("plans", {}))
                    print(f"         {tpa_name}: {plan_count} plans")
