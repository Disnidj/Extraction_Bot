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
            "network_count": 0,
            "records_count": 0,
        }
    
    def _create_record(
        self,
        field_name: str,
        values: List[str],
        region: str = "",
        tpa: str = "",
        network: str = ""
    ) -> Dict:
        """
        Create a record in the standard extraction format.
        
        Mapping to match ADNIC/Qatar/Takaful format:
        - TPA = Indemnity Limit (master cascading field)
        - Network = Applicable Network (second-level cascading field)
        
        Args:
            field_name: Name of the dropdown field
            values: List of option values
            region: Region name (Dubai, etc.)
            tpa: TPA value (Indemnity Limit in Sukoon, e.g., "1000000")
            network: Network value (Applicable Network in Sukoon, e.g., "Edge")
            
        Returns:
            Dict in extraction format
        """
        return {
            "data": {
                "Portal": PORTAL_NAME,
                "Region": region,
                "TPA": tpa,  # Indemnity Limit maps to TPA
                "Network": network,  # Applicable Network maps to Network
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
        # Step 1: Get the master list of TPA options (Indemnity Limit = TPA)
        # ═══════════════════════════════════════════════════════════
        print("\n📥 Step 1: Getting TPA options (Indemnity Limit = TPA in Sukoon)...")
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
        
        print(f"   ✓ Found {len(indemnity_options)} TPAs (Indemnity Limits)")
        for opt in indemnity_options:
            print(f"      • {opt.text} (ID: {opt.value})")
        
        # Record the TPA options (Indemnity Limit = TPA in Sukoon)
        # This is the master list showing all available TPAs
        record = self._create_record(
            "TPA",
            [opt.text for opt in indemnity_options],
            region=region
        )
        self.records.append(record)
        
        # ═══════════════════════════════════════════════════════════
        # Step 2: For each TPA (Indemnity Limit), get networks and sub-options
        # TWO LEVEL LOOP: TPA → Network → Other fields
        # ═══════════════════════════════════════════════════════════
        print(f"\n📥 Step 2: Extracting options for each TPA + Network combination...")
        
        for idx, indemnity in enumerate(indemnity_options, 1):
            print(f"\n   🏢 TPA [{idx}/{len(indemnity_options)}]: {indemnity.text} (ID: {indemnity.value})")
            
            self.stats["indemnity_count"] += 1
            
            # First call: Get networks available for this TPA
            all_options = await self.client.call_populate_ddl(
                indemnity_id=indemnity.value,
                region_name=region
            )
            
            if not all_options:
                print(f"      ⚠️ No options returned for indemnityId={indemnity.value}")
                continue
            
            # Get network options for this TPA
            network_options = all_options.get("IndemnityNetwork", [])
            
            # Record the network options list for this TPA
            if network_options:
                record = self._create_record(
                    "Network",
                    [opt.text for opt in network_options],
                    region=region,
                    tpa=indemnity.text
                )
                self.records.append(record)
                print(f"      📋 Networks available: {len(network_options)}")
            
            # ═══════════════════════════════════════════════════════
            # Step 2b: For each Network, get the dependent options
            # This tests if options change per network selection
            # ═══════════════════════════════════════════════════════
            if network_options:
                for net_idx, network in enumerate(network_options, 1):
                    print(f"\n      🔹 Network [{net_idx}/{len(network_options)}]: {network.text}")
                    self.stats["network_count"] += 1
                    
                    # Try calling API with networkId to see if options differ
                    network_options_result = await self.client.call_populate_ddl(
                        indemnity_id=indemnity.value,
                        region_name=region,
                        network_id=network.value
                    )
                    
                    # Record each field's options with TPA + Network context
                    for field_key, options in network_options_result.items():
                        if field_key in ["ProductIndemnity", "IndemnityNetwork"]:
                            continue  # Already recorded above
                        
                        if not options:
                            continue  # Skip empty lists
                        
                        field_info = RESPONSE_FIELD_MAPPING.get(field_key, {})
                        display_name = field_info.get("display_name", field_key)
                        
                        # Create record with TPA + Network context
                        record = self._create_record(
                            display_name,
                            [opt.text for opt in options],
                            region=region,
                            tpa=indemnity.text,
                            network=network.text
                        )
                        self.records.append(record)
                        
                        print(f"         ✓ {display_name}: {len(options)} options")
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.2)
            else:
                # No networks - record fields without network context
                for field_key, options in all_options.items():
                    if field_key == "ProductIndemnity":
                        continue
                    
                    if not options:
                        continue
                    
                    field_info = RESPONSE_FIELD_MAPPING.get(field_key, {})
                    display_name = field_info.get("display_name", field_key)
                    
                    record = self._create_record(
                        display_name,
                        [opt.text for opt in options],
                        region=region,
                        tpa=indemnity.text
                    )
                    self.records.append(record)
                    
                    print(f"      ✓ {display_name}: {len(options)} options")
            
            # Small delay between TPAs
            await asyncio.sleep(0.3)
    
    def _print_summary(self):
        """Print extraction summary."""
        client_stats = self.client.get_stats()
        
        print("\n" + "=" * 60)
        print("📊 SUKOON EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"   Regions processed:     {self.stats['regions_count']}")
        print(f"   TPAs (Indemnity):      {self.stats['indemnity_count']}")
        print(f"   Networks processed:    {self.stats['network_count']}")
        print(f"   Total API calls:       {client_stats['total_api_calls']}")
        print(f"   Total records saved:   {self.stats['records_count']}")
        print("=" * 60)
        print("📌 Note: TPA = Indemnity Limit, Network = Applicable Network")
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
