"""
Orient Aura API Extractor
Orchestrates extraction of all dropdown values using API calls.

Flow (Orient-specific):
Pre-Level: Industry Categories (Business Nature)
Level 0: Groups
Level 1: Emirates (per group)
Level 2: TPAs (per emirate)
Level 3: Plans (per TPA)
Level 4: Benefits (per plan)
"""

import json
import os
from datetime import datetime
from src.utils.logger import orient_aura_logger
from .client import OrientAuraAPIClient
from .mapping import PORTAL_REGION, ORIENT_MAPPING


class OrientAuraAPIExtractor:
    """Extracts all dropdown values via API calls."""
    
    def __init__(self, auth):
        """
        Initialize extractor with auth token.
        
        Args:
            auth: OrientAuraAuthToken instance with valid token
        """
        self.auth = auth
        self.results = None
        self.errors = []  # Track errors during extraction
    
    async def extract_all_benefits(self):
        """
        Extract all benefit dropdown values for Orient Aura portal.
        
        Hierarchy:
        - Industry Categories (Pre-Level)
        - Groups → Emirates → TPAs → Plans → Benefits
        
        Returns:
            dict: Complete extraction results with errors tracked
        """
        orient_aura_logger.info("="*60)
        orient_aura_logger.info("🚀 ORIENT AURA API EXTRACTION STARTED")
        orient_aura_logger.info("="*60)
        
        self.errors = []  # Reset errors for new extraction
        self.results = {
            "portal": "ORIENT AURA",
            "extracted_at": datetime.now().isoformat(),
            "industry_categories": [],
            "groups": {},
            "errors": []  # Will be populated at the end
        }
        
        async with OrientAuraAPIClient(self.auth) as client:
            # Pre-Level: Extract Industry Categories (Business Nature)
            print("\n📥 Pre-Level: Extracting Industry Categories (Business Nature)...")
            orient_aura_logger.info("Pre-Level: Extracting Industry Categories")
            industries = await client.get_industries()
            if industries:
                # Only include industries where allows="true"
                allowed_industries = [
                    ind["industry_name"] 
                    for ind in industries 
                    if ind.get("allows", "").lower() == "true"
                ]
                self.results["industry_categories"] = allowed_industries
                orient_aura_logger.info(f"Industry Categories: {len(allowed_industries)} options extracted")
                print(f"   ✓ Industry Categories: {len(allowed_industries)} options")
            else:
                orient_aura_logger.warning("No Industry Categories found")
                print("   ⚠️ No Industry Categories found")
            
            # Level 0: Get groups from API and find matching group by name
            target_group_name = ORIENT_MAPPING["group"]["group_name"]  # "Nextcare Sme"
            print(f"\n📥 Level 0: Fetching groups from API, looking for: {target_group_name}")
            orient_aura_logger.info(f"Fetching groups from API, target: {target_group_name}")
            
            all_groups = await client.get_groups(version_id=ORIENT_MAPPING["version_id"])
            orient_aura_logger.info(f"Found {len(all_groups)} groups from API")
            
            # Check if API returned empty (could be server error)
            if not all_groups:
                error_msg = f"API returned no groups - possible server error or connectivity issue"
                orient_aura_logger.error(error_msg)
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
                orient_aura_logger.error(error_msg)
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
            orient_aura_logger.info(f"Using Group from API: {group_name} (ID: {group_id})")
            
            # Process the matched group
            print(f"\n🏢 Processing Group: {group_name} (ID: {group_id})")
            orient_aura_logger.info(f"Processing Group: {group_name}")
            
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
            client: OrientAuraAPIClient instance
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
            orient_aura_logger.warning(f"No emirates found for group {group_name}")
            print(f"   ⚠️ No emirates found")
            return group_results
        
        # Filter to Dubai only (like Takaful, Qatar, ADNIC)
        dubai_emirate = None
        for emirate in emirates_list:
            if emirate.get("emirates", "").strip().lower() == "dubai":
                dubai_emirate = emirate
                break
        
        if not dubai_emirate:
            orient_aura_logger.warning(f"Dubai emirate not found for group {group_name}")
            print(f"   ⚠️ Dubai emirate not found")
            return group_results
        
        print(f"   📍 Processing: Dubai only ")
        orient_aura_logger.info(f"Processing Dubai emirate only")
        
        # Process Dubai emirate only
        emirate_name = dubai_emirate.get("emirates")
        emirate_results = await self._extract_emirate_data(
            client, emirate_name, dubai_emirate
        )
        group_results["emirates"][emirate_name] = emirate_results
        
        return group_results
    
    async def _extract_emirate_data(self, client, emirate_name, emirate_config):
        """
        Extract data for a single emirate.
        
        Args:
            client: OrientAuraAPIClient instance
            emirate_name: Name of the emirate
            emirate_config: Emirate configuration dict from API
            
        Returns:
            dict: Emirate extraction results
        """
        print(f"\n🌍 Processing Emirate: {emirate_name}")
        orient_aura_logger.info(f"Processing emirate: {emirate_name}")
        
        emirates_id = emirate_config.get("emirates_master_id")
        
        emirate_results = {
            "emirates_master_id": emirates_id,
            "group_id": emirate_config.get("group_id"),
            "reinsurer_company_id": emirate_config.get("reinsurer_company_id"),
            "tpas": {}
        }
        
        # Fetch TPAs for this emirate
        tpas = await client.get_tpas(emirates_id)
        
        if not tpas:
            orient_aura_logger.warning(f"No TPAs found for {emirate_name}")
            print(f"   ⚠️ No TPAs found")
            return emirate_results
        
        print(f"   🏥 Found {len(tpas)} TPAs")
        orient_aura_logger.info(f"Found {len(tpas)} TPAs for {emirate_name}")
        
        # Process each TPA
        for tpa in tpas:
            tpa_name = tpa.get("tpa_name")
            print(f"\n   📋 Processing TPA: {tpa_name}")
            orient_aura_logger.info(f"Processing TPA: {tpa_name}")
            tpa_results = await self._extract_tpa_data(client, tpa_name, tpa)
            emirate_results["tpas"][tpa_name] = tpa_results
            print(f"   ✅ Completed TPA: {tpa_name}")
        
        print(f"✅ Completed Emirate: {emirate_name}")
        return emirate_results
    
    async def _extract_tpa_data(self, client, tpa_name, tpa_config):
        """
        Extract data for a single TPA.
        
        Args:
            client: OrientAuraAPIClient instance
            tpa_name: Name of the TPA
            tpa_config: TPA configuration dict from API
            
        Returns:
            dict: TPA extraction results
        """
        tpa_id = tpa_config.get("tpa_id")
        
        tpa_results = {
            "tpa_id": tpa_id,
            "group_id": tpa_config.get("group_id"),
            "emirates_id": tpa_config.get("emirates_id"),
            "reinsurer_company_id": tpa_config.get("reinsurer_company_id"),
            "plans": {}
        }
        
        # Fetch plans for this TPA
        plans = await client.get_plans(tpa_id)
        
        if not plans:
            orient_aura_logger.warning(f"No plans found for TPA {tpa_name}")
            print(f"      ⚠️ No plans found")
            return tpa_results
        
        print(f"      📄 Found {len(plans)} plans")
        orient_aura_logger.info(f"Found {len(plans)} plans for TPA {tpa_name}")
        
        # Process each plan
        for plan in plans:
            plan_name = plan.get("plans", "").strip()
            plan_id = plan.get("plan_id")
            print(f"         📋 Extracting plan: {plan_name} (ID: {plan_id})")
            plan_results = await self._extract_plan_data(client, plan)
            tpa_results["plans"][plan_name] = plan_results
        
        return tpa_results
    
    async def _extract_plan_data(self, client, plan):
        """
        Extract benefit data for a single plan.
        
        Args:
            client: OrientAuraAPIClient instance
            plan: Plan data dict from API
            
        Returns:
            dict: Plan extraction results with benefits
        """
        plan_id = plan.get("plan_id")
        plan_name = plan.get("plans", "").strip()
        reinsurer_company_id = plan.get("reinsurer_company_id")
        
        orient_aura_logger.debug(f"Extracting plan: {plan_name} (ID: {plan_id})")
        
        # Fetch benefits for this plan
        benefits = await client.get_benefits(plan_id, reinsurer_company_id)
        
        return {
            "plan_id": plan_id,
            "reinsurer_plan_id": plan.get("reinsurer_plan_id"),
            "reinsurer_company_id": reinsurer_company_id,
            "reinsurer_company_name": plan.get("reinsurer_company_name"),
            "benefits": benefits
        }
    
    def save_results(self, output_dir: str = "extracted_data") -> str:
        """
        Save extraction results to JSON file.
        
        Args:
            output_dir: Base directory to save file
            
        Returns:
            str: Path to saved file
        """
        # Save to portal-specific subfolder
        portal_dir = os.path.join(output_dir, "orient_aura")
        os.makedirs(portal_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"orient_aura_benefits_{timestamp}.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 JSON results saved to {output_file}")
        orient_aura_logger.info(f"Results saved to {output_file}")
        return output_file
    
    def print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        
        if not self.results:
            print("   No results available")
            return
        
        # Count statistics
        groups_count = len(self.results.get("groups", {}))
        emirates_list = []
        tpas_list = []
        plans_count = 0
        benefits_count = 0
        
        for group_data in self.results.get("groups", {}).values():
            for emirate_name, emirate_data in group_data.get("emirates", {}).items():
                emirates_list.append(emirate_name)
                for tpa_name, tpa_data in emirate_data.get("tpas", {}).items():
                    tpas_list.append(f"{emirate_name} - {tpa_name}")
                    for plan_data in tpa_data.get("plans", {}).values():
                        plans_count += 1
                        if isinstance(plan_data.get("benefits"), dict):
                            benefits_count += len(plan_data["benefits"])
        
        print(f"   Region: {emirates_list[0] if emirates_list else 'N/A'} (like Takaful/Qatar/ADNIC)")
        print(f"   Groups processed: {groups_count}")
        print(f"   TPAs processed: {len(set(tpas_list))}")
        print(f"   Plans extracted: {plans_count}")
        print(f"   Benefit categories: {benefits_count}")
        print(f"   Industry categories: {len(self.results.get('industry_categories', []))}")
        print("=" * 60)
