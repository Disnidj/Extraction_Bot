"""
Takaful API Extractor
Orchestrates extraction of all dropdown values using API calls.
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
    
    async def extract_all_benefits(self):
        """
        Extract all benefit dropdown values for Dubai TPAs and Plans.
        Uses hardcoded mapping for TPA IDs, fetches plans dynamically,
        then gets all benefit dropdown values for each plan.
        
        Returns:
            dict: Complete extraction results
        """
        self.results = {
            "portal": "TAKAFUL EMARAT",
            "extracted_at": datetime.now().isoformat(),
            "emirates": {}
        }
        
        async with TakafulAPIClient(self.auth) as client:
            # Process Dubai only (as per requirements)
            dubai_data = TAKAFUL_MAPPING["emirates"]["Dubai"]
            dubai_results = await self._extract_emirate_data(client, "Dubai", dubai_data)
            self.results["emirates"]["Dubai"] = dubai_results
        
        return self.results
    
    async def _extract_emirate_data(self, client, emirate_name, emirate_config):
        """
        Extract data for a single emirate.
        
        Args:
            client: TakafulAPIClient instance
            emirate_name: Name of the emirate
            emirate_config: Configuration dict for this emirate
            
        Returns:
            dict: Emirate extraction results
        """
        print(f"\n🌍 Processing Emirate: {emirate_name}")
        
        emirate_results = {
            "emirates_id": emirate_config["emirates_id"],
            "tpas": {}
        }
        
        for tpa_name, tpa_config in emirate_config["tpas"].items():
            tpa_results = await self._extract_tpa_data(client, tpa_name, tpa_config)
            emirate_results["tpas"][tpa_name] = tpa_results
        
        return emirate_results
    
    async def _extract_tpa_data(self, client, tpa_name, tpa_config):
        """
        Extract data for a single TPA.
        
        Args:
            client: TakafulAPIClient instance
            tpa_name: Name of the TPA
            tpa_config: Configuration dict for this TPA
            
        Returns:
            dict: TPA extraction results
        """
        print(f"\n   📍 Processing TPA: {tpa_name}")
        
        tpa_id = tpa_config["tpa_id"]
        reinsurer_company_id = tpa_config["reinsurer_company_id"]
        
        tpa_results = {
            "tpa_id": tpa_id,
            "reinsurer_company_id": reinsurer_company_id,
            "plans": {}
        }
        
        # Fetch plans for this TPA
        plans = await client.get_plans(tpa_id)
        print(f"      Found {len(plans)} plans")
        
        for plan in plans:
            plan_results = await self._extract_plan_data(
                client, plan, reinsurer_company_id
            )
            plan_name = plan.get("plans", "").strip()
            tpa_results["plans"][plan_name] = plan_results
        
        print(f"   ✅ Completed TPA: {tpa_name}")
        return tpa_results
    
    async def _extract_plan_data(self, client, plan, reinsurer_company_id):
        """
        Extract benefit data for a single plan.
        
        Args:
            client: TakafulAPIClient instance
            plan: Plan data dict from API
            reinsurer_company_id: Reinsurer company ID
            
        Returns:
            dict: Plan extraction results with benefits
        """
        plan_id = plan.get("plan_id")
        plan_name = plan.get("plans", "").strip()
        reinsurer_plan_id = plan.get("reinsurer_plan_id")
        
        print(f"      📋 Fetching benefits for: {plan_name} (ID: {plan_id})")
        
        # Fetch benefits for this plan
        benefits = await client.get_benefits(plan_id, reinsurer_company_id)
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.3)
        
        return {
            "plan_id": plan_id,
            "reinsurer_plan_id": reinsurer_plan_id,
            "reinsurer_company_id": reinsurer_company_id,
            "benefits": benefits
        }
    
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
        
        for emirate_name, emirate_data in self.results.get("emirates", {}).items():
            print(f"\n   {emirate_name}:")
            for tpa_name, tpa_data in emirate_data.get("tpas", {}).items():
                plan_count = len(tpa_data.get("plans", {}))
                print(f"      {tpa_name}: {plan_count} plans")
