"""
Habitat detection client for automatic habitat type identification from GPS coordinates.

Uses OpenStreetMap Overpass API to query land use and natural features,
then determines primary habitat and hybrid habitat percentages.
"""

import requests
from typing import Dict, Optional, List, Tuple
import json
from pathlib import Path
from collections import Counter


class HabitatClient:
    """Client for detecting habitat type from GPS coordinates."""

    # Mapping from OSM tags to Praven habitat types
    HABITAT_MAPPING = {
        # Water/Wetland features
        'water': 'wetland',
        'wetland': 'wetland',
        'marsh': 'wetland',
        'swamp': 'wetland',
        'bog': 'wetland',
        'reedbed': 'wetland',
        'tidalflat': 'wetland',
        'saltmarsh': 'wetland',
        'reservoir': 'wetland',
        'lake': 'wetland',
        'pond': 'wetland',
        'river': 'wetland',
        'stream': 'wetland',

        # Forest features
        'forest': 'forest',
        'wood': 'forest',
        'tree_row': 'forest',
        'scrub': 'forest',

        # Grassland features
        'grassland': 'grassland',
        'meadow': 'grassland',
        'heath': 'grassland',
        'grass': 'grassland',
        'farmland': 'grassland',
        'farmyard': 'grassland',

        # Urban features
        'residential': 'urban',
        'commercial': 'urban',
        'industrial': 'urban',
        'retail': 'urban',
        'construction': 'urban',

        # Agricultural features
        'farm': 'agricultural',
        'orchard': 'agricultural',
        'vineyard': 'agricultural',
        'allotments': 'agricultural',
        'plant_nursery': 'agricultural',

        # Oceanic/coastal features
        'coastline': 'oceanic',
        'beach': 'oceanic',
        'sand': 'oceanic',
        'bay': 'oceanic',
    }

    def __init__(self, cache_dir: str = "cache/habitat"):
        """
        Initialize habitat client.

        Args:
            cache_dir: Directory for caching habitat data
        """
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_habitat(
        self,
        lat: float,
        lon: float,
        radius_m: int = 1000
    ) -> Dict[str, any]:
        """
        Detect habitat type from GPS coordinates.

        Args:
            lat: Latitude
            lon: Longitude
            radius_m: Search radius in meters (default: 500m)

        Returns:
            Dictionary with:
            {
                'primary': str (main habitat type),
                'confidence': float (0.0-1.0),
                'hybrid': dict (other habitats with percentages),
                'raw_features': list (OSM features found)
            }
        """
        # Check cache first
        cache_key = f"{lat:.4f}_{lon:.4f}_{radius_m}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        # Query OSM for land use features
        features = self._query_osm_features(lat, lon, radius_m)

        # Analyze features to determine habitat
        habitat_data = self._analyze_features(features)

        # Cache the result
        self._save_to_cache(cache_key, habitat_data)

        return habitat_data

    def _query_osm_features(
        self,
        lat: float,
        lon: float,
        radius_m: int
    ) -> List[Dict]:
        """Query OpenStreetMap Overpass API for land use features."""
        # Overpass QL query for land use and natural features
        query = f"""
        [out:json][timeout:25];
        (
          // Natural features
          way["natural"](around:{radius_m},{lat},{lon});
          relation["natural"](around:{radius_m},{lat},{lon});

          // Land use features
          way["landuse"](around:{radius_m},{lat},{lon});
          relation["landuse"](around:{radius_m},{lat},{lon});

          // Water features
          way["water"](around:{radius_m},{lat},{lon});
          way["waterway"](around:{radius_m},{lat},{lon});

          // Wetland features
          way["wetland"](around:{radius_m},{lat},{lon});
        );
        out body;
        """

        try:
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            return data.get('elements', [])

        except Exception as e:
            print(f"Warning: Could not fetch OSM data: {e}")
            return []

    def _analyze_features(self, features: List[Dict]) -> Dict[str, any]:
        """Analyze OSM features to determine habitat type and hybrids."""
        if not features:
            return self._get_default_habitat()

        # Count habitat types from features
        habitat_counts = Counter()

        for feature in features:
            tags = feature.get('tags', {})

            # Check natural tag
            if 'natural' in tags:
                habitat = self.HABITAT_MAPPING.get(tags['natural'])
                if habitat:
                    habitat_counts[habitat] += 1

            # Check landuse tag
            if 'landuse' in tags:
                habitat = self.HABITAT_MAPPING.get(tags['landuse'])
                if habitat:
                    habitat_counts[habitat] += 1

            # Check water tag
            if 'water' in tags:
                habitat_counts['wetland'] += 1

            # Check wetland tag
            if 'wetland' in tags:
                habitat_counts['wetland'] += 1

            # Check waterway tag
            if 'waterway' in tags:
                habitat_counts['wetland'] += 1

        if not habitat_counts:
            return self._get_default_habitat()

        # Calculate percentages
        total = sum(habitat_counts.values())
        percentages = {
            habitat: count / total
            for habitat, count in habitat_counts.items()
        }

        # Get primary habitat (highest percentage)
        primary = max(percentages.items(), key=lambda x: x[1])
        primary_habitat = primary[0]
        primary_confidence = primary[1]

        # Get hybrid habitats (>10% but not primary)
        hybrid = {
            habitat: pct
            for habitat, pct in percentages.items()
            if habitat != primary_habitat and pct >= 0.1
        }

        return {
            'primary': primary_habitat,
            'confidence': primary_confidence,
            'hybrid': hybrid,
            'raw_features': [
                {
                    'type': f.get('type'),
                    'tags': f.get('tags', {})
                }
                for f in features[:10]  # Limit to first 10 for brevity
            ]
        }

    def _get_default_habitat(self) -> Dict[str, any]:
        """Return default habitat when detection fails."""
        return {
            'primary': 'unknown',
            'confidence': 0.0,
            'hybrid': {},
            'raw_features': []
        }

    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get habitat data from cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        return None

    def _save_to_cache(self, cache_key: str, data: Dict) -> None:
        """Save habitat data to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not cache habitat data: {e}")

    def format_habitat_description(self, habitat_data: Dict) -> str:
        """
        Format habitat data into human-readable description.

        Args:
            habitat_data: Habitat data from get_habitat()

        Returns:
            Formatted string like "wetland (70%), forest (30%)"
        """
        if habitat_data['primary'] == 'unknown':
            return "unknown"

        primary = habitat_data['primary']
        confidence = habitat_data['confidence']

        if not habitat_data['hybrid']:
            # Pure habitat
            return f"{primary} ({confidence*100:.0f}%)"

        # Hybrid habitat
        parts = [f"{primary} ({confidence*100:.0f}%)"]
        for habitat, pct in sorted(
            habitat_data['hybrid'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            parts.append(f"{habitat} ({pct*100:.0f}%)")

        return ", ".join(parts)


def get_habitat_from_coords(
    lat: float,
    lon: float,
    radius_m: int = 500
) -> Tuple[str, Dict]:
    """
    Convenience function to get habitat from coordinates.

    Args:
        lat: Latitude
        lon: Longitude
        radius_m: Search radius in meters

    Returns:
        Tuple of (primary_habitat_type, full_habitat_data)
    """
    client = HabitatClient()
    habitat_data = client.get_habitat(lat, lon, radius_m)
    return habitat_data['primary'], habitat_data


if __name__ == "__main__":
    # Demo
    client = HabitatClient()

    # Test with Gaulossen coordinates (wetland)
    print("Testing Gaulossen Nature Reserve (63.341, 10.215):")
    habitat = client.get_habitat(63.341, 10.215, radius_m=500)

    print(f"\nPrimary habitat: {habitat['primary']}")
    print(f"Confidence: {habitat['confidence']*100:.0f}%")

    if habitat['hybrid']:
        print("\nHybrid habitats:")
        for h, pct in habitat['hybrid'].items():
            print(f"  {h}: {pct*100:.0f}%")

    print(f"\nFormatted: {client.format_habitat_description(habitat)}")

    print(f"\nRaw OSM features found: {len(habitat['raw_features'])}")
    if habitat['raw_features']:
        print("Sample features:")
        for feature in habitat['raw_features'][:3]:
            print(f"  {feature['type']}: {feature['tags']}")
