"""
Al Sagr API Extractor
Orchestrates extraction of benefit data from Al Sagr portal.

Extraction Flow:
1. Call GetGroupQuotationBenefitStructure to get plans, categories, benefit structure
2. For EACH unique plan (not per category - benefits are identical):
   - Call GetBenefitsByPlan to get benefit values
3. Collect all benefit values and map benefitId to field names

Key Optimization:
- Benefits are IDENTICAL across categories for the same plan
- Only ONE API call per plan is needed (not per plan+category combination)
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from src.utils.logger import alsagr_logger
from .client import AlSagrAPIClient
from .mapping import (
    PORTAL_NAME, 
    PORTAL_REGION, 
    BENEFIT_FIELD_MAPPING,
    FIELD_MAPPING,
    SELECTED_TPA_ID,
    SELECTED_TPA_NAME,
    REQUIRED_VISA_REGION,
)


class AlSagrAPIExtractor:
    """
    Orchestrates API extraction for Al Sagr benefit data.
    
    Unlike cascading dropdown portals (ADNIC, Takaful), Al Sagr extracts
    benefit VALUES for each plan, not dropdown OPTIONS.
    
    The benefit structure is:
    - Each plan has the same benefit fields (benefitId)
    - Each benefit field has a value for each plan
    - Benefits are identical across categories for the same plan
    """
    
    def __init__(self, auth, quotation_id: int = None, proposal_id: int = None):
        """
        Initialize extractor with auth token.
        
        Args:
            auth: AlSagrAuthToken instance with valid token
            quotation_id: Quotation ID to extract (can be set later)
            proposal_id: Proposal ID (can be extracted from benefit structure)
        """
        self.auth = auth
        self.quotation_id = quotation_id
        self.proposal_id = proposal_id
        self.results = {
            "portal": PORTAL_NAME,
            "region": PORTAL_REGION,
            "extraction_time": None,
            "quotation_id": quotation_id,
            "proposal_id": proposal_id,
            "tpa_options": [],  # TPA dropdown options
            "plans": [],
            "categories": [],
            "benefits": [],
            "records": [],
            "errors": [],
        }
        self.stats = {
            "api_calls": 0,
            "tpa_count": 0,
            "plans_count": 0,
            "categories_count": 0,
            "benefit_fields_count": 0,
            "records_count": 0,
        }
    
    async def extract_all_benefits(self, quotation_id: int = None) -> Dict:
        """
        Extract all benefit data for a quotation.
        
        Flow:
        1. Get benefit structure (plans, categories, benefit fields)
        2. Get proposalId from structure
        3. For each unique plan:
           - Get benefit values (ONE call per plan)
        4. Format results
        
        Args:
            quotation_id: Optional quotation ID (uses self.quotation_id if not provided)
            
        Returns:
            dict: Extraction results
        """
        if quotation_id:
            self.quotation_id = quotation_id
        
        if not self.quotation_id:
            error = "No quotation_id provided"
            alsagr_logger.error(error)
            self.results["errors"].append(error)
            return self.results
        
        self.results["quotation_id"] = self.quotation_id
        self.results["extraction_time"] = datetime.now().isoformat()
        
        print("\n" + "=" * 60)
        print("🚀 AL SAGR API EXTRACTION")
        print("=" * 60)
        print(f"📌 Quotation ID: {self.quotation_id}")
        print("=" * 60)
        
        async with AlSagrAPIClient(self.auth) as client:
            # Pre-Level: Get TPA options (filter to NEXT CARE MANAGEMENT LLC only)
            print("\n📋 Pre-Level: Fetching TPA options...")
            tpa_options = await client.get_tpa_masters()
            
            if tpa_options:
                # Filter to only NEXT CARE MANAGEMENT LLC (domainValue: 1)
                filtered_tpa = [
                    tpa for tpa in tpa_options 
                    if tpa.get('domainValue') == SELECTED_TPA_ID
                ]
                
                if filtered_tpa:
                    self.results["tpa_options"] = filtered_tpa
                    self.stats["tpa_count"] = len(filtered_tpa)
                    print(f"   ✓ Using TPA: {SELECTED_TPA_NAME} (ID: {SELECTED_TPA_ID})")
                    
                    # Create TPA record with only NEXT CARE MANAGEMENT LLC
                    tpa_record = {
                        "data": {
                            "Portal": PORTAL_NAME,
                            "Region": PORTAL_REGION,
                            "TPA": "",  # Empty for dropdown option
                            "Network": "",
                            "field name": "TPA",
                            "values": [SELECTED_TPA_NAME],  # Only this TPA
                        }
                    }
                    self.results["records"].append(tpa_record)
                else:
                    print(f"   ⚠️  TPA {SELECTED_TPA_NAME} not found in response")
            else:
                print("   ⚠️  Could not fetch TPA options")
            
            # Step 1: Get benefit structure
            print("\n📋 Step 1: Fetching benefit structure...")
            structure = await client.get_benefit_structure(self.quotation_id)
            
            if not structure:
                error = "Failed to get benefit structure"
                self.results["errors"].append(error)
                return self.results
            
            # Extract components
            plan_benefits = structure.get("planBenefits", [])
            categories = structure.get("category", [])
            benefit_structure = structure.get("benefitStructure", [])
            proposal_masters = structure.get("proposalMasters", [])
            
            # Get proposal ID
            if proposal_masters:
                self.proposal_id = proposal_masters[0].get("proposalId")
                self.results["proposal_id"] = self.proposal_id
                print(f"   ✓ Proposal ID: {self.proposal_id}")
            else:
                error = "No proposalMasters found in response"
                self.results["errors"].append(error)
                return self.results
            
            # Store metadata
            self.results["categories"] = categories
            self.stats["categories_count"] = len(categories)
            self.stats["benefit_fields_count"] = len(benefit_structure)
            
            print(f"   ✓ Found {len(plan_benefits)} plan-category combinations")
            print(f"   ✓ Found {len(categories)} categories")
            print(f"   ✓ Found {len(benefit_structure)} benefit fields")
            
            # Step 2: Get unique plans (benefits are same across categories)
            unique_plans = self._get_unique_plans(plan_benefits)
            self.stats["plans_count"] = len(unique_plans)
            
            print(f"\n📋 Step 2: Extracting benefits for {len(unique_plans)} unique plans...")
            print("   (Only 1 API call per plan - benefits identical across categories)")
            
            # Step 3: Get benefits for each unique plan
            # NOTE: For API extraction, we include ALL plans (no visa region filter)
            # This ensures we get all dropdown values for the database
            all_plans_benefits = []
            
            for idx, plan in enumerate(unique_plans, 1):
                plan_id = plan["planId"]
                plan_name = plan["planName"]
                
                print(f"\n   [{idx}/{len(unique_plans)}] Plan {plan_id}: {plan_name}")
                
                benefits = await client.get_benefits_by_plan(
                    plan_id=plan_id,
                    quotation_id=self.quotation_id,
                    proposal_id=self.proposal_id
                )
                
                if benefits:
                    # Check Visa Region - only include Dubai plans
                    visa_region = self._get_visa_region_from_benefits(benefits)
                    
                    if visa_region == REQUIRED_VISA_REGION:
                        plan_record = self._process_plan_benefits(plan, benefits)
                        all_plans_benefits.append(plan_record)
                        print(f"      ✓ Got {len(benefits)} benefit values (Visa Region: {visa_region})")
                    else:
                        print(f"      ⏩ Skipping - Visa Region: {visa_region or 'N/A'} (Required: {REQUIRED_VISA_REGION})")
                else:
                    error = f"Failed to get benefits for plan {plan_id}"
                    self.results["errors"].append(error)
                    print(f"      ❌ {error}")
            
            # Store all plans
            self.results["plans"] = all_plans_benefits
            self.stats["plans_count"] = len(all_plans_benefits)
            print(f"\n   ✓ Extracted {len(all_plans_benefits)} plans")
            
            # Create Network dropdown records - one per plan name
            # Portal's "Plan" names go to "Network" dropdown (MapID 3)
            # Each plan name is a Selection_Value for the Network dropdown
            if all_plans_benefits:
                for plan in all_plans_benefits:
                    plan_name = plan["planName"]
                    network_record = {
                        "data": {
                            "Portal": PORTAL_NAME,
                            "Region": PORTAL_REGION,
                            "TPA": SELECTED_TPA_NAME,  # Fixed TPA
                            "Network": "",  # Empty - this IS the dropdown being populated
                            "field name": "Plan",  # Maps to Network dropdown via FIELD_MAPPING
                            "values": [plan_name],  # Single plan name as value
                        }
                    }
                    self.results["records"].append(network_record)
                
                print(f"   ✓ Created Network dropdown with {len(all_plans_benefits)} plan values")
                
                # Create Plan_Selection dropdown records - one per plan's network type
                # Portal's "Network" (RN/GN/GN+) goes to "Plan_Selection" dropdown (MapID 63)
                # Each network is associated with its parent Network (plan name)
                for plan in all_plans_benefits:
                    plan_name = plan["planName"]
                    network_type = plan.get("network_type", "")
                    
                    if network_type:
                        plan_selection_record = {
                            "data": {
                                "Portal": PORTAL_NAME,
                                "Region": PORTAL_REGION,
                                "TPA": SELECTED_TPA_NAME,
                                "Network": plan_name,  # Cascading: depends on Network (plan name)
                                "field name": "Plan_Selection",  # Maps to Plan_Selection dropdown (DB_TO_PORTAL_DISPLAY["Plan_Selection"] = "Network" = portal display)
                                "values": [network_type],  # RN, GN, or GN+
                            }
                        }
                        self.results["records"].append(plan_selection_record)
                
                print(f"   ✓ Created Plan_Selection dropdown records for {len(all_plans_benefits)} plans")
            
            # Step 4: Create extraction records (for formatter)
            self._create_records()
            
            # Update stats
            self.stats["api_calls"] = client.get_call_count()
            self.stats["records_count"] = len(self.results["records"])
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _get_unique_plans(self, plan_benefits: List[Dict]) -> List[Dict]:
        """
        Get unique plans from plan_benefits (dedupe by planId).
        
        Benefits are identical across categories, so we only need
        one entry per planId.
        
        Args:
            plan_benefits: List of plan-category combinations
            
        Returns:
            List of unique plans
        """
        seen_plan_ids = set()
        unique_plans = []
        
        for pb in plan_benefits:
            plan_id = pb.get("planId")
            if plan_id and plan_id not in seen_plan_ids:
                seen_plan_ids.add(plan_id)
                unique_plans.append({
                    "planId": plan_id,
                    "planName": pb.get("planName", f"Plan {plan_id}"),
                })
        
        return unique_plans
    
    def _get_visa_region_from_benefits(self, benefits: List[Dict]) -> Optional[str]:
        """
        Extract Visa Region value from benefits list.
        
        Args:
            benefits: List of benefit objects
            
        Returns:
            Visa Region value or None
        """
        # benefitId 8 = "Visa Region" based on BENEFIT_FIELD_MAPPING
        # API returns valueText (not value) - e.g. {"benefitId":8,"valueText":"Dubai"}
        for benefit in benefits:
            benefit_id = benefit.get("benefitId")
            if benefit_id == 8:  # Visa Region
                return benefit.get("valueText", "")
        return None
    
    def _process_plan_benefits(self, plan: Dict, benefits: List[Dict]) -> Dict:
        """
        Process benefit values for a plan.
        
        Args:
            plan: Plan dict with planId, planName
            benefits: List of benefit objects with benefitId, value, etc.
            
        Returns:
            Processed plan record with benefits and network_type (RN/GN)
        """
        plan_record = {
            "planId": plan["planId"],
            "planName": plan["planName"],
            "network_type": "",  # Will store RN/GN from benefitId 9 (Portal's "Network" field)
            "benefits": {},
        }
        
        # Map benefitId to valueText (API returns valueText, not value)
        for benefit in benefits:
            benefit_id = benefit.get("benefitId")
            value = benefit.get("valueText", "")  # API returns valueText field
            
            # Get field name from mapping, or use benefitId as fallback
            field_name = BENEFIT_FIELD_MAPPING.get(benefit_id, f"Benefit_{benefit_id}")
            
            # benefitId 9 is the "Network" field (RN, GN, GN+) - store at plan level
            if benefit_id == 9:
                plan_record["network_type"] = value
            
            plan_record["benefits"][field_name] = {
                "benefitId": benefit_id,
                "value": value,
            }
        
        return plan_record
    
    def _create_records(self):
        """
        Create flat records for the formatter.
        
        Each record represents one field value for the database:
        {"Portal": "...", "TPA": "...", "Network": "plan_name", "field_name": "...", "value": "..."}
        
        Filtering applied:
        - TPA: Only NEXT CARE MANAGEMENT LLC
        - Plans: Only with Visa Region = Dubai
        - Network = Plan name (portal's "Plan" → DB's "Network")
        """
        records = []
        
        # TPA, Network, and Plan_Selection records already added in extract_all_benefits
        
        for plan in self.results["plans"]:
            plan_name = plan["planName"]
            
            for field_name, benefit_data in plan["benefits"].items():
                value = benefit_data.get("value", "")
                
                # Skip empty values
                if not value:
                    continue
                
                # Skip "Network" field - already handled as Plan_Selection dropdown
                # benefitId 9 values (RN/GN) are Plan_Selection dropdown options, not benefit values
                if field_name == "Network":
                    continue
                
                record = {
                    "data": {
                        "Portal": PORTAL_NAME,
                        "Region": PORTAL_REGION,
                        "TPA": SELECTED_TPA_NAME,  # Fixed TPA: NEXT CARE MANAGEMENT LLC
                        "Network": plan_name,  # Plan name → DB's Network column
                        "field name": field_name,
                        "values": [str(value)],  # Single value as list for consistency
                    }
                }
                records.append(record)
        
        # Keep TPA, Plan (Network dropdown), and Plan_Selection dropdown records from earlier
        dropdown_records = [
            r for r in self.results["records"] 
            if r.get("data", {}).get("field name") in ["TPA", "Plan", "Plan_Selection"]
        ]
        self.results["records"] = dropdown_records + records
    
    def _print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"   Portal: {PORTAL_NAME}")
        print(f"   Quotation ID: {self.quotation_id}")
        print(f"   Proposal ID: {self.proposal_id}")
        print(f"   API Calls: {self.stats['api_calls']}")
        print(f"   TPA Options: {self.stats['tpa_count']}")
        print(f"   Plans: {self.stats['plans_count']}")
        print(f"   Categories: {self.stats['categories_count']}")
        print(f"   Benefit Fields: {self.stats['benefit_fields_count']}")
        print(f"   Records: {self.stats['records_count']}")
        
        if self.results["errors"]:
            print(f"\n   ⚠️ Errors: {len(self.results['errors'])}")
            for error in self.results["errors"]:
                print(f"      - {error}")
        else:
            print(f"\n   ✓ No errors!")
        
        print("=" * 60)
    
    def save_results(self, output_dir: str = "extracted_data") -> str:
        """
        Save extraction results to JSON file.
        
        Args:
            output_dir: Base output directory
            
        Returns:
            Path to saved JSON file
        """
        # Create portal-specific folder
        portal_dir = os.path.join(output_dir, "alsagr")
        os.makedirs(portal_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alsagr_api_results_{timestamp}.json"
        filepath = os.path.join(portal_dir, filename)
        
        # Save JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        alsagr_logger.info(f"Results saved to {filepath}")
        print(f"\n📁 JSON results saved to: {filepath}")
        
        return filepath
    
    def validate_extraction(self) -> Tuple[bool, List[str]]:
        """
        Validate extraction results.
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        if not self.results["plans"]:
            errors.append("No plans extracted")
        
        if not self.results["records"]:
            errors.append("No records created")
        
        if self.results["errors"]:
            errors.extend(self.results["errors"])
        
        is_valid = len(errors) == 0
        return is_valid, errors
