"""
Liva Insurance API Extractor

Orchestrates the extraction of ALL dropdown combinations from Liva Insurance portal.
Uses LivaInsuranceApiClient to make API calls and collects all possible values.

Extraction Strategy:
1. Level 0: Get TPA options (independent)
2. Level 1: For each TPA → Get Regions
3. Level 2: For each TPA+Region → Get Networks
4. Level 3: For each TPA+Region+Network → Get 20 benefit fields in parallel
5. Level 4: For each TPA+Region+Network+AnnualLimit → Get Dental Limit
6. Level 5: For each TPA+Region+Network+AL+DentalLimit → Get Dental Copay
"""

import asyncio
from typing import Dict, List, Tuple
from patchright.async_api import Page
from src.utils.logger import liva_insurance_logger
from .client import LivaInsuranceApiClient, DropdownOption
from .mapping import (
    INDEPENDENT_APIS,
    TPA_DEPENDENT_APIS,
    REGION_DEPENDENT_APIS,
    NETWORK_DEPENDENT_APIS,
    ANNUAL_LIMIT_DEPENDENT_APIS,
    DENTAL_LIMIT_DEPENDENT_APIS,
    PORTAL_NAME,
    PORTAL_REGION,
)


class LivaInsuranceApiExtractor:
    """
    Orchestrates API extraction for all Liva Insurance dropdown combinations.
    """

    def __init__(self, page: Page):
        self.client = LivaInsuranceApiClient(page)
        self.records: List[Dict] = []
        self.all_networks: set = set()
        self.stats = {
            "tpa_count": 0,
            "region_count": 0,
            "network_count": 0,
            "annual_limit_combos": 0,
            "records_count": 0,
        }

    def _create_record(
        self,
        field_name: str,
        values: List[str],
        tpa: str = "",
        network: str = "",
        region: str = "",
        annual_limit: str = "",
        dental_limit: str = ""
    ) -> Dict:
        """Create a record in the standard extraction format."""
        data = {
            "Portal": PORTAL_NAME,
            "TPA": tpa,
            "Region": region if region else PORTAL_REGION,
            "Network": network,
            "field name": field_name,
            "values": values
        }
        if annual_limit:
            data["Annual Limit"] = annual_limit
        if dental_limit:
            data["Dental Limit"] = dental_limit

        return {"data": data}

    async def extract_level_0(self) -> Dict[str, List[DropdownOption]]:
        """Extract Level 0: TPA options (independent)."""
        print("\n📥 Level 0: Fetching TPA Options...")

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

            record = self._create_record(display_name, [o.name for o in options])
            self.records.append(record)

            print(f"   ✓ {display_name}: {len(options)} options")

        return independent

    async def extract_level_1(self, tpa: DropdownOption) -> List[DropdownOption]:
        """Extract Level 1: Regions for a TPA."""
        regions = []

        for api in TPA_DEPENDENT_APIS:
            options = await self.client.get_tpa_dependent_options(
                api["endpoint"], api["category"], tpa.value
            )
            if api["endpoint"] == "GetDropDownRegion":
                regions = options

        self.stats["region_count"] += len(regions)
        print(f"   📋 Regions available: {len(regions)}")

        return regions

    async def extract_level_2(
        self, tpa: DropdownOption, region: DropdownOption
    ) -> List[DropdownOption]:
        """Extract Level 2: Networks for a TPA+Region."""
        networks = []

        for api in REGION_DEPENDENT_APIS:
            options = await self.client.get_region_dependent_options(
                api["endpoint"], api["category"], tpa.value, region.value
            )

            for opt in options:
                self.all_networks.add(opt.name)

            if api["endpoint"] == "GetDropDownNWRegion":
                networks = options

        self.stats["network_count"] += len(networks)
        print(f"      📋 Networks available: {len(networks)}")

        return networks

    async def extract_level_3(
        self, tpa: DropdownOption, region: DropdownOption, network: DropdownOption
    ) -> Dict[str, List[DropdownOption]]:
        """
        Extract Level 3: All benefit fields for TPA+Region+Network.
        Calls all 20 APIs in parallel.
        """
        tasks = [
            self.client.get_network_dependent_options(
                api["endpoint"], api["category"],
                tpa.value, region.value, network.value
            )
            for api in NETWORK_DEPENDENT_APIS
        ]
        results = await asyncio.gather(*tasks)

        level3 = {}
        for api, options in zip(NETWORK_DEPENDENT_APIS, results):
            endpoint = api["endpoint"]
            display_name = api["display_name"]

            level3[endpoint] = options

            record = self._create_record(
                display_name,
                [o.name for o in options],
                tpa=tpa.name,
                network=network.name,
                region=region.name
            )
            self.records.append(record)

            print(f"         ✓ {display_name}: {len(options)} options")

        return level3

    async def extract_level_4(
        self, tpa: DropdownOption, region: DropdownOption,
        network: DropdownOption, annual_limit: DropdownOption
    ) -> Dict[str, List[DropdownOption]]:
        """Extract Level 4: Dental Limit for TPA+Region+Network+AnnualLimit."""
        level4 = {}

        for api in ANNUAL_LIMIT_DEPENDENT_APIS:
            options = await self.client.get_annual_limit_dependent_options(
                api["endpoint"], api["category"],
                tpa.value, region.value, network.value, annual_limit.value
            )

            level4[api["endpoint"]] = options

            record = self._create_record(
                api["display_name"],
                [o.name for o in options],
                tpa=tpa.name,
                network=network.name,
                region=region.name,
                annual_limit=annual_limit.name
            )
            self.records.append(record)

            print(f"            → Dental Limit (AL={annual_limit.name}): {len(options)} options")

        return level4

    async def extract_level_5(
        self, tpa: DropdownOption, region: DropdownOption,
        network: DropdownOption, annual_limit: DropdownOption,
        dental_limit: DropdownOption
    ) -> List[DropdownOption]:
        """Extract Level 5: Dental Copay for TPA+Region+Network+AL+DentalLimit."""
        all_options = []

        for api in DENTAL_LIMIT_DEPENDENT_APIS:
            options = await self.client.get_dental_limit_dependent_options(
                api["endpoint"], api["category"],
                tpa.value, region.value, network.value,
                annual_limit.value, dental_limit.value
            )

            record = self._create_record(
                api["display_name"],
                [o.name for o in options],
                tpa=tpa.name,
                network=network.name,
                region=region.name,
                annual_limit=annual_limit.name,
                dental_limit=dental_limit.name
            )
            self.records.append(record)

            all_options = options
            print(f"               → Dental Copay (DL={dental_limit.name}): {len(options)} options")

        return all_options

    async def extract_all(self) -> List[Dict]:
        """
        Extract ALL possible dropdown combinations.

        Iteration Order:
        Level 0: TPA
        FOR each TPA:
            Level 1: Regions
            FOR each Region:
                Level 2: Networks
                FOR each Network:
                    Level 3: All benefit fields (parallel)
                    Level 4-5: Dental cascading (AL → DentalLimit → DentalCopay)
        """
        print("\n" + "=" * 60)
        print("🚀 LIVA INSURANCE API EXTRACTION - ALL COMBINATIONS")
        print("=" * 60)

        liva_insurance_logger.info("=" * 60)
        liva_insurance_logger.info("🚀 LIVA INSURANCE API EXTRACTION STARTED")
        liva_insurance_logger.info("=" * 60)

        # Level 0: TPA
        independent = await self.extract_level_0()
        tpa_options = independent.get("GetDropDownTPA", [])
        self.stats["tpa_count"] = len(tpa_options)

        liva_insurance_logger.info(f"Level 0 Complete: Found {len(tpa_options)} TPAs")

        # Level 1-5: Cascading
        print(f"\n📥 Level 1-5: Processing {len(tpa_options)} TPAs...")

        for tpa_idx, tpa in enumerate(tpa_options, 1):
            print(f"\n{'─' * 55}")
            print(f"🏢 TPA {tpa_idx}/{len(tpa_options)}: {tpa.name} ({tpa.value})")
            print(f"{'─' * 55}")

            # Level 1: Regions
            regions = await self.extract_level_1(tpa)

            # Create Region record per TPA
            if regions:
                record = self._create_record(
                    "Region", [r.name for r in regions], tpa=tpa.name
                )
                self.records.append(record)

            for reg_idx, region in enumerate(regions, 1):
                print(f"\n   🌍 Region {reg_idx}/{len(regions)}: {region.name}")

                # Level 2: Networks
                networks = await self.extract_level_2(tpa, region)

                # Create Network record per TPA+Region
                if networks:
                    record = self._create_record(
                        "Network", [n.name for n in networks],
                        tpa=tpa.name, region=region.name
                    )
                    self.records.append(record)

                for net_idx, network in enumerate(networks, 1):
                    print(f"\n      🔹 Network {net_idx}/{len(networks)}: {network.name}")

                    # Level 3: All benefit fields in parallel
                    level3 = await self.extract_level_3(tpa, region, network)

                    # Level 4-5: Dental cascading
                    annual_limits = level3.get("GetDropDownALNw", [])
                    if annual_limits:
                        print(f"\n         💰 Processing {len(annual_limits)} Annual Limits for Dental...")
                        self.stats["annual_limit_combos"] += len(annual_limits)

                        for al in annual_limits:
                            # Level 4: Dental Limit
                            level4 = await self.extract_level_4(tpa, region, network, al)

                            # Level 5: Dental Copay
                            dental_limits = level4.get("GetDropDowndentalLimit", [])
                            for dl in dental_limits:
                                await self.extract_level_5(tpa, region, network, al, dl)

        # Add Network dropdown with empty TPA/Network for expansion
        if self.all_networks:
            network_record = self._create_record(
                "Network", list(self.all_networks), tpa="", network=""
            )
            self.records.append(network_record)
            print(f"\n   ✓ Added Network dropdown: {len(self.all_networks)} unique networks")

        # Update stats
        self.stats["records_count"] = len(self.records)

        self._print_summary()

        liva_insurance_logger.info("=" * 60)
        liva_insurance_logger.info(f"✅ EXTRACTION COMPLETE: {len(self.records)} records")
        liva_insurance_logger.info(f"Stats: {self.stats}")
        liva_insurance_logger.info(f"Total API calls: {self.client.call_count}")
        liva_insurance_logger.info("=" * 60)

        return self.records

    def _print_summary(self):
        """Print extraction summary."""
        client_stats = self.client.get_stats()

        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"   TPAs processed:          {self.stats['tpa_count']}")
        print(f"   Regions processed:       {self.stats['region_count']}")
        print(f"   Networks processed:      {self.stats['network_count']}")
        print(f"   Annual Limit combos:     {self.stats['annual_limit_combos']}")
        print(f"   Total API calls:         {client_stats['total_api_calls']}")
        print(f"   Total records saved:     {self.stats['records_count']}")
        print("=" * 60)

    def get_records(self) -> List[Dict]:
        """Get all extracted records."""
        return self.records

    def get_stats(self) -> Dict:
        """Get extraction statistics."""
        return {**self.stats, **self.client.get_stats()}

    def validate_extraction(self) -> Tuple[bool, List[str]]:
        """
        Validate that extraction completed successfully.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        if self.stats["tpa_count"] == 0:
            errors.append("No TPAs extracted")

        if self.stats["network_count"] == 0:
            errors.append("No Networks extracted despite having TPAs")

        if self.stats["records_count"] < 20:
            errors.append(f"Only {self.stats['records_count']} records extracted (expected 20+)")

        # Check API call count is reasonable
        if self.client.call_count < 5:
            errors.append(f"Only {self.client.call_count} API calls made (expected many more)")

        is_valid = len(errors) == 0

        if is_valid:
            liva_insurance_logger.info("✅ Extraction validation passed")
        else:
            for error in errors:
                liva_insurance_logger.error(f"Validation error: {error}")

        return is_valid, errors
