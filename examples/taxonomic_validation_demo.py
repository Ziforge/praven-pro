#!/usr/bin/env python3
"""
Demonstrate taxonomic validation covering 6000+ species with family rules.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from praven.rules.taxonomic import TaxonomicValidator


def main():
    """Demo taxonomic validation."""

    print("=" * 80)
    print("Praven Pro - Taxonomic Validation (6000+ Species Coverage)")
    print("=" * 80)

    validator = TaxonomicValidator()

    # Get stats
    stats = validator.get_coverage_stats()
    print(f"\nCoverage Statistics:")
    print(f"  Families with rules: {stats['families']}")
    print(f"  Orders with rules: {stats['orders']}")
    print(f"  Species exceptions: {stats['exceptions']}")
    print(f"  Estimated species coverage: {stats['estimated_species_coverage']:,}+ species")

    print(f"\nKnown families:")
    for family in sorted(validator.list_families())[:15]:
        print(f"  - {family}")
    print(f"  ... and {len(validator.list_families()) - 15} more")

    # Test cases - species NOT in manual database
    print(f"\n{'=' * 80}")
    print("Test Cases - Validating Species NOT in Manual Database")
    print("=" * 80)

    test_cases = [
        # Woodpeckers (should catch nocturnal detections)
        {
            "species": "Downy Woodpecker",
            "hour": 23,
            "habitat": "wetland",
            "expected": "REJECT (nocturnal woodpecker)"
        },
        {
            "species": "Pileated Woodpecker",
            "hour": 2,
            "habitat": "forest",
            "expected": "REJECT (nocturnal woodpecker)"
        },
        # Owls (should allow nocturnal)
        {
            "species": "Great Gray Owl",
            "hour": 23,
            "habitat": "forest",
            "expected": "ACCEPT (nocturnal owl)"
        },
        {
            "species": "Snowy Owl",
            "hour": 3,
            "habitat": "grassland",
            "expected": "ACCEPT (nocturnal owl)"
        },
        # Oceanic birds (should reject inland)
        {
            "species": "Leach's Storm-Petrel",
            "hour": 12,
            "habitat": "wetland",
            "expected": "REJECT (oceanic inland)"
        },
        {
            "species": "Wilson's Storm-Petrel",
            "hour": 15,
            "habitat": "forest",
            "expected": "REJECT (oceanic inland)"
        },
        {
            "species": "Black-browed Albatross",
            "hour": 10,
            "habitat": "wetland",
            "expected": "REJECT (oceanic inland)"
        },
        # Waterfowl (should allow wetland)
        {
            "species": "Wood Duck",
            "hour": 14,
            "habitat": "wetland",
            "expected": "ACCEPT (wetland duck)"
        },
        {
            "species": "Tufted Duck",
            "hour": 22,
            "habitat": "wetland",
            "expected": "ACCEPT (nocturnal duck)"
        },
        # Forest specialists (should reject in wetland)
        {
            "species": "Black-backed Woodpecker",
            "hour": 10,
            "habitat": "wetland",
            "expected": "REJECT (forest species in wetland)"
        },
        # Finches
        {
            "species": "Pine Grosbeak",
            "hour": 8,
            "habitat": "forest",
            "expected": "ACCEPT (diurnal finch in forest)"
        },
        # Rails (nocturnal/crepuscular)
        {
            "species": "Sora",
            "hour": 22,
            "habitat": "wetland",
            "expected": "ACCEPT (nocturnal rail)"
        },
        {
            "species": "Virginia Rail",
            "hour": 1,
            "habitat": "wetland",
            "expected": "ACCEPT (nocturnal rail)"
        },
        # Nightjars (nocturnal)
        {
            "species": "Common Nighthawk",
            "hour": 23,
            "habitat": "grassland",
            "expected": "ACCEPT (nocturnal)"
        },
        {
            "species": "European Nightjar",
            "hour": 2,
            "habitat": "forest",
            "expected": "ACCEPT (nocturnal)"
        }
    ]

    correct = 0
    total = len(test_cases)

    for i, test in enumerate(test_cases, 1):
        # Temporal validation
        temporal_valid, temporal_reason, period = validator.validate_temporal(
            test["species"],
            test["hour"]
        )

        # Habitat validation
        habitat_valid, habitat_reason, score = validator.validate_habitat(
            test["species"],
            test["habitat"]
        )

        # Overall result
        is_valid = temporal_valid and habitat_valid
        status = "ACCEPT" if is_valid else "REJECT"

        # Check if matches expected
        expected_status = test["expected"].split()[0]
        match = "✓" if status == expected_status else "✗"
        correct += 1 if status == expected_status else 0

        # Get family info
        family_info = validator.get_family_info(test["species"])
        family = family_info['family']

        print(f"\n[{i}] {match} {test['species']} (Family: {family})")
        print(f"    Time: {test['hour']:02d}:00 ({period}) | Habitat: {test['habitat']}")
        print(f"    Expected: {test['expected']}")
        print(f"    Got: {status}")

        if not is_valid:
            reason = temporal_reason or habitat_reason
            print(f"    Reason: {reason[:75]}...")

    print(f"\n{'=' * 80}")
    print(f"Accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
    print("=" * 80)

    if correct == total:
        print("\n✓ All tests passed! Taxonomic validation working correctly.")
        print(f"\nThis system can now validate 6000+ BirdNET species using {stats['families']} family rules!")
    else:
        print(f"\n✗ {total - correct} test(s) failed.")


if __name__ == "__main__":
    main()
