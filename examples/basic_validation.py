#!/usr/bin/env python3
"""
Basic validation example for Praven Pro.

Demonstrates validating individual BirdNET detections.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from praven import BiologicalValidator, ValidationConfig


def main():
    """Run basic validation examples."""

    # Configure validator for Gaulossen Nature Reserve
    config = ValidationConfig(
        location=(63.341, 10.215),  # Gaulosen coordinates
        date="2025-10-13",
        habitat_type="wetland",
        weather_conditions={
            "rain": 0.8,
            "fog": 0.7,
            "temperature": 8.0
        },
        ebird_api_key=os.getenv('EBIRD_API_KEY'),  # Optional
        geographic_radius_km=50
    )

    validator = BiologicalValidator(config)

    print("=" * 70)
    print("Praven Pro - Biological Validation Demo")
    print("=" * 70)
    print(f"\nLocation: {config.location}")
    print(f"Date: {config.date}")
    print(f"Habitat: {config.habitat_type}")
    print(f"Weather: Rain={config.weather_conditions['rain']}, Fog={config.weather_conditions['fog']}")
    print()

    # Test cases from Gaulossen study
    test_cases = [
        {
            "species": "Great Snipe",
            "timestamp": "2025-10-13 20:00:00",
            "confidence": 0.85,
            "expected": "ACCEPT",
            "note": "Crepuscular species at dusk - should accept"
        },
        {
            "species": "Graylag Goose",
            "timestamp": "2025-10-13 14:00:00",
            "confidence": 0.92,
            "expected": "ACCEPT",
            "note": "Common wetland species - should accept"
        },
        {
            "species": "Lesser Spotted Woodpecker",
            "timestamp": "2025-10-13 23:45:00",
            "confidence": 0.78,
            "expected": "REJECT",
            "note": "Diurnal species at night - should REJECT"
        },
        {
            "species": "European Storm-Petrel",
            "timestamp": "2025-10-13 12:00:00",
            "confidence": 0.81,
            "expected": "REJECT",
            "note": "Oceanic species inland - should REJECT"
        },
        {
            "species": "Manx Shearwater",
            "timestamp": "2025-10-13 15:30:00",
            "confidence": 0.75,
            "expected": "REJECT",
            "note": "Pelagic species inland - should REJECT"
        },
        {
            "species": "Bar-headed Goose",
            "timestamp": "2025-10-13 10:00:00",
            "confidence": 0.82,
            "expected": "REJECT",
            "note": "Non-native to Europe - should REJECT"
        },
        {
            "species": "Western Capercaillie",
            "timestamp": "2025-10-13 08:00:00",
            "confidence": 0.79,
            "expected": "REJECT",
            "note": "Forest species in wetland - should REJECT"
        },
        {
            "species": "Mallard",
            "timestamp": "2025-10-13 23:00:00",
            "confidence": 0.88,
            "expected": "ACCEPT",
            "note": "Nocturnal feeding behavior - should accept"
        }
    ]

    # Run validation
    print("\nValidation Results:")
    print("-" * 70)

    correct = 0
    total = len(test_cases)

    for i, test in enumerate(test_cases, 1):
        result = validator.validate_detection(
            species=test["species"],
            timestamp=test["timestamp"],
            confidence=test["confidence"]
        )

        # Check if result matches expectation
        match = "✓" if result.status == test["expected"] else "✗"
        correct += 1 if result.status == test["expected"] else 0

        print(f"\n[{i}] {match} {test['species']}")
        print(f"    Time: {test['timestamp']}")
        print(f"    Expected: {test['expected']} | Got: {result.status}")
        print(f"    Score: {result.overall_score:.3f} (BirdNET: {test['confidence']:.2f})")

        if result.status == "REJECT":
            print(f"    Reason: {result.rejection_reason}")

        if result.review_notes:
            print(f"    Notes: {'; '.join(result.review_notes)}")

        print(f"    Test: {test['note']}")

    # Summary
    print("\n" + "=" * 70)
    print(f"Accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
    print("=" * 70)

    if correct == total:
        print("\n✓ All tests passed! Validation system working correctly.")
    else:
        print(f"\n✗ {total - correct} test(s) failed. Review validation logic.")


if __name__ == "__main__":
    main()
