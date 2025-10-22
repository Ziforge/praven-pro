"""
eBird Data Preloader

Downloads and caches regional eBird occurrence data at startup to avoid
API rate limiting during validation. Uses regional hotspot data and recent
observations to build a local occurrence database.
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
import time


class eBirdPreloader:
    """Preloads and caches regional eBird data."""

    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "cache/ebird"):
        """
        Initialize preloader.

        Args:
            api_key: eBird API key (defaults to EBIRD_API_KEY env var)
            cache_dir: Directory for cached data
        """
        self.api_key = api_key or os.getenv("EBIRD_API_KEY")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.base_url = "https://api.ebird.org/v2"
        self.headers = {"X-eBirdApiToken": self.api_key} if self.api_key else {}

        # Cache duration: 7 days
        self.cache_duration = timedelta(days=7)

        # Regional species cache
        self.regional_species: Dict[str, Set[str]] = {}
        self.recent_observations: Dict[str, List[Dict]] = {}

    def get_region_code(self, lat: float, lon: float) -> str:
        """
        Get eBird region code from coordinates.

        For now, use a simple grid-based approach.
        Could be enhanced with actual eBird region lookup.
        """
        # Simple grid: 1-degree cells
        lat_grid = int(lat)
        lon_grid = int(lon)
        return f"grid_{lat_grid}_{lon_grid}"

    def preload_region(
        self,
        lat: float,
        lon: float,
        radius_km: int = 50,
        days_back: int = 30,
        force_refresh: bool = False,
        auto_update: bool = True
    ) -> Dict[str, any]:
        """
        Preload eBird data for a region.

        AUTO-UPDATE BEHAVIOR (when auto_update=True):
        - Checks cache on every run
        - Uses cached data if < 7 days old
        - Auto-refreshes if >= 7 days old
        - Downloads fresh data if no cache exists

        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in km
            days_back: How many days of observations to fetch
            force_refresh: Force refresh even if cached data exists
            auto_update: Automatically update stale cache (default: True)

        Returns:
            Dictionary with preloaded data statistics
        """
        region_code = self.get_region_code(lat, lon)
        cache_file = self.cache_dir / f"{region_code}_r{radius_km}_d{days_back}.json"

        # Check cache on every run
        needs_refresh = force_refresh
        cache_age_days = None

        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            cache_age_days = cache_age.days

            # Auto-update if cache is stale
            if auto_update and cache_age >= self.cache_duration:
                print(f"eBird cache is stale ({cache_age_days} days old, max {self.cache_duration.days})")
                print(f"  Auto-refreshing...")
                needs_refresh = True
            elif cache_age < self.cache_duration:
                # Cache is fresh, use it
                print(f"Loading cached eBird data for region {region_code}")
                print(f"  Cache age: {cache_age_days} days (max: {self.cache_duration.days})")
                print(f"  Next update in: {(self.cache_duration - cache_age).days} days")

                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)

                self.regional_species[region_code] = set(cached_data['species'])
                self.recent_observations[region_code] = cached_data['observations']

                return {
                    'region': region_code,
                    'species_count': len(cached_data['species']),
                    'observation_count': len(cached_data['observations']),
                    'cache_age_days': cache_age_days,
                    'days_until_refresh': (self.cache_duration - cache_age).days,
                    'cached': True
                }
        else:
            print(f"No eBird cache found for region {region_code}")
            print(f"  Downloading fresh data...")
            needs_refresh = True

        # Only fetch if we need to
        if not needs_refresh:
            return  # Should not reach here, but safety check

        # Fetch fresh data from eBird API
        print(f"  Center: ({lat}, {lon})")
        print(f"  Radius: {radius_km} km")
        print(f"  Days back: {days_back}")

        if not self.api_key:
            print("  WARNING: No eBird API key - using offline mode")
            return self._create_offline_cache(region_code, cache_file)

        species_set = set()
        observations = []

        try:
            # Fetch recent observations in region
            url = f"{self.base_url}/data/obs/geo/recent"
            params = {
                'lat': lat,
                'lng': lon,
                'dist': radius_km,
                'back': days_back,
                'maxResults': 10000  # Maximum allowed
            }

            print(f"  Requesting: {url}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                observations = data

                for obs in data:
                    if 'comName' in obs:
                        species_set.add(obs['comName'])

                print(f"  Received {len(observations)} observations")
                print(f"  Found {len(species_set)} species")

            elif response.status_code == 429:
                print(f"  WARNING: Rate limit hit - using cached/offline data")
                return self._create_offline_cache(region_code, cache_file)
            else:
                print(f"  WARNING: API error {response.status_code}")
                return self._create_offline_cache(region_code, cache_file)

            # Small delay to be nice to API
            time.sleep(0.5)

        except Exception as e:
            print(f"  ERROR: {e}")
            return self._create_offline_cache(region_code, cache_file)

        # Cache the data
        cache_data = {
            'region': region_code,
            'lat': lat,
            'lon': lon,
            'radius_km': radius_km,
            'days_back': days_back,
            'species': list(species_set),
            'observations': observations,
            'cached_at': datetime.now().isoformat(),
            'observation_count': len(observations)
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

        self.regional_species[region_code] = species_set
        self.recent_observations[region_code] = observations

        print(f"  Cached to: {cache_file}")

        return {
            'region': region_code,
            'species_count': len(species_set),
            'observation_count': len(observations),
            'cache_age_days': 0,
            'cached': False
        }

    def _create_offline_cache(self, region_code: str, cache_file: Path) -> Dict:
        """Create empty offline cache for when API is unavailable."""
        cache_data = {
            'region': region_code,
            'species': [],
            'observations': [],
            'cached_at': datetime.now().isoformat(),
            'offline_mode': True
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

        self.regional_species[region_code] = set()
        self.recent_observations[region_code] = []

        return {
            'region': region_code,
            'species_count': 0,
            'observation_count': 0,
            'cache_age_days': 0,
            'cached': True,
            'offline_mode': True
        }

    def check_species_expected(
        self,
        species_name: str,
        lat: float,
        lon: float
    ) -> Tuple[bool, Optional[float]]:
        """
        Check if species is expected in region (from preloaded data).

        Args:
            species_name: Common name of species
            lat: Latitude
            lon: Longitude

        Returns:
            (is_expected, frequency_estimate)
        """
        region_code = self.get_region_code(lat, lon)

        if region_code not in self.regional_species:
            # Region not preloaded - return neutral
            return (True, None)  # Don't reject if we don't have data

        species_set = self.regional_species[region_code]

        if not species_set:
            # Offline mode - return neutral
            return (True, None)

        is_expected = species_name in species_set

        # Calculate rough frequency estimate
        frequency = None
        if region_code in self.recent_observations:
            total_obs = len(self.recent_observations[region_code])
            if total_obs > 0:
                species_obs = sum(
                    1 for obs in self.recent_observations[region_code]
                    if obs.get('comName') == species_name
                )
                frequency = species_obs / total_obs

        return (is_expected, frequency)

    def get_cache_info(self) -> Dict:
        """Get information about cached regions."""
        cache_files = list(self.cache_dir.glob("*.json"))

        info = {
            'cache_dir': str(self.cache_dir),
            'cached_regions': len(cache_files),
            'total_species': sum(len(s) for s in self.regional_species.values()),
            'regions': {}
        }

        for region, species in self.regional_species.items():
            info['regions'][region] = {
                'species_count': len(species),
                'observation_count': len(self.recent_observations.get(region, []))
            }

        return info


# Convenience function for preloading at startup
def preload_for_study(
    lat: float,
    lon: float,
    radius_km: int = 50,
    days_back: int = 30,
    api_key: Optional[str] = None
) -> eBirdPreloader:
    """
    Preload eBird data for a study site.

    Args:
        lat: Study site latitude
        lon: Study site longitude
        radius_km: Radius around site
        days_back: Days of recent observations
        api_key: eBird API key (optional)

    Returns:
        Configured eBirdPreloader instance
    """
    preloader = eBirdPreloader(api_key=api_key)
    stats = preloader.preload_region(lat, lon, radius_km, days_back)

    print("\neBird Preload Complete!")
    print(f"  Region: {stats['region']}")
    print(f"  Species: {stats['species_count']}")
    print(f"  Observations: {stats['observation_count']}")
    if stats.get('offline_mode'):
        print(f"  Mode: OFFLINE (no API key or rate limited)")
    elif stats['cached']:
        print(f"  Mode: CACHED ({stats['cache_age_days']} days old)")
    else:
        print(f"  Mode: FRESH (just downloaded)")

    return preloader
