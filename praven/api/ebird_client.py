"""
eBird API client for species occurrence and frequency data.

API Documentation: https://documenter.getpostman.com/view/664302/S1ENwy59
"""

import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from .cache import APICache


class eBirdClient:
    """Client for eBird API 2.0."""

    BASE_URL = "https://api.ebird.org/v2"

    def __init__(self, api_key: str, cache_dir: str = "cache", cache_ttl_hours: int = 24):
        """
        Initialize eBird API client.

        Args:
            api_key: eBird API key (get from https://ebird.org/api/keygen)
            cache_dir: Directory for caching API responses
            cache_ttl_hours: Cache time-to-live in hours
        """
        if not api_key:
            raise ValueError("eBird API key required. Get one at https://ebird.org/api/keygen")

        self.api_key = api_key
        self.cache = APICache(cache_dir, cache_ttl_hours)
        self.session = requests.Session()
        self.session.headers.update({'X-eBirdApiToken': api_key})

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with error handling."""
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"eBird API error: {e}")
            return {}

    def get_recent_observations(
        self,
        lat: float,
        lon: float,
        radius_km: float = 50,
        days_back: int = 30,
        species_code: Optional[str] = None
    ) -> List[Dict]:
        """
        Get recent observations near a location.

        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers (max 50)
            days_back: Days back to search (max 30)
            species_code: Optional 6-letter eBird species code

        Returns:
            List of observation dictionaries
        """
        cache_key = self.cache._get_cache_key(
            'recent_obs', lat, lon, radius_km, days_back, species_code
        )

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        endpoint = "data/obs/geo/recent"
        if species_code:
            endpoint = f"data/obs/geo/recent/{species_code}"

        params = {
            'lat': lat,
            'lng': lon,
            'dist': min(radius_km, 50),  # eBird max is 50km
            'back': min(days_back, 30)   # eBird max is 30 days
        }

        result = self._make_request(endpoint, params)
        self.cache.set(cache_key, result)
        return result

    def get_regional_checklist(
        self,
        region_code: str,
        date: Optional[str] = None
    ) -> List[str]:
        """
        Get species checklist for a region.

        Args:
            region_code: eBird region code (e.g., 'NO' for Norway, 'NO-50' for Trøndelag)
            date: Optional date in YYYY-MM-DD format

        Returns:
            List of species codes expected in region
        """
        cache_key = self.cache._get_cache_key('checklist', region_code, date)

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        endpoint = f"product/spplist/{region_code}"
        result = self._make_request(endpoint)

        self.cache.set(cache_key, result)
        return result if isinstance(result, list) else []

    def check_species_occurrence(
        self,
        species_common_name: str,
        lat: float,
        lon: float,
        date: str,
        radius_km: float = 50
    ) -> Dict[str, any]:
        """
        Check if a species is expected at a location and time.

        Args:
            species_common_name: Common name of species
            lat: Latitude
            lon: Longitude
            date: Date in YYYY-MM-DD format
            radius_km: Search radius in kilometers

        Returns:
            Dictionary with occurrence information:
            {
                'expected': bool,
                'frequency': float (0-1, or None),
                'recent_obs_count': int,
                'last_seen_date': str or None
            }
        """
        # Calculate days back from date to now
        obs_date = datetime.strptime(date, '%Y-%m-%d')
        days_back = min((datetime.now() - obs_date).days, 30)

        if days_back < 0:
            # Future date - can't check recent observations
            days_back = 30

        # Get recent observations
        observations = self.get_recent_observations(
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            days_back=days_back
        )

        # Check for species
        species_obs = [
            obs for obs in observations
            if obs.get('comName', '').lower() == species_common_name.lower()
        ]

        result = {
            'expected': len(species_obs) > 0,
            'frequency': None,
            'recent_obs_count': len(species_obs),
            'last_seen_date': None
        }

        if species_obs:
            # Get most recent observation
            latest = max(species_obs, key=lambda x: x.get('obsDt', ''))
            result['last_seen_date'] = latest.get('obsDt')

            # Estimate frequency (rough approximation)
            # Divide by total unique observation events in area
            unique_checklists = len(set(obs.get('subId', '') for obs in observations))
            if unique_checklists > 0:
                result['frequency'] = len(species_obs) / unique_checklists

        return result

    def get_hotspots(
        self,
        lat: float,
        lon: float,
        radius_km: float = 50
    ) -> List[Dict]:
        """
        Get eBird hotspots near a location.

        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers

        Returns:
            List of hotspot dictionaries
        """
        cache_key = self.cache._get_cache_key('hotspots', lat, lon, radius_km)

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        endpoint = "ref/hotspot/geo"
        params = {
            'lat': lat,
            'lng': lon,
            'dist': min(radius_km, 50),
            'fmt': 'json'
        }

        result = self._make_request(endpoint, params)
        self.cache.set(cache_key, result)
        return result if isinstance(result, list) else []

    @staticmethod
    def get_region_code_for_location(lat: float, lon: float) -> str:
        """
        Get eBird region code for a location (simplified).

        This is a simple country-level mapping. For sub-regions,
        you'd need to use the eBird region API or manual mapping.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            eBird region code (e.g., 'NO' for Norway)
        """
        # Simplified mapping for Scandinavia
        # For Gaulosen (63.341°N, 10.215°E) -> Norway -> 'NO'
        # Could be extended with more precise region detection

        if 58 <= lat <= 71 and 4 <= lon <= 31:
            return 'NO'  # Norway
        elif 55 <= lat <= 69 and 11 <= lon <= 24:
            return 'SE'  # Sweden
        elif 54 <= lat <= 58 and 8 <= lon <= 15:
            return 'DK'  # Denmark
        else:
            # Default to world
            return 'world'

    def get_species_frequency(
        self,
        species_common_name: str,
        region_code: str,
        month: int
    ) -> Optional[float]:
        """
        Get species frequency in a region for a specific month.

        Note: This requires the eBird Status and Trends data product,
        which is not directly available via the API. This is a placeholder
        that uses recent observations as a proxy.

        Args:
            species_common_name: Common name
            region_code: eBird region code
            month: Month number (1-12)

        Returns:
            Frequency estimate (0-1) or None if no data
        """
        # This is a simplified proxy using recent observations
        # In production, you'd want to use the Status and Trends data
        print(f"Note: Using recent observations as proxy for {species_common_name} frequency")
        return None  # Placeholder for now
