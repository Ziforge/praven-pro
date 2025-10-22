"""
GBIF API client for species occurrence and range data.

API Documentation: https://techdocs.gbif.org/en/openapi/
"""

import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from .cache import APICache


class GBIFClient:
    """Client for GBIF API."""

    BASE_URL = "https://api.gbif.org/v1"

    def __init__(self, cache_dir: str = "cache", cache_ttl_hours: int = 24):
        """
        Initialize GBIF API client.

        Args:
            cache_dir: Directory for caching API responses
            cache_ttl_hours: Cache time-to-live in hours

        Note: GBIF API does not require authentication
        """
        self.cache = APICache(cache_dir, cache_ttl_hours)
        self.session = requests.Session()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with error handling."""
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"GBIF API error: {e}")
            return {}

    def search_species(self, name: str, rank: str = "SPECIES") -> List[Dict]:
        """
        Search for species by name.

        Args:
            name: Scientific or common name
            rank: Taxonomic rank (SPECIES, GENUS, etc.)

        Returns:
            List of matching species
        """
        cache_key = self.cache._get_cache_key('species_search', name, rank)

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        params = {
            'q': name,
            'rank': rank,
            'limit': 10
        }

        result = self._make_request('species/search', params)
        results = result.get('results', [])

        self.cache.set(cache_key, results)
        return results

    def get_species_key(self, scientific_name: str) -> Optional[int]:
        """
        Get GBIF species key (taxon ID) from scientific name.

        Args:
            scientific_name: Scientific name (e.g., "Gallinago media")

        Returns:
            GBIF species key or None
        """
        results = self.search_species(scientific_name)

        if results:
            # Return first exact match
            for result in results:
                if result.get('scientificName', '').lower() == scientific_name.lower():
                    return result.get('key')

            # Fallback to first result
            return results[0].get('key')

        return None

    def get_occurrences(
        self,
        species_key: Optional[int] = None,
        scientific_name: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_km: Optional[float] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        limit: int = 300
    ) -> List[Dict]:
        """
        Get occurrence records for a species.

        Args:
            species_key: GBIF species key
            scientific_name: Scientific name (alternative to species_key)
            lat: Latitude for geographic filtering
            lon: Longitude for geographic filtering
            radius_km: Search radius in kilometers
            year: Year filter
            month: Month filter (1-12)
            limit: Maximum number of records

        Returns:
            List of occurrence records
        """
        # Get species key if not provided
        if species_key is None and scientific_name:
            species_key = self.get_species_key(scientific_name)

        if species_key is None:
            return []

        cache_key = self.cache._get_cache_key(
            'occurrences', species_key, lat, lon, radius_km, year, month, limit
        )

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        params = {
            'speciesKey': species_key,
            'limit': min(limit, 300),  # GBIF max is 300 per request
            'hasCoordinate': 'true'
        }

        if year:
            params['year'] = year

        if month:
            params['month'] = month

        # Geographic filter
        if lat is not None and lon is not None:
            # GBIF uses decimal degrees, we need to convert radius to degrees
            # Roughly: 1 degree latitude = 111 km
            degree_radius = (radius_km or 50) / 111.0

            params['decimalLatitude'] = f"{lat-degree_radius},{lat+degree_radius}"
            params['decimalLongitude'] = f"{lon-degree_radius},{lon+degree_radius}"

        result = self._make_request('occurrence/search', params)
        occurrences = result.get('results', [])

        self.cache.set(cache_key, occurrences)
        return occurrences

    def check_species_in_area(
        self,
        scientific_name: str,
        lat: float,
        lon: float,
        radius_km: float = 50,
        months: Optional[List[int]] = None,
        years_back: int = 10
    ) -> Dict[str, any]:
        """
        Check if species has been recorded in an area.

        Args:
            scientific_name: Scientific name
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers
            months: Optional list of months to filter (e.g., [10, 11] for Oct-Nov)
            years_back: How many years back to search

        Returns:
            Dictionary with:
            {
                'present': bool,
                'occurrence_count': int,
                'years_recorded': list,
                'months_recorded': list,
                'closest_distance_km': float or None
            }
        """
        current_year = datetime.now().year
        all_occurrences = []

        # Search recent years
        for year_offset in range(years_back):
            year = current_year - year_offset

            if months:
                # Search specific months
                for month in months:
                    occs = self.get_occurrences(
                        scientific_name=scientific_name,
                        lat=lat,
                        lon=lon,
                        radius_km=radius_km,
                        year=year,
                        month=month,
                        limit=100
                    )
                    all_occurrences.extend(occs)
            else:
                # Search whole year
                occs = self.get_occurrences(
                    scientific_name=scientific_name,
                    lat=lat,
                    lon=lon,
                    radius_km=radius_km,
                    year=year,
                    limit=100
                )
                all_occurrences.extend(occs)

        # Analyze occurrences
        years_recorded = sorted(set(occ.get('year') for occ in all_occurrences if occ.get('year')))
        months_recorded = sorted(set(occ.get('month') for occ in all_occurrences if occ.get('month')))

        # Calculate distances
        closest_distance = None
        if all_occurrences:
            distances = []
            for occ in all_occurrences:
                occ_lat = occ.get('decimalLatitude')
                occ_lon = occ.get('decimalLongitude')

                if occ_lat is not None and occ_lon is not None:
                    # Haversine distance approximation
                    distance_km = self._haversine_distance(lat, lon, occ_lat, occ_lon)
                    distances.append(distance_km)

            if distances:
                closest_distance = min(distances)

        return {
            'present': len(all_occurrences) > 0,
            'occurrence_count': len(all_occurrences),
            'years_recorded': years_recorded,
            'months_recorded': months_recorded,
            'closest_distance_km': closest_distance
        }

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth radius in kilometers

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def get_species_habitat_info(self, scientific_name: str) -> Optional[Dict]:
        """
        Get habitat information from GBIF species page.

        Note: GBIF doesn't provide structured habitat data via API.
        This is a placeholder for future implementation using
        species page scraping or external databases.

        Args:
            scientific_name: Scientific name

        Returns:
            Habitat information dictionary or None
        """
        # Placeholder - would need to implement web scraping or
        # integrate with other databases like EOL, Wikipedia, etc.
        return None
