"""
Habitat-based validation rules.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple


class HabitatValidator:
    """Validates species detections based on habitat requirements."""

    def __init__(self, species_db_path: Optional[str] = None):
        """
        Initialize habitat validator.

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

    def validate(
        self,
        species_name: str,
        habitat_type: str,
        min_threshold: float = 0.3
    ) -> Tuple[bool, Optional[str], float]:
        """
        Validate if species is suitable for habitat.

        Args:
            species_name: Common name of species
            habitat_type: Habitat type (wetland, forest, oceanic, etc.)
            min_threshold: Minimum habitat suitability score (0-1)

        Returns:
            Tuple of (is_valid, rejection_reason, habitat_score)
        """
        species_info = self.get_species_info(species_name)

        if species_info is None:
            # Species not in database - flag for review
            return (True, None, 0.5)

        habitat_prefs = species_info.get('habitat_preferences', {})
        habitat_score = habitat_prefs.get(habitat_type, 0.0)

        # Check for explicit oceanic species inland
        if habitat_type != 'oceanic' and habitat_prefs.get('oceanic', 0.0) >= 0.95:
            # Strictly oceanic species detected inland
            other_habitats = {k: v for k, v in habitat_prefs.items() if k != 'oceanic'}
            max_other = max(other_habitats.values()) if other_habitats else 0.0

            if max_other < 0.1:
                return (
                    False,
                    f"Habitat mismatch: {species_name} is pelagic/oceanic species, "
                    f"detected in {habitat_type} habitat (score={habitat_score:.2f})",
                    habitat_score
                )

        # Check general habitat suitability
        if habitat_score < min_threshold:
            # Get best habitat for this species
            best_habitat = max(habitat_prefs.items(), key=lambda x: x[1])

            return (
                False,
                f"Habitat mismatch: {species_name} prefers {best_habitat[0]} "
                f"(score={best_habitat[1]:.2f}), detected in {habitat_type} "
                f"(score={habitat_score:.2f})",
                habitat_score
            )

        return (True, None, habitat_score)

    def get_habitat_score(self, species_name: str, habitat_type: str) -> float:
        """
        Get habitat suitability score for a species.

        Args:
            species_name: Common name of species
            habitat_type: Habitat type

        Returns:
            Habitat score (0-1) or 0.5 if species unknown
        """
        species_info = self.get_species_info(species_name)

        if species_info is None:
            return 0.5  # Unknown species - neutral score

        habitat_prefs = species_info.get('habitat_preferences', {})
        return habitat_prefs.get(habitat_type, 0.5)

    def check_native_region(
        self,
        species_name: str,
        region: str = "Europe"
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if species is native to a region.

        Args:
            species_name: Common name of species
            region: Region name (Europe, Asia, etc.)

        Returns:
            Tuple of (is_native, rejection_reason)
        """
        species_info = self.get_species_info(species_name)

        if species_info is None:
            return (True, None)  # Unknown - don't reject

        native_region = species_info.get('native_region')

        if native_region and native_region != region:
            return (
                False,
                f"Non-native species: {species_name} is native to {native_region}, "
                f"not {region} (likely escaped bird)"
            )

        return (True, None)

    def get_preferred_habitats(self, species_name: str, threshold: float = 0.6) -> list:
        """
        Get list of preferred habitats for a species.

        Args:
            species_name: Common name of species
            threshold: Minimum score to be considered "preferred"

        Returns:
            List of habitat types where score >= threshold
        """
        species_info = self.get_species_info(species_name)

        if species_info is None:
            return []

        habitat_prefs = species_info.get('habitat_preferences', {})
        return [
            habitat for habitat, score in habitat_prefs.items()
            if score >= threshold
        ]
