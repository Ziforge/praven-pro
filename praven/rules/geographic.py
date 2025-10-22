"""
Geographic validation rules using eBird and GBIF APIs.
"""

from typing import Dict, Optional, Tuple
from ..api import eBirdClient, GBIFClient
from ..config import ValidationConfig


class GeographicValidator:
    """Validates species detections based on geographic occurrence data."""

    def __init__(
        self,
        ebird_client: Optional[eBirdClient] = None,
        gbif_client: Optional[GBIFClient] = None,
        config: Optional[ValidationConfig] = None
    ):
        """
        Initialize geographic validator.

        Args:
            ebird_client: eBird API client (optional, will create if needed)
            gbif_client: GBIF API client (optional, will create if needed)
            config: Validation configuration
        """
        self.ebird = ebird_client
        self.gbif = gbif_client or GBIFClient()
        self.config = config

    def validate_with_ebird(
        self,
        species_name: str,
        lat: float,
        lon: float,
        date: str,
        radius_km: float = 50
    ) -> Tuple[bool, Optional[str], Dict]:
        """
        Validate species occurrence using eBird data.

        Args:
            species_name: Common name of species
            lat: Latitude
            lon: Longitude
            date: Date in YYYY-MM-DD format
            radius_km: Search radius in kilometers

        Returns:
            Tuple of (is_expected, warning, metadata)
        """
        if self.ebird is None:
            # No eBird client - skip validation
            return (True, "eBird validation skipped (no API key)", {})

        try:
            occurrence = self.ebird.check_species_occurrence(
                species_common_name=species_name,
                lat=lat,
                lon=lon,
                date=date,
                radius_km=radius_km
            )

            metadata = {
                'ebird_expected': occurrence['expected'],
                'ebird_recent_count': occurrence['recent_obs_count'],
                'ebird_frequency': occurrence['frequency'],
                'ebird_last_seen': occurrence['last_seen_date']
            }

            if not occurrence['expected']:
                # Species not recently observed
                warning = (
                    f"eBird: {species_name} not observed in {radius_km}km radius "
                    f"in recent 30 days (location: {lat:.3f}, {lon:.3f})"
                )
                return (False, warning, metadata)

            return (True, None, metadata)

        except Exception as e:
            return (True, f"eBird API error: {e}", {})

    def validate_with_gbif(
        self,
        scientific_name: str,
        lat: float,
        lon: float,
        date: str,
        radius_km: float = 50
    ) -> Tuple[bool, Optional[str], Dict]:
        """
        Validate species occurrence using GBIF data.

        Args:
            scientific_name: Scientific name of species
            lat: Latitude
            lon: Longitude
            date: Date in YYYY-MM-DD format
            radius_km: Search radius in kilometers

        Returns:
            Tuple of (is_present, warning, metadata)
        """
        try:
            from datetime import datetime

            # Get month from date
            dt = datetime.strptime(date, '%Y-%m-%d')
            month = dt.month

            # Check GBIF occurrences
            occurrence = self.gbif.check_species_in_area(
                scientific_name=scientific_name,
                lat=lat,
                lon=lon,
                radius_km=radius_km,
                months=[month],
                years_back=10
            )

            metadata = {
                'gbif_present': occurrence['present'],
                'gbif_occurrence_count': occurrence['occurrence_count'],
                'gbif_closest_km': occurrence['closest_distance_km'],
                'gbif_months': occurrence['months_recorded']
            }

            if not occurrence['present']:
                # No GBIF occurrences found
                warning = (
                    f"GBIF: {scientific_name} has no recorded occurrences in "
                    f"{radius_km}km radius for month {month} (last 10 years)"
                )
                # Don't reject based on GBIF alone - just warn
                return (True, warning, metadata)

            return (True, None, metadata)

        except Exception as e:
            return (True, f"GBIF API error: {e}", {})

    def validate(
        self,
        species_name: str,
        scientific_name: Optional[str],
        lat: float,
        lon: float,
        date: str,
        radius_km: float = 50,
        require_both: bool = False
    ) -> Tuple[bool, Optional[str], Dict]:
        """
        Validate species using both eBird and GBIF.

        Args:
            species_name: Common name
            scientific_name: Scientific name (optional for eBird)
            lat: Latitude
            lon: Longitude
            date: Date in YYYY-MM-DD format
            radius_km: Search radius
            require_both: If True, require both APIs to confirm

        Returns:
            Tuple of (is_valid, warning, combined_metadata)
        """
        warnings = []
        metadata = {}

        # Try eBird
        ebird_valid, ebird_warn, ebird_meta = self.validate_with_ebird(
            species_name, lat, lon, date, radius_km
        )
        metadata.update(ebird_meta)
        if ebird_warn:
            warnings.append(ebird_warn)

        # Try GBIF
        gbif_valid = True
        if scientific_name:
            gbif_valid, gbif_warn, gbif_meta = self.validate_with_gbif(
                scientific_name, lat, lon, date, radius_km
            )
            metadata.update(gbif_meta)
            if gbif_warn:
                warnings.append(gbif_warn)

        # Combine results
        if require_both:
            is_valid = ebird_valid and gbif_valid
        else:
            # Accept if either confirms (more lenient)
            is_valid = ebird_valid or gbif_valid

        warning = "; ".join(warnings) if warnings else None

        return (is_valid, warning, metadata)

    def get_occurrence_confidence(self, metadata: Dict) -> float:
        """
        Calculate confidence score from occurrence metadata.

        Args:
            metadata: Metadata from validate()

        Returns:
            Confidence score (0-1)
        """
        score = 0.5  # Baseline

        # eBird contribution
        if metadata.get('ebird_expected'):
            score += 0.3

            freq = metadata.get('ebird_frequency')
            if freq is not None:
                score += 0.1 * freq  # Up to 0.1 bonus

        # GBIF contribution
        if metadata.get('gbif_present'):
            score += 0.2

            count = metadata.get('gbif_occurrence_count', 0)
            if count > 10:
                score += 0.1
            elif count > 5:
                score += 0.05

        # Distance penalty
        distance = metadata.get('gbif_closest_km')
        if distance is not None:
            if distance < 10:
                score += 0.05
            elif distance > 40:
                score -= 0.1

        return min(max(score, 0.0), 1.0)
