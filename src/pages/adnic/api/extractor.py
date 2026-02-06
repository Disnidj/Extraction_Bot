"""
ADNIC API Extractor

Orchestrates the extraction of ALL dropdown combinations from ADNIC portal.
Uses ADNICApiClient to make API calls and collects all possible values.
"""

import asyncio
from typing import Dict, List, Any, Optional
from patchright.async_api import Page
from src.utils.logger import adnic_logger
from .client import ADNICApiClient, DropdownOption
from .mapping import (
    ADNIC_API_CONFIG,
    INDEPENDENT_APIS,
    TPA_DEPENDENT_APIS,
    NETWORK_DEPENDENT_APIS,
    TCOVER_DEPENDENT_APIS,
    PORTAL_NAME,
    PORTAL_REGION,
)


class ADNICApiExtractor:
    """
    Orchestrates API extraction for all ADNIC dropdown combinations.
    
    Extraction Strategy:
    0. Pre-Level: Get Business Nature options (from registration page)
    1. Level 0: Get all independent options (TPA, Annual Limit, etc.)
    2. Level 1: For each TPA → Get Networks
    3. Level 2: For each TPA+Network → Get TCover, Pharmacy, Dental, Optical
    4. Level 3: For each TPA+Network+TCover → Get Emergency options
    """
    
    def __init__(self, page: Page, business_nature_options: List[Dict] = None):
        """
        Initialize extractor with authenticated page.
        
        Args:
            page: Playwright page with active ADNIC session
            business_nature_options: Pre-extracted Business Nature options from auth flow (optional)
        """
        self.client = ADNICApiClient(page)
        self.records: List[Dict] = []
        self.business_nature_options = business_nature_options or []
        self.stats = {
            "tpa_count": 0,
            "network_count": 0,
            "tcover_count": 0,
            "records_count": 0,
        }
    
    def _create_record(
        self,
        field_name: str,
        values: List[str],
        tpa: str = "",
        network: str = "",
        tcover_elective: str = ""
    ) -> Dict:
        """
        Create a record in the standard extraction format.
        
        Args:
            field_name: Name of the dropdown field
            values: List of option values
            tpa: TPA name (optional)
            network: Network name (optional)
            tcover_elective: Territorial Cover name (optional)
            
        Returns:
            Dict in extraction format
        """
        data = {
            "Portal": PORTAL_NAME,
            "TPA": tpa,
            "Region": PORTAL_REGION,
            "Network": network,
            "field name": field_name,
            "values": values
        }
        if tcover_elective:
            data["Territorial Cover - Elective"] = tcover_elective
        
        return {"data": data}
    
    async def extract_business_nature(self) -> List[DropdownOption]:
        """
        Extract Business Nature options (Pre-Level).
        
        Uses pre-extracted options from auth flow if available.
        
        Returns:
            List of Business Nature DropdownOption objects
        """
        print("\n📥 Pre-Level: Extracting Business Nature Options...")
        
        if self.business_nature_options:
            # Convert dict format to DropdownOption objects
            options = [
                DropdownOption(
                    name=opt.get("name", ""),
                    value=opt.get("value", ""),
                    is_default=False
                )
                for opt in self.business_nature_options
            ]
            
            # Create record for Business Nature
            record = self._create_record(
                "Business Nature",
                [o.name for o in options]
            )
            self.records.append(record)
            
            print(f"   ✓ Business Nature: {len(options)} options")
            return options
        else:
            print("   ⚠️ No Business Nature options available")
            return []
    
    async def extract_level_0(self) -> Dict[str, List[DropdownOption]]:
        """
        Extract Level 0: Independent options (no dependencies).
        
        Returns:
            Dict mapping endpoint to list of options
        """
        print("\n📥 Level 0: Fetching Independent Options...")
        
        # Call all independent APIs in parallel
        tasks = [
            self.client.get_independent_options(api["endpoint"], api["category"])
            for api in INDEPENDENT_APIS
        ]
        results = await asyncio.gather(*tasks)
        
        independent = {}
        for api, options in zip(INDEPENDENT_APIS, results):
            endpoint = api["endpoint"]
            display_name = api["display_name"]
            
            independent[endpoint] = options
            
            # Create record
            record = self._create_record(display_name, [o.name for o in options])
            self.records.append(record)
            
            print(f"   ✓ {display_name}: {len(options)} options")
        
        return independent
    
    async def extract_level_1(self, tpa: DropdownOption) -> List[DropdownOption]:
        """
        Extract Level 1: TPA-dependent options (Networks).
        
        Args:
            tpa: Selected TPA option
            
        Returns:
            List of Network options
        """
        networks = []
        
        for api in TPA_DEPENDENT_APIS:
            options = await self.client.get_tpa_dependent_options(
                api["endpoint"],
                api["category"],
                tpa.value
            )
            
            # Create record
            record = self._create_record(
                api["display_name"],
                [o.name for o in options],
                tpa=tpa.name
            )
            self.records.append(record)
            
            if api["endpoint"] == "GetNetworkTPA":
                networks = options
        
        self.stats["network_count"] += len(networks)
        print(f"   📋 Networks available: {len(networks)}")
        
        return networks
    
    async def extract_level_2(
        self,
        tpa: DropdownOption,
        network: DropdownOption
    ) -> Dict[str, List[DropdownOption]]:
        """
        Extract Level 2: TPA+Network dependent options.
        
        Args:
            tpa: Selected TPA option
            network: Selected Network option
            
        Returns:
            Dict mapping endpoint to list of options
        """
        # Call Level 2 APIs in parallel
        tasks = [
            self.client.get_network_dependent_options(
                api["endpoint"],
                api["category"],
                tpa.value,
                network.value
            )
            for api in NETWORK_DEPENDENT_APIS
        ]
        results = await asyncio.gather(*tasks)
        
        level2 = {}
        for api, options in zip(NETWORK_DEPENDENT_APIS, results):
            endpoint = api["endpoint"]
            display_name = api["display_name"]
            
            level2[endpoint] = options
            
            # Create record
            record = self._create_record(
                display_name,
                [o.name for o in options],
                tpa=tpa.name,
                network=network.name
            )
            self.records.append(record)
            
            print(f"      ✓ {display_name}: {len(options)} options")
        
        return level2
    
    async def extract_level_3(
        self,
        tpa: DropdownOption,
        network: DropdownOption,
        tcover: DropdownOption
    ) -> List[DropdownOption]:
        """
        Extract Level 3: TPA+Network+TCover dependent options (Emergency).
        
        Args:
            tpa: Selected TPA option
            network: Selected Network option
            tcover: Selected Territorial Cover option
            
        Returns:
            List of Emergency options
        """
        emergency_options = []
        
        for api in TCOVER_DEPENDENT_APIS:
            options = await self.client.get_tcover_dependent_options(
                api["endpoint"],
                api["category"],
                tpa.value,
                network.value,
                tcover.value
            )
            
            # Create record
            record = self._create_record(
                api["display_name"],
                [o.name for o in options],
                tpa=tpa.name,
                network=network.name,
                tcover_elective=tcover.name
            )
            self.records.append(record)
            
            emergency_options = options
            print(f"         → {tcover.name}: {len(options)} emergency options")
        
        return emergency_options
    
    async def extract_all(self) -> List[Dict]:
        """
        Extract ALL possible dropdown combinations.
        
        Iteration Order:
        Pre-Level: Get Business Nature options (from registration page)
        FOR each TPA in [ADNIC, NextCare, Nas]:
            FOR each Network in [networks for this TPA]:
                FOR each TerritorialCover in [covers for TPA+Network]:
                    → Get Emergency options
                → Get Pharmacy, Dental, Optical
            → Get Networks
        
        Returns:
            List of all extracted records
        """
        print("\n" + "=" * 60)
        print("🚀 ADNIC API EXTRACTION - ALL COMBINATIONS")
        print("=" * 60)
        
        # Pre-Level: Business Nature options
        await self.extract_business_nature()
        
        # Level 0: Independent options
        independent = await self.extract_level_0()
        
        tpa_options = independent.get("GetTPAByProduct", [])
        self.stats["tpa_count"] = len(tpa_options)
        
        # Level 1-3: Cascading options
        print(f"\n📥 Level 1-3: Processing {len(tpa_options)} TPAs...")
        
        for tpa_idx, tpa in enumerate(tpa_options, 1):
            print(f"\n{'─' * 50}")
            print(f"🏢 TPA {tpa_idx}/{len(tpa_options)}: {tpa.name} ({tpa.value})")
            print(f"{'─' * 50}")
            
            # Level 1: Get Networks
            networks = await self.extract_level_1(tpa)
            
            # For each Network
            for net_idx, network in enumerate(networks, 1):
                print(f"\n   🔹 Network {net_idx}/{len(networks)}: {network.name}")
                
                # Level 2: Get TCover, Pharmacy, Dental, Optical
                level2 = await self.extract_level_2(tpa, network)
                
                # Level 3: For each TCover → Get Emergency
                tcovers = level2.get("GetTerritorialCover", [])
                self.stats["tcover_count"] += len(tcovers)
                
                print(f"      🌍 Processing {len(tcovers)} Territorial Covers...")
                
                for tcover in tcovers:
                    await self.extract_level_3(tpa, network, tcover)
        
        # Update stats
        self.stats["records_count"] = len(self.records)
        
        # Print summary
        self._print_summary()
        
        return self.records
    
    def _print_summary(self):
        """Print extraction summary."""
        client_stats = self.client.get_stats()
        
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"   TPAs processed:        {self.stats['tpa_count']}")
        print(f"   Networks processed:    {self.stats['network_count']}")
        print(f"   TCover combinations:   {self.stats['tcover_count']}")
        print(f"   Total API calls:       {client_stats['total_api_calls']}")
        print(f"   Total records saved:   {self.stats['records_count']}")
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
