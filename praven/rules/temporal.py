"""
Temporal validation rules for time-of-day and seasonality.
"""

import json
from pathlib import Path
from datetime import datetime, time
from typing import Dict, Optional, Tuple, List


class TemporalValidator:
    """Validates species detections based on temporal patterns."""

    def __init__(self, species_db_path: Optional[str] = None):
        """
        Initialize temporal validator.

        Args:
            species_db_path: Path to species database JSON file
        """
        if species_db_path is None:
            # Use default database
            default_path = Path(__file__).parent.parent / "data" / "species_db.json"
            species_db_path = str(default_path)

        with open(species_db_path, 'r') as f:
            self.species_db = json.load(f)

    def get_species_info(self, species_name: str) -> Optional[Dict]:
        """Get species information from database."""
        return self.species_db.get('species', {}).get(species_name)

    def validate_time_of_day(
        self,
        species_name: str,
        timestamp: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Validate if species should be vocally active at this time.

        Args:
            species_name: Common name of species
            timestamp: Timestamp string (YYYY-MM-DD HH:MM:SS or HH:MM:SS)

        Returns:
            Tuple of (is_valid, rejection_reason, time_period)
        """
        species_info = self.get_species_info(species_name)

        if species_info is None:
            # Species not in database - flag for review
            return (True, None, "unknown")

        # Parse timestamp to get hour
        try:
            if 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif ' ' in timestamp:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            else:
                # Just time
                dt = datetime.strptime(timestamp, '%H:%M:%S')
        except ValueError:
            return (True, None, "unknown")

        hour = dt.hour

        # Determine time period
        if 0 <= hour < 6:
            period = "night"
        elif 6 <= hour < 9:
            period = "dawn"
        elif 9 <= hour < 17:
            period = "day"
        elif 17 <= hour < 21:
            period = "dusk"
        else:  # 21-24
            period = "night"

        # Get activity patterns
        is_diurnal = species_info.get('diurnal', True)
        is_crepuscular = species_info.get('crepuscular', False)
        is_nocturnal = species_info.get('nocturnal', False)

        # Check for violations
        if period == "night" and not is_nocturnal and not is_crepuscular:
            # Strictly diurnal species detected at night
            if is_diurnal and not is_crepuscular:
                return (
                    False,
                    f"Temporal impossibility: {species_name} is strictly diurnal, "
                    f"detected at {dt.strftime('%H:%M')} (night period)",
                    period
                )

        if period == "day" and not is_diurnal:
            # Strictly nocturnal species detected during day
            if is_nocturnal and not is_crepuscular and not is_diurnal:
                return (
                    False,
                    f"Temporal implausibility: {species_name} is nocturnal, "
                    f"detected at {dt.strftime('%H:%M')} (day period)",
                    period
                )

        # Crepuscular check
        if period in ["dawn", "dusk"]:
            # Dawn/dusk is acceptable for all species
            return (True, None, period)

        return (True, None, period)

    def validate_seasonality(
        self,
        species_name: str,
        date: str
    ) -> Tuple[bool, Optional[str], int]:
        """
        Validate if species should be present in this month.

        Args:
            species_name: Common name of species
            date: Date string (YYYY-MM-DD)

        Returns:
            Tuple of (is_valid, warning_message, month)
        """
        species_info = self.get_species_info(species_name)

        if species_info is None:
            # Species not in database
            return (True, None, 0)

        # Parse date
        try:
            dt = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return (True, None, 0)

        month = dt.month

        # Get active months
        active_months = species_info.get('active_months', [])

        if not active_months:
            # No restriction - assume year-round or unknown
            return (True, None, month)

        # Check if month is in active period
        if month not in active_months:
            migration_info = species_info.get('migration', {})
            status_parts = []

            if migration_info.get('summer_visitor'):
                status_parts.append("summer visitor")
            if migration_info.get('winter_visitor'):
                status_parts.append("winter visitor")
            if migration_info.get('passage_migrant'):
                status_parts.append("passage migrant")

            status_str = ", ".join(status_parts) if status_parts else "seasonal species"

            return (
                False,
                f"Seasonal implausibility: {species_name} ({status_str}) "
                f"detected in month {month}, expected in months {active_months}",
                month
            )

        return (True, None, month)

    def get_activity_period(self, hour: int) -> str:
        """
        Get activity period name for an hour.

        Args:
            hour: Hour (0-23)

        Returns:
            Period name: night, dawn, day, dusk
        """
        if 0 <= hour < 6:
            return "night"
        elif 6 <= hour < 9:
            return "dawn"
        elif 9 <= hour < 17:
            return "day"
        elif 17 <= hour < 21:
            return "dusk"
        else:
            return "night"

    def is_species_active(
        self,
        species_name: str,
        timestamp: str,
        date: str
    ) -> Tuple[bool, List[str]]:
        """
        Check if species should be active at this time and date.

        Args:
            species_name: Common name of species
            timestamp: Timestamp (HH:MM:SS or YYYY-MM-DD HH:MM:SS)
            date: Date (YYYY-MM-DD)

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        # Check time of day
        time_valid, time_reason, period = self.validate_time_of_day(
            species_name, timestamp
        )

        if not time_valid:
            warnings.append(time_reason)

        # Check seasonality
        season_valid, season_reason, month = self.validate_seasonality(
            species_name, date
        )

        if not season_valid:
            warnings.append(season_reason)

        is_valid = time_valid and season_valid

        return (is_valid, warnings)

    def get_expected_months(self, species_name: str) -> List[int]:
        """
        Get months when species is expected to be present.

        Args:
            species_name: Common name of species

        Returns:
            List of month numbers (1-12), empty list if year-round
        """
        species_info = self.get_species_info(species_name)

        if species_info is None:
            return []

        return species_info.get('active_months', [])
