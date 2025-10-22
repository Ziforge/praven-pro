"""
Taxonomic-based validation using family/order-level biological rules.

This allows validation of ANY bird species using family-level rules,
covering 6000+ species without manual database entries.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple, List


class TaxonomicValidator:
    """Validate species using taxonomic family/order rules."""

    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialize taxonomic validator.

        Args:
            rules_path: Path to taxonomic rules JSON
        """
        if rules_path is None:
            default_path = Path(__file__).parent.parent / "data" / "taxonomic_rules.json"
            rules_path = str(default_path)

        with open(rules_path, 'r') as f:
            rules_data = json.load(f)

        self.family_rules = rules_data['family_rules']
        self.order_rules = rules_data.get('order_rules', {})
        self.exceptions = rules_data.get('exceptions', {})

    def infer_family(self, common_name: str) -> Optional[str]:
        """
        Infer bird family from common name.

        Args:
            common_name: Common name (e.g., "Lesser Spotted Woodpecker")

        Returns:
            Family name (e.g., "Picidae") or None
        """
        # Check each family's common name patterns
        for family, rules in self.family_rules.items():
            common_patterns = rules.get('common_names', [])

            for pattern in common_patterns:
                if pattern.lower() in common_name.lower():
                    return family

        return None

    def get_family_rules(self, family: str) -> Optional[Dict]:
        """Get rules for a bird family."""
        return self.family_rules.get(family)

    def validate_temporal(
        self,
        common_name: str,
        hour: int
    ) -> Tuple[bool, Optional[str], str]:
        """
        Validate time-of-day using taxonomic rules.

        Args:
            common_name: Common name
            hour: Hour (0-23)

        Returns:
            (is_valid, rejection_reason, time_period)
        """
        # Check for species-specific exception
        if common_name in self.exceptions:
            rules = self.exceptions[common_name]
        else:
            # Infer family and get rules
            family = self.infer_family(common_name)

            if family is None:
                # Unknown family - can't validate
                return (True, None, "unknown")

            rules = self.get_family_rules(family)

            if rules is None:
                return (True, None, "unknown")

        # Determine time period
        if 0 <= hour < 6:
            period = "night"
        elif 6 <= hour < 9:
            period = "dawn"
        elif 9 <= hour < 17:
            period = "day"
        elif 17 <= hour < 21:
            period = "dusk"
        else:
            period = "night"

        # Get activity patterns
        is_diurnal = rules.get('diurnal', True)
        is_crepuscular = rules.get('crepuscular', False)
        is_nocturnal = rules.get('nocturnal', False)

        # Validate
        if period == "night":
            if not is_nocturnal and not is_crepuscular:
                # Strictly diurnal species at night
                if is_diurnal and not is_crepuscular:
                    family_note = rules.get('notes', '')
                    return (
                        False,
                        f"Temporal impossibility: {common_name} is diurnal (family rule), "
                        f"detected at {hour:02d}:00 (night). {family_note}",
                        period
                    )

        if period == "day":
            if not is_diurnal and not is_crepuscular:
                # Strictly nocturnal species during day
                if is_nocturnal:
                    return (
                        False,
                        f"Temporal implausibility: {common_name} is nocturnal (family rule), "
                        f"detected at {hour:02d}:00 (day)",
                        period
                    )

        return (True, None, period)

    def validate_habitat(
        self,
        common_name: str,
        habitat_type: str,
        min_threshold: float = 0.3
    ) -> Tuple[bool, Optional[str], float]:
        """
        Validate habitat using taxonomic rules.

        Args:
            common_name: Common name
            habitat_type: Habitat (wetland, forest, oceanic, etc.)
            min_threshold: Minimum suitability score

        Returns:
            (is_valid, rejection_reason, habitat_score)
        """
        # Check for species exception
        if common_name in self.exceptions:
            rules = self.exceptions[common_name]
        else:
            # Infer family
            family = self.infer_family(common_name)

            if family is None:
                # Unknown - assume valid
                return (True, None, 0.5)

            rules = self.get_family_rules(family)

            if rules is None:
                return (True, None, 0.5)

        # Get habitat preferences
        habitat_prefs = rules.get('habitat_preferences', {})

        if not habitat_prefs:
            # No habitat data - assume valid
            return (True, None, 0.5)

        habitat_score = habitat_prefs.get(habitat_type, 0.5)

        # Check for oceanic species inland
        if habitat_type != 'oceanic' and habitat_prefs.get('oceanic', 0.0) >= 0.95:
            # Strictly oceanic species detected inland
            other_habitats = {k: v for k, v in habitat_prefs.items() if k != 'oceanic'}
            max_other = max(other_habitats.values()) if other_habitats else 0.0

            if max_other < 0.1:
                family = self.infer_family(common_name)
                family_note = rules.get('notes', '')

                return (
                    False,
                    f"Habitat mismatch: {common_name} is pelagic/oceanic (family: {family}), "
                    f"detected in {habitat_type}. {family_note}",
                    habitat_score
                )

        # Check general habitat suitability
        if habitat_score < min_threshold:
            family = self.infer_family(common_name)
            best_habitat = max(habitat_prefs.items(), key=lambda x: x[1])

            return (
                False,
                f"Habitat mismatch: {common_name} (family: {family}) prefers {best_habitat[0]} "
                f"(score={best_habitat[1]:.2f}), detected in {habitat_type} (score={habitat_score:.2f})",
                habitat_score
            )

        return (True, None, habitat_score)

    def get_family_info(self, common_name: str) -> Dict:
        """
        Get all family information for a species.

        Args:
            common_name: Common name

        Returns:
            Dictionary with family rules
        """
        family = self.infer_family(common_name)

        if family is None:
            return {
                'family': 'Unknown',
                'common_names': [],
                'diurnal': True,
                'crepuscular': False,
                'nocturnal': False,
                'habitat_preferences': {},
                'notes': 'Family unknown - validation limited'
            }

        rules = self.get_family_rules(family)

        return {
            'family': family,
            **rules
        }

    def list_families(self) -> List[str]:
        """Get list of all known families."""
        return list(self.family_rules.keys())

    def get_coverage_stats(self) -> Dict:
        """Get coverage statistics."""
        return {
            'families': len(self.family_rules),
            'orders': len(self.order_rules),
            'exceptions': len(self.exceptions),
            'estimated_species_coverage': len(self.family_rules) * 100  # Rough estimate
        }
