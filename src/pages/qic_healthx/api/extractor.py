"""
QIC HealthX API Extractor
Orchestrates extraction of all benefit dropdown values from QIC HealthX API.

Flow:
1. Fetch all plans (filtered to Dubai)
2. For each plan, extract all benefits (simple + nested)
3. Map to required output fields
"""

import json
import os
from datetime import datetime
from src.utils.logger import qic_healthx_logger
from .client import QICHealthXAPIClient
from .mapping import (
    PORTAL_NAME, PORTAL_REGION, TPA_NAME,
    NESTED_BENEFITS, REQUIRED_FIELDS
)


class QICHealthXExtractor:
    """Extracts all dropdown values from QIC HealthX API."""
    
    def __init__(self, auth):
        """
        Initialize extractor with auth token.
        
        Args:
            auth: QICHealthXAuthToken instance with valid token
        """
        self.auth = auth
        self.results = None
        self.errors = []
    
    async def extract_all_benefits(self):
        """
        Extract all benefit dropdown values for QIC HealthX portal.
        
        Returns:
            dict: Complete extraction results with all benefits
        """
        qic_healthx_logger.info("=" * 60)
        qic_healthx_logger.info("🚀 QIC HEALTHX API EXTRACTION STARTED")
        qic_healthx_logger.info("=" * 60)
        
        print("\n" + "=" * 60)
        print("🏢 QIC HEALTHX EXCLUSIVE - API EXTRACTION")
        print("=" * 60)
        print(f"📍 TPA: {TPA_NAME}")
        print(f"📍 Region: {PORTAL_REGION}")
        print(f"📍 Required Fields: {len(REQUIRED_FIELDS)}")
        print("=" * 60)
        
        self.errors = []
        self.results = {
            "portal": PORTAL_NAME,
            "tpa": TPA_NAME,
            "region": PORTAL_REGION,
            "extracted_at": datetime.now().isoformat(),
            "plans": {},
            "all_benefits": {},  # Consolidated benefits across all plans
            "errors": []
        }
        
        async with QICHealthXAPIClient(self.auth) as client:
            # Fetch Dubai plans only
            print("\n📥 Level 0: Fetching Dubai plans from API...")
            qic_healthx_logger.info("Fetching Dubai plans from API")
            
            dubai_plans = await client.get_dubai_plans()
            
            if not dubai_plans:
                error_msg = "No Dubai plans found in API response"
                qic_healthx_logger.error(error_msg)
                self.errors.append(error_msg)
                print(f"   ❌ {error_msg}")
                self.results["errors"] = self.errors
                return self.results
            
            print(f"   ✓ Found {len(dubai_plans)} Dubai plans")
            qic_healthx_logger.info(f"Found {len(dubai_plans)} Dubai plans")
            
            for plan in dubai_plans:
                print(f"      - {plan.get('name', 'Unknown')}")
            
            # Process each plan
            print("\n📥 Level 1: Extracting benefits from each plan...")
            for i, plan in enumerate(dubai_plans, 1):
                plan_name = plan.get("name", "Unknown")
                plan_id = plan.get("id", "")
                
                print(f"\n   [{i}/{len(dubai_plans)}] Processing: {plan_name}")
                qic_healthx_logger.info(f"Processing plan: {plan_name}")
                
                plan_benefits = self._extract_plan_benefits(plan)
                
                self.results["plans"][plan_name] = {
                    "id": plan_id,
                    "benefits": plan_benefits
                }
                
                # Print benefit count
                print(f"       ✓ Extracted {len(plan_benefits)} benefit types")
                
                # Merge into consolidated benefits
                self._merge_benefits(plan_benefits)
        
        # Validate required fields
        self._validate_required_fields()
        
        # Add final summary
        self._generate_summary()
        self.results["errors"] = self.errors
        
        qic_healthx_logger.info("=" * 60)
        qic_healthx_logger.info("✓ QIC HEALTHX API EXTRACTION COMPLETED")
        qic_healthx_logger.info("=" * 60)
        
        return self.results
    
    def _validate_required_fields(self):
        """Validate that all required fields have been extracted."""
        extracted = set(self.results.get("all_benefits", {}).keys())
        required = set(REQUIRED_FIELDS)
        
        missing = required - extracted
        extra = extracted - required
        
        if missing:
            error_msg = f"Missing required fields: {', '.join(sorted(missing))}"
            qic_healthx_logger.warning(error_msg)
            self.errors.append(error_msg)
        
        qic_healthx_logger.info(f"Field validation: {len(extracted)}/{len(required)} required fields extracted")
        
        if extra:
            qic_healthx_logger.debug(f"Extra fields extracted: {', '.join(sorted(extra))}")
    
    def _extract_plan_benefits(self, plan: dict) -> dict:
        """
        Extract all benefits from a single plan.
        Uses API's 'name' field directly (not code mapping) for resilience.
        
        Args:
            plan: Plan object from API
            
        Returns:
            dict: Extracted benefits {dropdown_name: [values]}
        """
        benefits = {}
        
        optional_benefits = plan.get("rules", {}).get("optional_benefits", [])
        
        for benefit in optional_benefits:
            name = benefit.get("name", "").strip()
            limit_options = benefit.get("limit_options", {})
            
            if not name:
                continue
            
            # Check if it's a nested benefit (limit + copay)
            if name in NESTED_BENEFITS:
                nested_config = NESTED_BENEFITS[name]
                
                # Extract limit values from 'data' array
                limit_name = nested_config["limit_name"]
                limit_values = self._extract_nested_limit_values(limit_options)
                benefits[limit_name] = limit_values
                qic_healthx_logger.debug(f"  {limit_name}: {len(limit_values)} options")
                
                # Extract copay values from 'options' array (top-level labels)
                copay_name = nested_config["copay_name"]
                copay_values = self._extract_nested_copay_values(limit_options)
                benefits[copay_name] = copay_values
                qic_healthx_logger.debug(f"  {copay_name}: {len(copay_values)} options")
            else:
                # Simple benefit - use API name directly
                values = self._extract_simple_values(limit_options)
                benefits[name] = values
                qic_healthx_logger.debug(f"  {name}: {len(values)} options")
        
        return benefits
    
    def _extract_simple_values(self, limit_options: dict) -> list:
        """
        Extract values from simple benefit options array.
        
        Args:
            limit_options: The limit_options object
            
        Returns:
            list: List of option labels
        """
        options = limit_options.get("options", [])
        return [opt.get("label", "").strip() for opt in options if opt.get("label")]
    
    def _extract_nested_limit_values(self, limit_options: dict) -> list:
        """
        Extract limit values from nested benefit 'data' array.
        
        Args:
            limit_options: The limit_options object
            
        Returns:
            list: List of limit option labels
        """
        data = limit_options.get("data", [])
        return [item.get("label", "").strip() for item in data if item.get("label")]
    
    def _extract_nested_copay_values(self, limit_options: dict) -> list:
        """
        Extract copay values from nested benefit 'options' array.
        The copay is the top-level label in options (e.g., "0%", "10%", "20%")
        
        Args:
            limit_options: The limit_options object
            
        Returns:
            list: List of copay option labels
        """
        options = limit_options.get("options", [])
        return [opt.get("label", "").strip() for opt in options if opt.get("label")]
    
    def _merge_benefits(self, plan_benefits: dict):
        """
        Merge plan benefits into consolidated all_benefits.
        Uses set to avoid duplicates while preserving order.
        
        Args:
            plan_benefits: Benefits from a single plan
        """
        for dropdown_name, values in plan_benefits.items():
            if dropdown_name not in self.results["all_benefits"]:
                self.results["all_benefits"][dropdown_name] = []
            
            # Add new values that don't exist
            existing = set(self.results["all_benefits"][dropdown_name])
            for val in values:
                if val and val not in existing:
                    self.results["all_benefits"][dropdown_name].append(val)
                    existing.add(val)
    
    def _generate_summary(self):
        """Generate extraction summary statistics."""
        self.results["summary"] = {
            "total_plans": len(self.results["plans"]),
            "total_dropdown_types": len(self.results["all_benefits"]),
            "dropdown_counts": {
                name: len(values) 
                for name, values in self.results["all_benefits"].items()
            }
        }
    
    def save_results(self, output_dir: str = "extracted_data") -> str:
        """
        Save extraction results to JSON file.
        
        Args:
            output_dir: Base output directory
            
        Returns:
            str: Path to saved JSON file
        """
        if not self.results:
            raise ValueError("No results to save. Run extract_all_benefits first.")
        
        # Save to portal-specific subfolder (matches Orient Aura pattern)
        portal_dir = os.path.join(output_dir, "qic_healthx")
        os.makedirs(portal_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON (naming matches other portals: *_benefits_*.json)
        json_file = os.path.join(portal_dir, f"qic_healthx_benefits_{timestamp}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        qic_healthx_logger.info(f"Saved JSON results to: {json_file}")
        print(f"   📄 JSON saved: {json_file}")
        
        return json_file
    
    def print_summary(self):
        """Print extraction summary to console."""
        if not self.results:
            print("No results to summarize")
            return
        
        summary = self.results.get("summary", {})
        all_benefits = self.results.get("all_benefits", {})
        
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"   Portal: {PORTAL_NAME}")
        print(f"   TPA: {TPA_NAME}")
        print(f"   Region: {PORTAL_REGION}")
        print(f"   Total Plans: {summary.get('total_plans', 0)}")
        print(f"   Total Dropdown Types: {summary.get('total_dropdown_types', 0)}")
        print(f"   Required Fields: {len(REQUIRED_FIELDS)}")
        
        # Validate required fields
        extracted_fields = set(all_benefits.keys())
        required_set = set(REQUIRED_FIELDS)
        extracted_required = required_set & extracted_fields
        missing_required = required_set - extracted_fields
        
        print(f"   Fields Extracted: {len(extracted_required)}/{len(REQUIRED_FIELDS)} ✓")
        
        if missing_required:
            print(f"\n   ⚠️ MISSING REQUIRED FIELDS ({len(missing_required)}):")
            for field in sorted(missing_required):
                print(f"      ❌ {field}")
        
        print("\n   Dropdown Counts:")
        for name, count in sorted(summary.get("dropdown_counts", {}).items()):
            status = "✓" if name in required_set else "+"
            print(f"      {status} {name}: {count} options")
        
        errors = self.results.get("errors", [])
        if errors:
            print(f"\n   ⚠️ Errors ({len(errors)}):")
            for error in errors:
                print(f"      ❌ {error}")
        
        print("=" * 60)
