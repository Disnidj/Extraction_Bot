"""
Sukoon API Extractor

Orchestrates extraction of ALL dropdown combinations from Sukoon portal.
Unlike ADNIC (4 nested loops), Sukoon uses ONE loop over indemnityId values.

The "Mega API" pattern means:
- 1 API call returns ALL sub-options for a given indemnityId
- Much simpler loop structure
- Fewer API calls needed
"""

import asyncio
from typing import Dict, List, Any
from patchright.async_api import Page
from src.utils.logger import sukoon_logger
from .client import SukoonApiClient, DropdownOption
from .mapping import PORTAL_NAME, REGIONS, RESPONSE_FIELD_MAPPING


class SukoonApiExtractor:
    """
    Orchestrates API extraction for Sukoon dropdowns.
    
    Extraction Strategy (MUCH SIMPLER than ADNIC):
    1. Get list of indemnityId options (the "master switch")
    2. FOR each indemnityId → Call PopulateDDL → Get ALL sub-options
    3. Record all combinations
    
    That's it! ONE loop instead of four.
    
    Comparison:
    - ADNIC: 4 nested loops, ~176 API calls
    - Sukoon: 1 loop, ~5 API calls for Dubai
    """
    
    def __init__(self, page: Page):
        """
        Initialize extractor with authenticated page.
        
        Args:
            page: Playwright page with active Sukoon session
        """
        self.client = SukoonApiClient(page)
        self.records: List[Dict] = []
        self.stats = {
            "regions_count": 0,
            "indemnity_count": 0,
            "records_count": 0,
        }
    
    def _create_record(
        self,
        field_name: str,
        values: List[str],
        region: str = "",
        indemnity_limit: str = ""
    ) -> Dict:
        """
        Create a record in the standard extraction format.
        
        Args:
            field_name: Name of the dropdown field
            values: List of option values
            region: Region name (Dubai, etc.)
            indemnity_limit: Indemnity limit context
            
        Returns:
            Dict in extraction format
        """
        return {
            "data": {
                "Portal": PORTAL_NAME,
                "Region": region,
                "Indemnity Limit": indemnity_limit,
                "TPA": "",  # Sukoon doesn't have TPA in same sense as ADNIC
                "Network": "",
                "field name": field_name,
                "values": values
            }
        }
    
    async def extract_all(self, regions: List[str] = None) -> List[Dict]:
        """
        Extract ALL possible dropdown combinations.
        
        Sukoon Loop Structure (SIMPLE):
        
        FOR each region in [Dubai, Abu Dhabi, ...]:
            ├─► Call PopulateDDL(indemnityId=0) → Get indemnity options
            │
            └─► FOR each indemnityId in [1, 2, 3, 4, ...]:
                    │
                    └─► Call PopulateDDL(indemnityId=X) → Get ALL options
                        • Geographical Area options
                        • Network options
                        • Deductible options
                        • Co-Insurance options
                        • Lab/X-Ray options
                        • Enhanced Plan options
        
        Total API calls: (# of regions) × (1 + # of indemnity limits)
        Much fewer than ADNIC's 176 calls!
        
        Args:
            regions: List of regions to extract (default: ["Dubai"])
            
        Returns:
            List of all extracted records
        """
        if regions is None:
            regions = ["Dubai"]  # Default to Dubai
        
        print("\n" + "=" * 60)
        print("🚀 SUKOON API EXTRACTION - ALL COMBINATIONS")
        print("=" * 60)
        print("📌 Using Mega API pattern: PopulateDDL")
        print("📌 One API call returns ALL options for each indemnity level")
        print("=" * 60)
        
        for region in regions:
            await self._extract_region(region)
        
        # Update stats
        self.stats["records_count"] = len(self.records)
        
        # Print summary
        self._print_summary()
        
        return self.records
    
    async def _extract_region(self, region: str):
        """
        Extract all options for a single region.
        
        Args:
            region: Region name (Dubai, Abu Dhabi, etc.)
        """
        print(f"\n{'─' * 50}")
        print(f"🌍 Region: {region}")
        print(f"{'─' * 50}")
        
        self.stats["regions_count"] += 1
        
        # ═══════════════════════════════════════════════════════════
        # Step 1: Get the master list of indemnity options
        # ═══════════════════════════════════════════════════════════
        print("\n📥 Step 1: Getting Indemnity Limit options (master switch)...")
        indemnity_options = await self.client.get_indemnity_options(region)
        
        if not indemnity_options:
            print("   ⚠️ No indemnity options returned - check session/census")
            print("   → Trying alternative approach...")
            
            # Try calling with a known indemnityId to see if we get data
            test_result = await self.client.call_populate_ddl("1", region)
            if test_result:
                indemnity_options = test_result.get("ProductIndemnity", [])
        
        if not indemnity_options:
            print("   ❌ Could not get indemnity options. Skipping region.")
            return
        
        print(f"   ✓ Found {len(indemnity_options)} indemnity limits")
        for opt in indemnity_options:
            print(f"      • {opt.text} (ID: {opt.value})")
        
        # Record the indemnity limits themselves (master list)
        record = self._create_record(
            "Indemnity Limit",
            [opt.text for opt in indemnity_options],
            region=region
        )
        self.records.append(record)
        
        # ═══════════════════════════════════════════════════════════
        # Step 2: For each indemnity limit, get all sub-options
        # This is the MAIN LOOP - only ONE level deep!
        # ═══════════════════════════════════════════════════════════
        print(f"\n📥 Step 2: Extracting options for each indemnity limit...")
        
        for idx, indemnity in enumerate(indemnity_options, 1):
            print(f"\n   💰 [{idx}/{len(indemnity_options)}] Limit: {indemnity.text} (ID: {indemnity.value})")
            
            self.stats["indemnity_count"] += 1
            
            # Call the Mega API with this indemnityId
            # This ONE call returns ALL options for this limit tier!
            all_options = await self.client.call_populate_ddl(
                indemnity_id=indemnity.value,
                region_name=region
            )
            
            if not all_options:
                print(f"      ⚠️ No options returned for indemnityId={indemnity.value}")
                continue
            
            # Record each field's options
            for field_key, options in all_options.items():
                if field_key == "ProductIndemnity":
                    continue  # Already recorded above
                
                if not options:
                    continue  # Skip empty lists
                
                field_info = RESPONSE_FIELD_MAPPING.get(field_key, {})
                display_name = field_info.get("display_name", field_key)
                
                # Create record with indemnity context
                record = self._create_record(
                    display_name,
                    [opt.text for opt in options],
                    region=region,
                    indemnity_limit=indemnity.text
                )
                self.records.append(record)
                
                print(f"      ✓ {display_name}: {len(options)} options")
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.3)
    
    def _print_summary(self):
        """Print extraction summary."""
        client_stats = self.client.get_stats()
        
        print("\n" + "=" * 60)
        print("📊 SUKOON EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"   Regions processed:     {self.stats['regions_count']}")
        print(f"   Indemnity limits:      {self.stats['indemnity_count']}")
        print(f"   Total API calls:       {client_stats['total_api_calls']}")
        print(f"   Total records saved:   {self.stats['records_count']}")
        print("=" * 60)
        print("📌 Note: Sukoon uses 'Mega API' - fewer calls than ADNIC!")
        print("=" * 60)
    
    def get_records(self) -> List[Dict]:
        """Get all extracted records."""
        return self.records
    
    def get_stats(self) -> Dict:
        """Get extraction statistics."""
        return {
            **self.stats,
            **self.client.get_stats()
        }
