"""
MaxHealth API Extractor
Orchestrates extraction of all dropdown values from MaxHealth portal.

Business Logic Rules:
1. Dubai Only: Filter states to Dubai (StateID: 53)
2. Exclude MEDNET + MAXTAILOR combination
3. Neuron + MAXGLOBAL: Policy Holder Type = SME Group (6), Micro SME (7)
4. Others: Policy Holder Type = SME Group (6), Micro Group (5), Individual (4)
5. Plans from dhaPlans only (Dubai Health Authority)
6. Hierarchical path: TPA → Network → Location → Policy Holder Type → Quotation For → Plan
"""

import json
import os
from datetime import datetime
from src.utils.logger import maxhealth_logger
from .client import MaxHealthAPIClient


# Business Logic Constants
DUBAI_STATE_ID = "53"
DUBAI_STATE_NAME = "Dubai"

# Excluded combinations (TPA Name, Product Name pattern)
EXCLUDED_COMBINATIONS = [
    ("MEDNET", "MAXTAILOR"),
    ("MEDNET", "MAXWELL"),  # Also excluded per API error
]

# Policy Holder Type (Target Group) rules
NEURON_MAXGLOBAL_TARGET_GROUPS = {
    "6": "SME Group",
    "7": "Micro SME"
}

STANDARD_TARGET_GROUPS = {
    "4": "Individual",
    "5": "Micro Group",
    "6": "SME Group"
}


class MaxHealthExtractor:
    """Extracts all dropdown values from MaxHealth portal via API."""
    
    def __init__(self, auth):
        """
        Initialize extractor.
        
        Args:
            auth: MaxHealthAuthToken instance with valid token
        """
        self.auth = auth
        self.results = {
            "portal": "MaxHealth",
            "extracted_at": datetime.now().isoformat(),
            "lookups": {},
            "filtered_lookups": {},  # Business rule filtered values
            "plans_by_combination": {}
        }
        self.stats = {
            "networks": 0,
            "products": 0,
            "combinations_tried": 0,
            "combinations_success": 0,
            "total_plans": 0
        }
    
    def _is_excluded_combination(self, network_name: str, product_name: str) -> bool:
        """Check if TPA + Network combination should be excluded."""
        for excluded_tpa, excluded_product in EXCLUDED_COMBINATIONS:
            if excluded_tpa.upper() in network_name.upper() and excluded_product.upper() in product_name.upper():
                return True
        return False
    
    def _get_valid_target_groups(self, network_name: str, product_name: str, all_target_groups: list) -> list:
        """
        Get valid Policy Holder Types based on TPA + Network combination.
        
        Rules:
        - Neuron + MAXGLOBAL: SME Group (6), Micro SME (7)
        - All others: Individual (4), Micro Group (5), SME Group (6)
        """
        is_neuron_maxglobal = (
            "NEURON" in network_name.upper() and 
            "MAXGLOBAL" in product_name.upper()
        )
        
        if is_neuron_maxglobal:
            valid_ids = NEURON_MAXGLOBAL_TARGET_GROUPS.keys()
        else:
            valid_ids = STANDARD_TARGET_GROUPS.keys()
        
        return [tg for tg in all_target_groups if str(tg.get("value")) in valid_ids]
    
    def _filter_states_to_dubai(self, states: list) -> list:
        """Filter states to only include Dubai."""
        return [s for s in states if str(s.get("value")) == DUBAI_STATE_ID]
    
    async def extract_all(self) -> dict:
        """
        Extract all dropdown values with business logic filtering.
        
        1. Fetch case-lookups (networks, products, states, etc.)
        2. Apply filtering rules (Dubai only, excluded combinations)
        3. For each valid network+product combination, get plans from dhaPlans only
        
        Returns:
            dict: Complete extraction results
        """
        async with MaxHealthAPIClient(self.auth) as client:
            # Step 1: Get case lookups
            print("\n📡 Step 1: Fetching case lookups...")
            lookups = await client.get_case_lookups()
            
            if not lookups or not lookups.get("isSuccess"):
                print("❌ Failed to fetch case lookups")
                return None
            
            self.results["lookups"] = lookups.get("data", {})
            
            networks = self.results["lookups"].get("networks", [])
            products = self.results["lookups"].get("products", [])
            states = self.results["lookups"].get("states", [])
            target_groups = self.results["lookups"].get("targetGroups", [])
            client_statuses = self.results["lookups"].get("clientStatuses", [])
            
            # Apply business rule filters
            dubai_states = self._filter_states_to_dubai(states)
            
            self.results["filtered_lookups"] = {
                "location": dubai_states,
                "location_name": DUBAI_STATE_NAME,
                "all_target_groups": target_groups,
                "quotation_for": client_statuses
            }
            
            self.stats["networks"] = len(networks)
            self.stats["products"] = len(products)
            
            print(f"   ✓ Networks (TPA): {len(networks)}")
            print(f"   ✓ Products (Network): {len(products)}")
            print(f"   ✓ States: {len(states)} → Filtered to Dubai only")
            print(f"   ✓ Target Groups: {len(target_groups)}")
            print(f"   ✓ Client Statuses (Quotation For): {len(client_statuses)}")
            
            # Step 2: Get plans for each valid network + product combination
            print("\n📡 Step 2: Fetching plans for valid TPA+Network combinations...")
            print("   📍 Location: Dubai (locked)")
            print("   🚫 Excluding: MEDNET+MAXTAILOR, MEDNET+MAXWELL")
            
            for network in networks:
                network_id = network.get("value")
                network_name = network.get("title")
                
                print(f"\n   🔹 TPA: {network_name} (ID: {network_id})")
                
                for product in products:
                    product_id = product.get("value")
                    product_name = product.get("title")
                    
                    # Check if product belongs to this network (cascading rule)
                    product_network = product.get("other")
                    if product_network and product_network != network_id:
                        continue  # Skip - product doesn't belong to this network
                    
                    # Check exclusion rules
                    if self._is_excluded_combination(network_name, product_name):
                        print(f"      📄 Network: {product_name}... ⏭️ Excluded (business rule)")
                        continue
                    
                    # Get valid target groups for this combination
                    valid_target_groups = self._get_valid_target_groups(
                        network_name, product_name, target_groups
                    )
                    
                    self.stats["combinations_tried"] += 1
                    print(f"      📄 Network: {product_name}...", end=" ")
                    
                    # Get plans for this combination
                    response = await client.get_plans_by_upload(network_id, product_id)
                    
                    if response and response.get("isSuccess"):
                        data = response.get("data", {})
                        
                        # Extract plans from dhaPlans ONLY (Dubai restriction)
                        plans = self._extract_plans_from_dha_only(data)
                        
                        if plans:
                            combo_key = f"{network_name}_{product_name}"
                            self.results["plans_by_combination"][combo_key] = {
                                "network_id": network_id,
                                "network_name": network_name,  # TPA
                                "product_id": product_id,
                                "product_name": product_name,  # Network
                                "location": DUBAI_STATE_NAME,
                                "valid_target_groups": [
                                    {"id": tg.get("value"), "name": tg.get("title")} 
                                    for tg in valid_target_groups
                                ],
                                "quotation_for": [
                                    {"id": cs.get("value"), "name": cs.get("title")} 
                                    for cs in client_statuses
                                ],
                                "plans": plans
                            }
                            self.stats["combinations_success"] += 1
                            self.stats["total_plans"] += len(plans)
                            print(f"✓ {len(plans)} plans (Dubai/DHA)")
                        else:
                            print("⚠️ No DHA plans")
                    else:
                        print("❌ Failed")
        
        return self.results
    
    def _extract_plans_from_dha_only(self, data: dict) -> list:
        """
        Extract plans from dhaPlans ONLY (Dubai Health Authority).
        Since location is locked to Dubai, ignore dohPlans entirely.
        
        Args:
            data: Response data dict
            
        Returns:
            list: List of plan dicts with id and title
        """
        plans = []
        seen_ids = set()
        
        # Get plans from plansByGroup.dhaPlans ONLY
        plans_by_group = data.get("plansByGroup", {})
        dha_plans = plans_by_group.get("dhaPlans", [])
        
        for plan in dha_plans:
            plan_id = plan.get("value")
            plan_title = plan.get("title", "").strip()
            
            if plan_id and plan_title and plan_id not in seen_ids:
                plans.append({
                    "id": plan_id,
                    "title": plan_title
                })
                seen_ids.add(plan_id)
        
        # Sort by title
        return sorted(plans, key=lambda x: x.get("title", ""))
    
    def _extract_plans_from_response(self, data: dict) -> list:
        """
        Legacy method - kept for backwards compatibility.
        Use _extract_plans_from_dha_only instead.
        """
        return [p.get("title") for p in self._extract_plans_from_dha_only(data)]
    
    def save_results(self, output_dir: str = "extracted_data") -> str:
        """
        Save extraction results to JSON file.
        
        Args:
            output_dir: Base directory to save file
            
        Returns:
            str: Path to saved file
        """
        portal_dir = os.path.join(output_dir, "maxhealth")
        os.makedirs(portal_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(portal_dir, f"maxhealth_benefits_{timestamp}.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 JSON results saved to {output_file}")
        maxhealth_logger.info(f"Results saved to {output_file}")
        return output_file
    
    def print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"   Networks (TPA): {self.stats['networks']}")
        print(f"   Products (Network): {self.stats['products']}")
        print(f"   Combinations tried: {self.stats['combinations_tried']}")
        print(f"   Combinations success: {self.stats['combinations_success']}")
        print(f"   Total plans extracted: {self.stats['total_plans']}")
        print(f"   Location: Dubai only (DHA plans)")

